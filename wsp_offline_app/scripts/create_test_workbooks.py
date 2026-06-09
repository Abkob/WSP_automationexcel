"""
Generate four test workbooks covering the full import/filter/search test matrix.

  w1_foundation.xlsx    30 diverse students — first import
  w2_growth.xlsx        all 30 carried + 15 new + 8 updated — adds & updates
  w3_changes.xlsx       35 of 45 + 5 new + 10 edits — 10 go missing
  w4_final_1000.xlsx    1 000 students · 3 sheets — large-dataset + multi-sheet test

Usage:
    .venv\\Scripts\\python.exe scripts\\create_test_workbooks.py

Output: data/test_workbooks/
Expected import sequence and results printed at the end.
"""
from __future__ import annotations

import copy
import random
from pathlib import Path

import openpyxl
import pandas as pd

# ─── Column schema ─────────────────────────────────────────────────────────────
COLS = [
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
    "FINANCIAL_AID", "DORMS",
]

# ─── Source pools for procedural generation ────────────────────────────────────
_FIRST_M = ["Ahmad", "Ali", "Karim", "Omar", "Hassan", "Jad", "Rami", "Tarek",
            "Fadi", "Samer", "Elie", "Georges", "Tony", "Marc", "Chadi", "Ziad",
            "Nader", "Bilal", "Khaled", "Samir", "Wissam", "Ramzi", "Rabih",
            "Dani", "Patrick", "Roland", "Simon", "Nabil", "Walid", "Ghassan"]
_FIRST_F = ["Lara", "Sara", "Maya", "Nour", "Aya", "Hana", "Rima", "Dana",
            "Lina", "Mona", "Nadine", "Celine", "Joelle", "Rita", "Carla",
            "Maria", "Sandra", "Jana", "Rania", "Tania", "Mirna", "Dina",
            "Layla", "Samar", "Ghina", "Roula", "Marianne", "Christelle",
            "Pamela", "Lynn"]
_FAMILY  = ["Hassan", "Khalil", "Nassar", "Abi Nader", "Daher", "Frem",
            "Moussa", "Rizk", "Khoury", "Salameh", "Habib", "Nakad",
            "Makhoul", "Haddad", "Nasser", "Sfeir", "Azar", "Tyan",
            "Hamdan", "Saad", "Hajj", "Kanaan", "Farhat", "Zein",
            "Raad", "Jaber", "Mansour", "Kassis", "Gemayel", "Bou Khalil",
            "Karam", "Abdallah", "Francis", "Maalouf", "Ghanem",
            "Chaaban", "Turk", "Sawaya", "Lahoud", "Abboud"]

