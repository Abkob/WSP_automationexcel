import json
import time
import urllib.request
from pathlib import Path

from openpyxl import Workbook

BASE = "http://127.0.0.1:8080"


def post(url, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())


# ── 1. fresh single-student file (never seen before) ──────────────────────────
p = Path("data/testbench/Z_reindex_test.xlsx")
p.parent.mkdir(exist_ok=True)
wb = Workbook()
ws = wb.active
ws.append([
    "STUD_ID", "STUD_NAME", "MAJR_DESC", "CLAS_DESC", "CUM_GPA",
    "PROBATION", "FINANCIAL_AID", "DORMS",
    "WSP_TECHNICAL_SKILLS", "WSP_PREFERRED_TYPE_OF_WORK",
    "ENRL_TERM", "LEVL_CODE", "COLL_CODE", "ENROLLED_IND", "REGISTERED_IND", "STST_DESC",
])
ws.append([
    "999001", "Test Reindex Student", "Computer Science", "Junior", 3.55,
    "N", "N", "N",
    "Python, FastAPI, Docker, SQL, REST APIs",
    "Backend software development, API design",
    "202520", "UG", "EN", "Y", "Y", "Active",
])
wb.save(p)
print(f"Created: {p}")

# ── 2. import ─────────────────────────────────────────────────────────────────
t0 = time.monotonic()
result = post(f"{BASE}/api/import/run", {"path": str(p.resolve())})
import_ms = (time.monotonic() - t0) * 1000
nr = result.get("new_rows", 0)
ur = result.get("updated_rows", 0)
print(f"Import: {import_ms:.0f} ms  new={nr}  updated={ur}")

# ── 3. wait for background reindex ────────────────────────────────────────────
print("Waiting 5 s for background reindex thread...")
time.sleep(5)

# ── 4. timed search (should hit warm index) ───────────────────────────────────
t1 = time.monotonic()
sr = post(f"{BASE}/api/search", {
    "semantic_query": "backend Python software development API",
    "page_size": 10,
    "semantic_threshold": 0.3,
})
search_ms = (time.monotonic() - t1) * 1000
total = sr.get("total_count", 0)
students = sr.get("students", [])
print(f"Search: {search_ms:.0f} ms  total={total}  returned={len(students)}")
for s in students[:5]:
    print(f"  {s.get('score', 0):.3f}  {s.get('STUD_NAME')}  ({s.get('MAJR_DESC')})")

# ── 5. second search immediately after (index definitely warm) ────────────────
t2 = time.monotonic()
sr2 = post(f"{BASE}/api/search", {
    "semantic_query": "backend Python software development API",
    "page_size": 10,
    "semantic_threshold": 0.3,
})
search2_ms = (time.monotonic() - t2) * 1000
print(f"Repeat : {search2_ms:.0f} ms  (should be near-identical, no re-encoding)")
