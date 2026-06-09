"""
Reset all student data and application state.

Deletes:
  - The SQLite database (wsp.db, wsp.db-shm, wsp.db-wal)
  - All backups       (data/backups/)
  - All exports       (data/exports/)
  - All archive files (data/archive/)
  - The semantic vector index (data/semantic_index/)
  - Application logs  (data/logs/)

Keeps:
  - The data/ folder structure itself
  - data/import_folder_config.json (your import-folder path preference)
  - data/test_workbooks/ (the generated test workbooks)

The database is recreated fresh (empty) on the next app launch.

Usage:
    .venv\\Scripts\\python.exe scripts\\reset_data.py
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def _read_import_folder_path() -> Path | None:
    config_path = DATA_DIR / "import_folder_config.json"
    if not config_path.exists():
        return None
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        p = Path(data.get("import_folder_path", ""))
        return p if p.is_dir() else None
    except Exception:
        return None


def _count_excel_files(folder: Path) -> list[Path]:
    return [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in {".xlsx", ".xls", ".xlsm"} and not f.name.startswith("~$")]


def _delete_files(folder: Path, *, label: str) -> int:
    if not folder.exists():
        return 0
    count = 0
    for item in folder.iterdir():
        try:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
            count += 1
        except Exception as exc:
            print(f"  WARNING: could not delete {item.name}: {exc}")
    print(f"  Cleared {label}: {count} item(s) removed")
    return count


def main() -> None:
    print()
    print("WSP Offline System — Data Reset")
    print("=" * 44)
    print()
    print("This will permanently delete:")
    print("  - The student database (wsp.db)")
    print("  - All backups, exports, archives")
    print("  - The semantic search index")
    print("  - Application logs")
    print()

    import_folder = _read_import_folder_path()
    if import_folder and import_folder.is_dir():
        excel_files = _count_excel_files(import_folder)
        if excel_files:
            print(f"  WARNING: Your Import Folder has {len(excel_files)} Excel file(s):")
            for f in excel_files[:5]:
                print(f"    - {f.name}")
            if len(excel_files) > 5:
                print(f"    ... and {len(excel_files) - 5} more")
            print()
            print("  After reset, the app will RE-IMPORT these files automatically on")
            print("  next startup (the import history is cleared with the database).")
            print("  To prevent that, remove or move those files before restarting.")
            print()

    answer = input("Type YES to confirm reset, or anything else to cancel: ").strip()
    if answer != "YES":
        print("\nCancelled — nothing was changed.")
        sys.exit(0)

    print()

    # ── Database files ────────────────────────────────────────────────────────
    removed_db = 0
    for db_file in ["wsp.db", "wsp.db-shm", "wsp.db-wal"]:
        p = DATA_DIR / db_file
        if p.exists():
            p.unlink()
            removed_db += 1
    print(f"  Deleted database: {removed_db} file(s)")

    # ── Subdirectories to wipe ────────────────────────────────────────────────
    _delete_files(DATA_DIR / "backups",        label="backups")
    _delete_files(DATA_DIR / "exports",        label="exports")
    _delete_files(DATA_DIR / "archive",        label="archive")
    _delete_files(DATA_DIR / "semantic_index", label="semantic index")
    _delete_files(DATA_DIR / "logs",           label="logs")

    print()
    print("Reset complete.")
    print("Launch the app normally — a fresh empty database will be created automatically.")
    print()


if __name__ == "__main__":
    main()