_MAJORS = {
    "EN":    [("Computer Science", ["Python, SQL, Git, Docker",
                                    "Python, SQL, FastAPI, React",
                                    "Java, Spring Boot, Kubernetes",
                                    "C++, MATLAB, Embedded systems",
                                    "Python, Machine learning, TensorFlow"]),
              ("Electrical Engineering", ["MATLAB, VHDL, Altium Designer",
                                          "MATLAB, C, circuit design, oscilloscope",
                                          "Python, FPGA, signal processing"]),
              ("Mechanical Engineering", ["SolidWorks, AutoCAD, ANSYS",
                                          "SolidWorks, CATIA, 3D printing",
                                          "MATLAB, Simulink, thermodynamics"]),
              ("Civil Engineering",      ["AutoCAD, STAAD Pro, SAP2000",
                                          "Revit, AutoCAD, GIS, project management"]),
              ("Chemical Engineering",   ["ASPEN Plus, MATLAB, process simulation",
                                          "HYSYS, lab safety, titration"])],
    "OSB":   [("Business Administration", ["Excel, PowerPoint, Tableau, SQL",
                                            "SAP, Excel, market research",
                                            "Excel, SPSS, financial modelling"]),
              ("Finance",                  ["Bloomberg terminal, Excel, Python",
                                            "Excel, SQL, risk analysis, DCF"]),
              ("Marketing",                ["Canva, Adobe Illustrator, Google Analytics",
                                            "HubSpot, social media, SEO, Canva"]),
              ("Accounting",               ["QuickBooks, Excel, IFRS knowledge",
                                            "SAP, Oracle, Excel, audit procedures"])],
    "AS":    [("Biology",           ["PCR, gel electrophoresis, microscopy",
                                     "CRISPR basics, cell culture, ELISA"]),
              ("Chemistry",         ["NMR, HPLC, titration, spectroscopy",
                                     "GC-MS, organic synthesis, lab safety"]),
              ("Mathematics",       ["MATLAB, Python, LaTeX, R",
                                     "Mathematica, Python, statistical modelling"]),
              ("Physics",           ["MATLAB, Python, LaTeX, LabVIEW",
                                     "Python, ROOT framework, data analysis"]),
              ("Psychology",        ["SPSS, qualitative research, Excel",
                                     "SPSS, NVivo, survey design"]),
              ("Political Science", ["Research writing, ArcGIS basics, Excel",
                                     "Policy analysis, data visualisation, Stata"])],
    "MSFEA": [("Architecture",         ["AutoCAD, Revit, SketchUp, Rhino",
                                         "AutoCAD, ArchiCAD, Lumion, Photoshop"]),
              ("Graphic Design",        ["Adobe Illustrator, InDesign, Figma",
                                         "Photoshop, Illustrator, After Effects"]),
              ("Landscape Architecture",["AutoCAD, SketchUp, GIS, Photoshop",
                                         "Rhino, Grasshopper, GIS, hand rendering"])],
    "FAS":   [("Agriculture",           ["GIS, ENVI, R, field sampling",
                                          "Soil analysis, SPSS, crop management"]),
              ("Food Science",          ["HPLC, sensory analysis, HACCP",
                                          "Microbiology techniques, ISO standards"]),
              ("Nutrition",             ["SPSS, dietary analysis software, Excel",
                                          "NutriBase, epidemiological methods"])],
    "AH":    [("History",              ["Archival research, Arabic, French, LaTeX",
                                         "Primary source analysis, APA/Chicago style"]),
              ("Philosophy",           ["Critical thinking, academic writing, LaTeX"]),
              ("English Literature",   ["Creative writing, content editing, research"])],
    "HS":    [("Nursing",              ["IV insertion, patient assessment, EMR systems",
                                         "Wound care, vital signs, clinical documentation"]),
              ("Public Health",        ["SPSS, epidemiology, GIS, survey tools",
                                         "R, public health surveillance, STATA"]),
              ("Physical Therapy",     ["Manual therapy, electrotherapy, exercise prescription"])]
}

_CLASSES   = ["Freshman", "Sophomore", "Junior", "Senior"]
_BOOL      = ["Y", "N"]
_TERMS     = ["202520", "202510", "202420", "202410"]
_PREV_WORK_TEMPLATES = [
    "Teaching assistant — {dept} department",
    "Research assistant — {dept} lab",
    "Intern — {company}",
    "Administrative assistant — {dept} office",
    "None",
]
_COMPANIES = ["consulting firm", "local startup", "media agency", "NGO",
              "bank", "hospital", "architecture firm", "engineering company"]
_PREFS     = {
    "Computer Science":       "Software development, data engineering",
    "Electrical Engineering":  "Hardware design, signal processing",
    "Mechanical Engineering":  "Product design, CAD drafting",
    "Civil Engineering":       "Structural engineering, project management",
    "Chemical Engineering":    "Process optimization, lab research",
    "Business Administration": "Operations management, consulting",
    "Finance":                 "Financial analysis, investment research",
    "Marketing":               "Brand strategy, digital marketing",
    "Accounting":              "Audit support, financial reporting",
    "Biology":                 "Lab assistance, research support",
    "Chemistry":               "Analytical lab work, quality control",
    "Mathematics":             "Tutoring, data analysis, research",
    "Physics":                 "Physics tutoring, instrumentation",
    "Psychology":              "Counselling support, research assistance",
    "Political Science":       "Policy research, event planning",
    "Architecture":            "Architectural drawing, design support",
    "Graphic Design":          "Visual content, social media design",
    "Landscape Architecture":  "Urban design, GIS mapping",
    "Agriculture":             "Field research, sustainable farming projects",
    "Food Science":            "Lab quality control, product development",
    "Nutrition":               "Dietetic counselling, health education",
    "History":                 "Research, archives, academic writing",
    "Philosophy":              "Academic tutoring, editorial assistance",
    "English Literature":      "Editing, creative writing, communications",
    "Nursing":                 "Clinical support, patient care",
    "Public Health":           "Health promotion, survey coordination",
    "Physical Therapy":        "Rehabilitation support, sports therapy",
}

