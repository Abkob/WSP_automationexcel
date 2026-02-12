"""Generate test Excel sheets for merge testing. Run once, then delete."""
import pandas as pd
import numpy as np
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Columns that match the real dataset ──────────────────────────────────────
COLUMNS = [
    "STUD_ID", "STUD_NAME", "MAJR_DESC", "CLAS_DESC", "STUD_EMAIL",
    "WSP_WRITTEN_LANGUAGES", "WSP_SPOKEN_LANGUAGES",
    "WSP_ORGANIZATIONAL_SKILLS", "WSP_TECHNICAL_SKILLS",
    "WSP_INTERPERSONAL_SKILLS", "WSP_ADDITIONAL_SKILLS",
    "WSP_PREV_WORK", "WSP_PREVIOUS_TYPE_OF_WORK", "WSP_PREFERRED_TYPE_OF_WORK",
    "DEANS_WARNING", "ENRL_TERM", "DEAN_WARN", "MOBILE_NBR", "PROBATION",
    "APPLICATION_DATE", "CUM_GPA", "STST_DESC", "STYP_CODE", "STYP_DESC",
    "ENROLLED_IND", "REGISTERED_IND", "LEVL_CODE", "COLL_CODE",
    "TOTAL_CREDIT_HOURS", "ASTD_TERM", "ATSD_CODE_END_OF_TERM", "ASTD_DESC",
    "ASTD_DATE_END_OF_TERM", "USAID", "MASTER_CARD", "UPP_MEPI", "GAS",
]

MAJORS = ["CS", "ECE", "ME", "BIO", "MATH", "PHYS", "ECON", "ARCH"]
CLASSES = ["Freshman", "Sophomore", "Junior", "Senior"]
TERMS = ["Fall24", "Spring25", "Summer25"]
STATUSES = ["Active", "Graduated", "Inactive"]

rng = np.random.default_rng(42)


def _make_rows(start_id, count):
    rows = []
    for i in range(count):
        sid = start_id + i
        rows.append({
            "STUD_ID": sid,
            "STUD_NAME": f"NewStudent_{sid}",
            "MAJR_DESC": rng.choice(MAJORS),
            "CLAS_DESC": rng.choice(CLASSES),
            "STUD_EMAIL": f"new{sid}@example.edu",
            "WSP_WRITTEN_LANGUAGES": "EN",
            "WSP_SPOKEN_LANGUAGES": "EN,AR",
            "WSP_ORGANIZATIONAL_SKILLS": rng.choice(["Low", "Medium", "High"]),
            "WSP_TECHNICAL_SKILLS": rng.choice(["Basic", "Intermediate", "Advanced"]),
            "WSP_INTERPERSONAL_SKILLS": rng.choice(["Low", "Medium", "High"]),
            "WSP_ADDITIONAL_SKILLS": "Excel",
            "WSP_PREV_WORK": rng.choice(["Yes", "No"]),
            "WSP_PREVIOUS_TYPE_OF_WORK": rng.choice(["Office", "Remote", ""]),
            "WSP_PREFERRED_TYPE_OF_WORK": rng.choice(["Office", "Remote", "Hybrid"]),
            "DEANS_WARNING": rng.choice(["Yes", "No"]),
            "ENRL_TERM": rng.choice(TERMS),
            "DEAN_WARN": rng.choice(["Y", "N"]),
            "MOBILE_NBR": f"70{rng.integers(100000, 999999)}",
            "PROBATION": rng.choice(["Yes", "No"]),
            "APPLICATION_DATE": f"2025-{rng.integers(1,13):02d}-{rng.integers(1,29):02d}",
            "CUM_GPA": round(rng.uniform(2.0, 4.0), 2),
            "STST_DESC": rng.choice(STATUSES),
            "STYP_CODE": "UG",
            "STYP_DESC": "Undergrad",
            "ENROLLED_IND": rng.choice(["Y", "N"]),
            "REGISTERED_IND": "Y",
            "LEVL_CODE": "UG",
            "COLL_CODE": rng.choice(["SCI", "ENG", "ART", "BUS"]),
            "TOTAL_CREDIT_HOURS": int(rng.integers(30, 130)),
            "ASTD_TERM": rng.choice(TERMS),
            "ATSD_CODE_END_OF_TERM": rng.choice(["GOOD", "WARN", "PROB"]),
            "ASTD_DESC": rng.choice(["Good Standing", "Probation", "Warning"]),
            "ASTD_DATE_END_OF_TERM": f"2025-{rng.integers(1,13):02d}-01",
            "USAID": rng.choice(["Yes", "No"]),
            "MASTER_CARD": rng.choice(["Yes", "No"]),
            "UPP_MEPI": rng.choice(["Yes", "No"]),
            "GAS": rng.choice(["Yes", "No"]),
        })
    return rows


# ── 1. COMPATIBLE file: same columns, new students ──────────────────────────
print("Creating test_compatible.xlsx  (15 new students, same columns)...")
df_compat = pd.DataFrame(_make_rows(9000, 15), columns=COLUMNS)
compat_path = os.path.join(OUT_DIR, "test_compatible.xlsx")
df_compat.to_excel(compat_path, index=False)
print(f"  -> {compat_path}")

# ── 2. COMPATIBLE with OVERLAP: has some IDs that exist in final_snapshot ────
print("Creating test_overlap.xlsx  (10 students, 5 overlap with original)...")
overlap_rows = _make_rows(1000, 5) + _make_rows(9500, 5)  # IDs 1000-1004 overlap
df_overlap = pd.DataFrame(overlap_rows, columns=COLUMNS)
overlap_path = os.path.join(OUT_DIR, "test_overlap.xlsx")
df_overlap.to_excel(overlap_path, index=False)
print(f"  -> {overlap_path}")

# ── 3. INCOMPATIBLE file: different columns ──────────────────────────────────
print("Creating test_incompatible.xlsx  (different columns)...")
df_incompat = pd.DataFrame({
    "ID": range(100, 110),
    "Name": [f"Person_{i}" for i in range(10)],
    "Score": rng.uniform(50, 100, 10).round(1),
    "Department": [rng.choice(["HR", "IT", "Sales"]) for _ in range(10)],
})
incompat_path = os.path.join(OUT_DIR, "test_incompatible.xlsx")
df_incompat.to_excel(incompat_path, index=False)
print(f"  -> {incompat_path}")

print()
print("Done! Test files created:")
print(f"  test_compatible.xlsx   - should MERGE successfully")
print(f"  test_overlap.xlsx      - should MERGE with dedup (5 overlap)")
print(f"  test_incompatible.xlsx - should be REJECTED (column mismatch)")
