from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

PROJECT_DIRECTORY = Path(__file__).resolve().parents[1]
if str(PROJECT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIRECTORY))

from config import PROJECT_ROOT, get_default_settings
from database.db import create_session_factory, create_sqlite_engine, initialize_database
from database.models import StudentCurrent
from services.dashboard_intelligence_service import build_dashboard_intelligence
from services.embedding_service import get_default_embedding_model
from services.preferred_work_grouping_service import PreferredWorkGrouper
from services.technical_skill_grouping_service import TechnicalSkillGrouper


EDGE_CASE_STUDENTS = (
    ("helping at teh vet w/ animls n feeding pets", "animal handling, front desk", "helped neighbor foster kittens"),
    ("animal shelter + pet care pls, cats mostly", "pet care; scheduling", "volunteered at an adoption day"),
    ("care for stry dogs and help with adoptions", "community outreach, animal care", "fed street dogs"),
    ("urban gardning / compost projects outside", "gardening; teamwork", "balcony vegetable garden"),
    ("sustainable farming and food gardens", "soil care, Excel", "school sustainability club"),
    ("plant nursery, soil n compost work", "plant care; inventory", "helped in family nursery"),
    ("old objects / museum stuff and archives", "cataloguing, writing", "scanned family photographs"),
    ("catalog artefacts and help exhibitions", "research; labels; organization", "student art exhibition"),
    ("museum collections, labels and preservation", "archiving; careful data entry", "library volunteer"),
    ("arabic english translaton + captions for deaf ppl", "Arabic, English, subtitles", "captioned club recordings"),
    ("translate docs, subtitles n accessibility", "translation; video captions", "translated event flyers"),
    ("accessibility captions and bilingual translation", "Arabic-English; editing", "accessibility volunteer"),
    ("run esports tournments and game modding", "gaming, Discord, event setup", "organized a small tournament"),
    ("video game testing + esports event work", "bug reports; gaming", "tested student game projects"),
    ("gaming club tournaments and testing games", "event planning; QA", "gaming society committee"),
    ("beach cleanup and marine turtle conservation", "field surveys; outreach", "coastal cleanup volunteer"),
    ("ocean conservation, coast surveys n cleanups", "mapping; data collection", "citizen science survey"),
    ("protect sea life and organize beach clean ups", "team leadership; ecology", "environmental club"),
    ("anything available", "none listed", "no previous experience"),
    ("open to any role wherever needed", "basic computer", "helped family occasionally"),
    ("any position is fine im flexible", "communication", "not sure"),
    ("idk maybe animals gardens events or spreadsheets", "Excel; gardening; events", "mixed volunteering"),
    ("i like coding but also photography and helping kids", "Python; photography; tutoring", "school coding club"),
    ("softwre dev / python automtion", "Python, Git, SQL", "built two scripts"),
    ("budgts, invoices n finacial reports", "Excel; bookkeeping", "tracked club expenses"),
)


def build_students() -> tuple[StudentCurrent, ...]:
    students = []
    majors = ("Biology", "Business Administration", "Computer Science", "English Literature")
    for index, (preference, skills, experience) in enumerate(EDGE_CASE_STUDENTS, start=1):
        students.append(
            StudentCurrent(
                STUD_ID=f"EDGE{index:03d}",
                STUD_NAME=f"Edge Case Student {index:02d}",
                MAJR_DESC=majors[(index - 1) % len(majors)],
                CLAS_DESC=("Freshman", "Sophomore", "Junior", "Senior")[(index - 1) % 4],
                CUM_GPA=round(2.2 + ((index * 7) % 18) / 10, 2),
                REGISTERED_IND=True,
                ENROLLED_IND=True,
                WSP_TECHNICAL_SKILLS=skills,
                WSP_PREV_WORK=experience,
                WSP_PREFERRED_TYPE_OF_WORK=preference,
            )
        )
    return tuple(students)


def run_audit(output_path: Path) -> dict:
    settings = get_default_settings()
    embedding_model = get_default_embedding_model(settings)
    grouper = PreferredWorkGrouper(embedding_model)
    skill_grouper = TechnicalSkillGrouper(embedding_model)
    students = build_students()

    with TemporaryDirectory(prefix="wsp-preference-audit-") as temporary_directory:
        database_path = Path(temporary_directory) / "edge-cases.db"
        engine = create_sqlite_engine(database_path)
        initialize_database(engine)
        session_factory = create_session_factory(engine)
        with session_factory() as session:
            session.add_all(students)
            session.commit()
            payload = build_dashboard_intelligence(
                session,
                work_grouper=grouper,
                skill_grouper=skill_grouper,
            )
        engine.dispose()

        grouping = grouper.group(student.WSP_PREFERRED_TYPE_OF_WORK for student in students)
        records = []
        for student in students:
            assignment = grouping.for_value(student.WSP_PREFERRED_TYPE_OF_WORK)
            records.append(
                {
                    "student_id": student.STUD_ID,
                    "preferred_work": student.WSP_PREFERRED_TYPE_OF_WORK,
                    "skills": student.WSP_TECHNICAL_SKILLS,
                    "experience": student.WSP_PREV_WORK,
                    "field": assignment.field_label if assignment else "Not provided",
                    "method": assignment.method if assignment else "not_grouped",
                    "confidence": assignment.confidence if assignment else None,
                    "needs_review": assignment.needs_review if assignment else True,
                    "emerging": assignment.is_emerging if assignment else False,
                }
            )

    report = {
        "fixture_student_count": len(students),
        "database_isolation": "Temporary database deleted after audit",
        "model": grouping.model_name,
        "summary": payload["preferred_work_grouping"],
        "technical_skill_summary": payload["technical_skill_grouping"],
        "discovered_fields": payload["charts"]["work_preferences"],
        "discovered_skill_topics": payload["charts"]["technical_skills"],
        "students": records,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit preferred-work grouping with messy isolated student fixtures.")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "testbench_reports" / "preferred_work_edge_case_report.json",
    )
    args = parser.parse_args()
    report = run_audit(args.output.resolve())
    print(json.dumps({"output": str(args.output.resolve()), **report["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