def _col_code(major: str) -> str:
    for coll, majors in _MAJORS.items():
        if any(m == major for m, _ in majors):
            return coll
    return "AS"

def _credits(cls: str) -> int:
    return {"Freshman": random.randint(0, 30),
             "Sophomore": random.randint(31, 60),
             "Junior": random.randint(61, 90),
             "Senior": random.randint(91, 130)}[cls]

def _gpa(probation: bool = False) -> float:
    if probation:
        return round(random.uniform(1.50, 2.29), 2)
    return round(random.uniform(2.00, 4.00), 2)

def _astd(gpa: float) -> tuple[str, str]:
    if gpa >= 3.50:
        return "DL", "Dean's List"
    if gpa >= 2.00:
        return "GS", "Good Standing"
    return "AP", "Academic Probation"

def _langs(extra_french: bool = False) -> tuple[str, str]:
    written = "Arabic, English"
    spoken  = "Arabic, English"
    if extra_french or random.random() < 0.3:
        written = "Arabic, English, French"
        spoken  = "Arabic, English, French"
    return written, spoken

def make_student(stud_id: int, rng: random.Random) -> dict:
    male   = rng.random() < 0.5
    fname  = rng.choice(_FIRST_M if male else _FIRST_F)
    lname  = rng.choice(_FAMILY)
    name   = f"{fname} {lname}"

    coll   = rng.choice(list(_MAJORS.keys()))
    majr, skills_pool = rng.choice(_MAJORS[coll])
    skills = rng.choice(skills_pool)
    cls    = rng.choice(_CLASSES)
    credits= _credits(cls)
    prob   = rng.random() < 0.08
    warn   = "Y" if prob or rng.random() < 0.05 else "N"
    prob_s = "Y" if prob else "N"
    gpa    = _gpa(prob)
    astd_c, astd_d = _astd(gpa)
    written, spoken = _langs(coll in ("AH",))
    aid    = "Y" if rng.random() < 0.25 else "N"
    usaid  = "Y" if rng.random() < 0.07 else "N"
    dorms  = "Y" if rng.random() < 0.20 else "N"
    mepi   = "Y" if rng.random() < 0.05 else "N"
    gas    = "Y" if rng.random() < 0.04 else "N"
    mc     = "Y" if rng.random() < 0.06 else "N"
    term   = rng.choice(_TERMS)
    prev_tmpl = rng.choice(_PREV_WORK_TEMPLATES)
    if "{dept}" in prev_tmpl:
        prev = prev_tmpl.format(dept=majr.split()[0])
    elif "{company}" in prev_tmpl:
        prev = prev_tmpl.format(company=rng.choice(_COMPANIES))
    else:
        prev = "None"
    prev_type = "Research" if "research" in prev.lower() else (
                "Academic support" if "assistant" in prev.lower() else (
                "Internship" if "intern" in prev.lower() else "None"))
    pref = _PREFS.get(majr, "Administrative support, general assistance")
    sid = str(stud_id).zfill(6)
    email_prefix = (fname[0] + lname.replace(" ", "").replace("-", ""))[:6].lower()
    email = f"{email_prefix}{sid[-3:]}@mail.aub.edu"
    org_skills_pool = [
        "Time management, scheduling",
        "Event planning, coordination",
        "Project management, reporting",
        "Record keeping, documentation",
        "Budget tracking, logistics",
        "Team leadership, delegation",
        "Research organisation, note taking",
    ]
    interp_pool = [
        "Communication, teamwork",
        "Critical thinking, problem solving",
        "Presentation, stakeholder engagement",
        "Negotiation, active listening",
        "Attention to detail, patience",
        "Creativity, adaptability",
        "Collaboration, conflict resolution",
    ]
    add_skills_pool = [
        "Git, Linux basics",
        "Microsoft Office, Canva",
        "Adobe Photoshop, video editing",
        "R programming basics",
        "Public speaking, debate",
        "Social media management",
        "First aid certified",
        "Data entry, Excel formulas",
        "Google Workspace, Notion",
        "Basic photography",
    ]
    return {
        "STUD_ID": sid,
        "STUD_NAME": name,
        "MAJR_DESC": majr,
        "CLAS_DESC": cls,
        "STUD_EMAIL": email,
        "WSP_WRITTEN_LANGUAGES": written,
        "WSP_SPOKEN_LANGUAGES": spoken,
        "WSP_ORGANIZATIONAL_SKILLS": rng.choice(org_skills_pool),
        "WSP_TECHNICAL_SKILLS": skills,
        "WSP_INTERPERSONAL_SKILLS": rng.choice(interp_pool),
        "WSP_ADDITIONAL_SKILLS": rng.choice(add_skills_pool),
        "WSP_PREV_WORK": prev,
        "WSP_PREVIOUS_TYPE_OF_WORK": prev_type,
        "WSP_PREFERRED_TYPE_OF_WORK": pref,
        "DEANS_WARNING": warn,
        "ENRL_TERM": term,
        "DEAN_WARN": warn,
        "MOBILE_NBR": f"+9617{rng.randint(1000000, 9999999)}",
        "PROBATION": prob_s,
        "APPLICATION_DATE": f"202{rng.randint(3,5)}-09-01",
        "CUM_GPA": gpa,
        "STST_DESC": "Active",
        "STYP_CODE": "R",
        "STYP_DESC": "Regular",
        "ENROLLED_IND": "Y",
        "REGISTERED_IND": "Y",
        "LEVL_CODE": "UG",
        "COLL_CODE": coll,
        "TOTAL_CREDIT_HOURS": credits,
        "ASTD_TERM": "202420",
        "ATSD_CODE_END_OF_TERM": astd_c,
        "ASTD_DESC": astd_d,
        "ASTD_DATE_END_OF_TERM": "2024-06-01",
        "USAID": usaid,
        "MASTER_CARD": mc,
        "UPP_MEPI": mepi,
        "GAS": gas,
        "FINANCIAL_AID": aid,
        "DORMS": dorms,
    }


