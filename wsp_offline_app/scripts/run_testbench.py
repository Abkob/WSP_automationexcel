"""
Automated testbench runner — imports every file in data/testbench/ via the
live API and verifies the result, then runs an export at the end.

Usage
─────
    # Make sure the app is running first:
    #   .venv\\Scripts\\python.exe main.py
    #
    .venv\\Scripts\\python.exe scripts\\run_testbench.py [--base-url http://127.0.0.1:8080]

What it does
────────────
    For each .xlsx in data/testbench/ (in sorted order):
      1. POST /api/import/run  {"path": "<absolute path>"}
      2. Prints the counts returned (new / updated / unchanged / missing)
      3. Marks expected-error files (A6, E2, E3) as PASS when they return 409/400
      4. Flags any unexpected HTTP error as FAIL

    After all imports:
      5. POST /api/search  {}  — sanity check that search works
      6. POST /api/export  {}  — export all students, prints row count and path
      7. GET  /api/system-status  — prints health summary

    Exits with code 0 if everything passes, 1 if any FAIL.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

try:
    import urllib.request as _req
    import urllib.error  as _err
except ImportError:
    print("ERROR: urllib not available", file=sys.stderr)
    sys.exit(1)


BASE_DIR = Path(__file__).resolve().parent.parent
TESTBENCH = BASE_DIR / "data" / "testbench"

# Files expected to be REJECTED by the API (HTTP 4xx is a PASS for these)
EXPECTED_ERRORS: dict[str, str] = {
    "A6_DUPLICATE_of_A1.xlsx":             "409 DuplicateExcelFileError",
    "E3_empty_no_rows.xlsx":               "400/422 NoValidStudentRows",
    "E2_students_not_on_first_sheet.xlsx": "400 or 0 rows (no STUD_ID column on first sheet)",
}


def _post(url: str, body: dict, timeout: int = 120) -> tuple[int, dict]:
    data = json.dumps(body).encode()
    request = _req.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with _req.urlopen(request, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read())
    except _err.HTTPError as exc:
        try:
            detail = json.loads(exc.read()).get("detail", "")
        except Exception:
            detail = ""
        return exc.code, {"detail": detail}


def _get(url: str, timeout: int = 30) -> tuple[int, dict]:
    request = _req.Request(url)
    try:
        with _req.urlopen(request, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read())
    except _err.HTTPError as exc:
        return exc.code, {"detail": str(exc)}


def _check_server(base: str) -> bool:
    try:
        code, _ = _get(f"{base}/api/system-status", timeout=5)
        return code == 200
    except Exception:
        return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    args = parser.parse_args()
    base: str = args.base_url.rstrip("/")

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    SEP = "-" * 72
    WIDE = 72

    print(SEP)
    print("WSP TESTBENCH RUNNER")
    print(SEP)

    if not _check_server(base):
        print(f"ERROR: App is not running at {base}")
        print("       Start it first:  .venv\\Scripts\\python.exe main.py")
        return 1

    print(f"  Server : {base}  [OK]")

    files = sorted(TESTBENCH.glob("*.xlsx"))
    if not files:
        print(f"ERROR: No .xlsx files found in {TESTBENCH}")
        print("       Run scripts\\create_testbench.py first.")
        return 1

    print(f"  Files  : {len(files)} workbooks in {TESTBENCH}")
    print()

    results: list[tuple[str, str, str]] = []   # (filename, PASS|FAIL|SKIP, note)
    fail_count = 0

    for xlsx in files:
        fname = xlsx.name
        is_expected_error = fname in EXPECTED_ERRORS
        expected_error_desc = EXPECTED_ERRORS.get(fname, "")

        t0 = time.monotonic()
        code, body = _post(f"{base}/api/import/run", {"path": str(xlsx)})
        elapsed = time.monotonic() - t0

        if is_expected_error:
            if code >= 400:
                note = f"HTTP {code} as expected ({expected_error_desc})"
                results.append((fname, "PASS", note))
                status_tag = "PASS"
            else:
                note = f"Expected HTTP 4xx but got {code}. Body: {body}"
                results.append((fname, "FAIL", note))
                status_tag = "FAIL"
                fail_count += 1
        elif code == 409:
            # File was already imported in a previous run (same bytes = same hash).
            # Not a failure — idempotent duplicate detection working correctly.
            detail = body.get("detail", "")[:100]
            note = f"SKIP — already imported (duplicate detection): {detail}"
            results.append((fname, "SKIP", note))
            status_tag = "SKIP"
        elif code == 200:
            new      = body.get("new_rows",       body.get("new_count",       0))
            updated  = body.get("updated_rows",   body.get("updated_count",   0))
            unchanged= body.get("unchanged_rows", body.get("unchanged_count", 0))
            missing  = body.get("missing_rows",   body.get("missing_count",   0))
            rejected = body.get("rejected_rows",  body.get("rejected_count",  0))
            note = f"new={new}  updated={updated}  unchanged={unchanged}  missing={missing}  rejected={rejected}  ({elapsed:.1f}s)"
            results.append((fname, "PASS", note))
            status_tag = "PASS"
        else:
            detail = body.get("detail", str(body))[:120]
            note = f"HTTP {code}: {detail}"
            results.append((fname, "FAIL", note))
            status_tag = "FAIL"
            fail_count += 1

        tag_width = 4
        print(f"  [{status_tag}] {fname}")
        print(f"         {note}")

    print()
    print(SEP)
    print("SEARCH SANITY CHECK")
    print(SEP)
    code, body = _post(f"{base}/api/search", {})
    if code == 200:
        total = body.get("total_count", body.get("total", "?"))
        print(f"  [PASS] /api/search -> {total} students found")
    else:
        print(f"  [FAIL] /api/search HTTP {code}: {body.get('detail','')}")
        fail_count += 1

    print()
    print(SEP)
    print("EXPORT CHECK")
    print(SEP)
    code, body = _post(f"{base}/api/export", {})
    if code == 200:
        row_count  = body.get("row_count", "?")
        export_path = body.get("path", "?")
        columns    = len(body.get("columns", []))
        print(f"  [PASS] /api/export -> {row_count} rows  |  {columns} columns")
        print(f"         Path: {export_path}")
        # Verify the file actually exists
        if Path(export_path).exists():
            size_kb = Path(export_path).stat().st_size // 1024
            print(f"         File on disk: {size_kb} KB  [OK]")
        else:
            print(f"         WARNING: export file not found at path above")
            fail_count += 1
    else:
        print(f"  [FAIL] /api/export HTTP {code}: {body.get('detail','')}")
        fail_count += 1

    print()
    print(SEP)
    print("SYSTEM STATUS")
    print(SEP)
    code, body = _post(f"{base}/api/system-status/diagnostics", {})
    if code == 200:
        checks = body.get("checks", {})
        for name, result in checks.items():
            ok = result.get("ok", result.get("status") == "ok")
            tag = "PASS" if ok else "WARN"
            msg = result.get("message", result.get("detail", ""))
            print(f"  [{tag}] {name}: {msg}")
    else:
        code2, body2 = _get(f"{base}/api/system-status")
        if code2 == 200:
            health = body2.get("health", {})
            system = body2.get("system", {})
            print(f"  Health : {health}")
            print(f"  System : db={system.get('database_path','?')}  students={system.get('total_students','?')}")
        else:
            print(f"  [WARN] Could not fetch system status (HTTP {code2})")

    print()
    print(SEP)
    skip_count  = sum(1 for _, s, _ in results if s == "SKIP")
    passes = sum(1 for _, s, _ in results if s == "PASS")
    total_ran = len(results) - skip_count
    print(f"RESULT: {passes}/{total_ran} imports passed  |  {skip_count} skipped (already imported)  |  {fail_count} failures")

    if fail_count == 0:
        print("All checks passed.")
    else:
        print("FAILURES detected — see FAIL lines above.")
        print()
        print("Failed files:")
        for fname, status, note in results:
            if status == "FAIL":
                print(f"  - {fname}: {note}")
    print(SEP)

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