def write_single_sheet(rows: list[dict], path: Path, sheet_name: str = "Sheet1") -> None:
    df = pd.DataFrame(rows, columns=COLS)
    df.to_excel(path, index=False, sheet_name=sheet_name, engine="openpyxl")
    print(f"  {path.name:<40}  {len(rows):>5} student rows")


def write_multi_sheet(students: list[dict], path: Path) -> None:
    """Write the 1 000-student workbook with 3 sheets."""
    df_students = pd.DataFrame(students, columns=COLS)

    # ── Sheet 2: major summary ──────────────────────────────────────────────
    summary = (
        df_students.groupby("MAJR_DESC")
        .agg(
            Count=("STUD_ID", "count"),
            Avg_GPA=("CUM_GPA", "mean"),
            On_Probation=("PROBATION", lambda s: (s == "Y").sum()),
            Financial_Aid=("FINANCIAL_AID", lambda s: (s == "Y").sum()),
        )
        .reset_index()
        .rename(columns={"MAJR_DESC": "Major"})
        .sort_values("Count", ascending=False)
    )
    summary["Avg_GPA"] = summary["Avg_GPA"].round(2)

    # ── Sheet 3: financial aid roster ──────────────────────────────────────
    aid_cols = ["STUD_ID", "STUD_NAME", "MAJR_DESC", "CLAS_DESC", "CUM_GPA",
                "FINANCIAL_AID", "USAID", "UPP_MEPI", "GAS", "MASTER_CARD", "DORMS"]
    aid_df = df_students[aid_cols][df_students["FINANCIAL_AID"] == "Y"].copy()

    with pd.ExcelWriter(str(path), engine="openpyxl") as writer:
        df_students.to_excel(writer, index=False, sheet_name="Sheet1")
        summary.to_excel(writer, index=False, sheet_name="Major_Summary")
        aid_df.to_excel(writer, index=False, sheet_name="Aid_Roster")

    sheets_info = f"Sheet1({len(students)}), Major_Summary({len(summary)}), Aid_Roster({len(aid_df)})"
    print(f"  {path.name:<40}  {sheets_info}")


def main() -> None:
    rng = random.Random(42)  # fixed seed -> reproducible
    out = Path(__file__).resolve().parent.parent / "data" / "test_workbooks"
    out.mkdir(parents=True, exist_ok=True)
    print(f"Writing test workbooks to: {out}\n")

    # ── Generate the master pool: IDs 100001–101000 ─────────────────────────
    all_students: dict[str, dict] = {}
    for i in range(1, 1001):
        s = make_student(100000 + i, rng)
        all_students[s["STUD_ID"]] = s

    ids = list(all_students.keys())  # ["100001", …, "101000"]

    # ── Wave 1: first 30 students — clean foundation ─────────────────────────
    w1_ids = ids[:30]
    w1 = [all_students[i] for i in w1_ids]
    write_single_sheet(w1, out / "w1_foundation.xlsx")

    # ── Wave 2: all 30 carried + 15 new + 8 updated ──────────────────────────
    w2_new_ids  = ids[30:45]
    w2_carry    = [copy.deepcopy(all_students[i]) for i in w1_ids]
    w2_new      = [all_students[i] for i in w2_new_ids]

    # 8 deliberate updates to carried-forward students
    updates_w2 = [
        (0,  {"CUM_GPA": round(w2_carry[0]["CUM_GPA"] + 0.25, 2),
               "WSP_TECHNICAL_SKILLS": w2_carry[0]["WSP_TECHNICAL_SKILLS"] + ", Docker"}),
        (2,  {"PROBATION": "Y", "DEANS_WARNING": "Y", "DEAN_WARN": "Y",
               "CUM_GPA": 2.10, "ATSD_CODE_END_OF_TERM": "AP",
               "ASTD_DESC": "Academic Probation"}),
        (5,  {"FINANCIAL_AID": "Y"}),
        (8,  {"DORMS": "Y", "CUM_GPA": round(w2_carry[8]["CUM_GPA"] - 0.30, 2)}),
        (11, {"WSP_PREFERRED_TYPE_OF_WORK": w2_carry[11]["WSP_PREFERRED_TYPE_OF_WORK"]
               + ", project coordination"}),
        (15, {"CLAS_DESC": "Junior",
               "TOTAL_CREDIT_HOURS": w2_carry[15]["TOTAL_CREDIT_HOURS"] + 30}),
        (20, {"STST_DESC": "Active", "REGISTERED_IND": "Y",
               "WSP_ORGANIZATIONAL_SKILLS": "Advanced scheduling, cross-team coordination"}),
        (27, {"CUM_GPA": min(4.0, round(w2_carry[27]["CUM_GPA"] + 0.40, 2)),
               "ATSD_CODE_END_OF_TERM": "DL", "ASTD_DESC": "Dean's List"}),
    ]
    for idx, changes in updates_w2:
        w2_carry[idx].update(changes)

    write_single_sheet(w2_carry + w2_new, out / "w2_growth.xlsx")

    # ── Wave 3: 35 of 45 + 5 new + 10 edits; 10 go missing ──────────────────
    # Drop IDs at positions 3, 7, 14, 22, 28 from the 45-student set
    # and positions 1, 6, 11, 38, 44 from the w2_ids list
    w2_all_ids  = w1_ids + w2_new_ids
    missing_indices = {3, 7, 14, 22, 28, 32, 36, 40, 42, 44}
    w3_carry_ids = [iid for j, iid in enumerate(w2_all_ids) if j not in missing_indices]
    w3_new_ids   = ids[45:50]

    # Build carry from the w2 dataset (preserves w2 edits, like a real export)
    w2_by_id = {s["STUD_ID"]: s for s in w2_carry + w2_new}
    w3_carry = [copy.deepcopy(w2_by_id[i]) for i in w3_carry_ids]
    w3_new   = [all_students[i] for i in w3_new_ids]

    # 10 deliberate updates in wave 3
    updates_w3 = [
        (0,  {"PROBATION": "N", "DEANS_WARNING": "N", "DEAN_WARN": "N",
               "CUM_GPA": 2.50, "ATSD_CODE_END_OF_TERM": "GS",
               "ASTD_DESC": "Good Standing"}),                       # probation lifted
        (1,  {"CUM_GPA": min(4.0, round(w3_carry[1]["CUM_GPA"] + 0.15, 2))}),
        (4,  {"DORMS": "N"}),                                         # moved out of dorms
        (6,  {"WSP_TECHNICAL_SKILLS": w3_carry[6]["WSP_TECHNICAL_SKILLS"]
               + ", Kubernetes, Helm"}),
        (9,  {"FINANCIAL_AID": "N"}),                                 # aid removed
        (12, {"CLAS_DESC": "Senior",
               "TOTAL_CREDIT_HOURS": w3_carry[12]["TOTAL_CREDIT_HOURS"] + 30}),
        (16, {"USAID": "Y"}),
        (18, {"CUM_GPA": round(w3_carry[18]["CUM_GPA"] - 0.50, 2),
               "PROBATION": "Y", "DEANS_WARNING": "Y", "DEAN_WARN": "Y",
               "ATSD_CODE_END_OF_TERM": "AP", "ASTD_DESC": "Academic Probation"}),
        (24, {"WSP_PREFERRED_TYPE_OF_WORK": "Data science, AI research"}),
        (30, {"ENRL_TERM": "202520", "REGISTERED_IND": "Y"}),
    ]
    for idx, changes in updates_w3:
        if idx < len(w3_carry):
            w3_carry[idx].update(changes)

    write_single_sheet(w3_carry + w3_new, out / "w3_changes.xlsx")

    # ── Wave 4: full 1 000 students, 3 sheets ────────────────────────────────
    # Use fresh copies so wave 3 edits don't leak into the large workbook
    w4_students = [copy.deepcopy(all_students[i]) for i in ids]
    write_multi_sheet(w4_students, out / "w4_final_1000.xlsx")

    # ── Summary ──────────────────────────────────────────────────────────────
    missing_ids = [w2_all_ids[j] for j in sorted(missing_indices) if j < len(w2_all_ids)]
    print()
    print("-" * 60)
    print("Import order and expected results:")
    print(f"  1. w1_foundation.xlsx  ->  30 new,  0 updated,   0 unchanged,  0 missing")
    print(f"  2. w2_growth.xlsx      ->  15 new,  8 updated,  22 unchanged,  0 missing")
    print(f"  3. w3_changes.xlsx     ->   5 new, 10 updated,  25 unchanged, 10 missing")
    print(f"     Missing: {', '.join(missing_ids)}")
    print(f"  4. w4_final_1000.xlsx  -> 950 new, 13 updated,  37 unchanged,  0 missing")
    print(f"     (w4 has original data; 8 w2-edited + 10 w3-edited students differ from DB)")
    print(f"     (Multi-sheet: Sheet1 / Major_Summary / Aid_Roster; import reads Sheet1 only)")
    print()
    print("Filter/search test targets in w4_final_1000.xlsx:")
    on_prob = sum(1 for s in w4_students if s["PROBATION"] == "Y")
    on_aid  = sum(1 for s in w4_students if s["FINANCIAL_AID"] == "Y")
    in_dorm = sum(1 for s in w4_students if s["DORMS"] == "Y")
    print(f"  Probation:    {on_prob:>4} students")
    print(f"  Financial Aid:{on_aid:>4} students")
    print(f"  Dorms:        {in_dorm:>4} students")
    from collections import Counter
    class_counts = Counter(s["CLAS_DESC"] for s in w4_students)
    for cls in _CLASSES:
        print(f"  {cls:<12}: {class_counts[cls]:>4} students")


if __name__ == "__main__":
    main()
