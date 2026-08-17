from __future__ import annotations

from database.db import create_session_factory, create_sqlite_engine, initialize_database
from database.models import StudentCurrent
from services.dashboard_intelligence_service import build_dashboard_intelligence, faculty_for_major
from services.preferred_work_grouping_service import PreferredWorkGrouper, WORK_FIELDS
from services.technical_skill_grouping_service import SKILL_TOPICS, TechnicalSkillGrouper

import numpy as np


class DashboardWorkEmbeddingModel:
    model_name = "test/dashboard-work"

    def encode(self, texts, *, kind: str):
        vectors = []
        for text in texts:
            vector = np.zeros(len(WORK_FIELDS) + 1, dtype=np.float32)
            if kind == "document":
                index = next(index for index, field in enumerate(WORK_FIELDS) if text in field.anchors)
                vector[index] = 1.0
            elif "data" in text.casefold() or "software" in text.casefold():
                vector[1] = 1.0
            elif "animal" in text.casefold() or "pet" in text.casefold():
                vector[len(WORK_FIELDS)] = 1.0
            else:
                vector[:len(WORK_FIELDS)] = 1 / np.sqrt(len(WORK_FIELDS))
            vectors.append(vector)
        return np.asarray(vectors, dtype=np.float32)


class DashboardSkillEmbeddingModel:
    model_name = "test/dashboard-skills"

    def encode(self, texts, *, kind: str):
        vectors = []
        for text in texts:
            vector = np.zeros(len(SKILL_TOPICS) + 1, dtype=np.float32)
            if kind == "document":
                index = next(index for index, topic in enumerate(SKILL_TOPICS) if text in topic.anchors)
                vector[index] = 1.0
            elif "drone" in text.casefold() or "uav" in text.casefold():
                vector[len(SKILL_TOPICS)] = 1.0
            else:
                vector[:len(SKILL_TOPICS)] = 1 / np.sqrt(len(SKILL_TOPICS))
            vectors.append(vector)
        return np.asarray(vectors, dtype=np.float32)


def test_official_faculty_mapping_uses_major_not_unreliable_college_code() -> None:
    assert faculty_for_major("Computer Science")["code"] == "FAS"
    assert faculty_for_major("Political Science")["code"] == "FAS"
    assert faculty_for_major("Architecture")["code"] == "MSFEA"
    assert faculty_for_major("Electrical and Computer Engineering")["code"] == "MSFEA"
    assert faculty_for_major("Accounting")["code"] == "OSB"
    assert faculty_for_major("Nursing")["code"] == "HSON"
    assert faculty_for_major("Public Health")["code"] == "FHS"
    assert faculty_for_major("New Experimental Major")["code"] == "UNMAPPED"


def test_dashboard_intelligence_filters_and_summarizes_students(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "dashboard.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(
                    STUD_ID="1001",
                    STUD_NAME="FAS Student",
                    MAJR_DESC="Computer Science",
                    COLL_CODE="EN",
                    CLAS_DESC="Junior",
                    CUM_GPA=3.6,
                    TOTAL_CREDIT_HOURS=70,
                    REGISTERED_IND=True,
                    ENROLLED_IND=True,
                    FINANCIAL_AID=True,
                    PROBATION=False,
                    STUD_EMAIL="fas@aub.edu.lb",
                    MOBILE_NBR="123",
                    WSP_TECHNICAL_SKILLS="Python, SQL",
                    WSP_PREFERRED_TYPE_OF_WORK="Data analysis",
                ),
                StudentCurrent(
                    STUD_ID="1002",
                    STUD_NAME="OSB Student",
                    MAJR_DESC="Finance",
                    COLL_CODE="OSB",
                    CLAS_DESC="Senior",
                    CUM_GPA=2.1,
                    FINANCIAL_AID=False,
                    PROBATION=True,
                ),
            ]
        )
        session.commit()

        payload = build_dashboard_intelligence(
            session,
            work_grouper=PreferredWorkGrouper(DashboardWorkEmbeddingModel()),
            faculty="FAS",
            class_year="Junior",
        )

    assert payload["total_matches"] == 1
    assert payload["selection_label"] == "FAS · Junior"
    assert payload["metrics"]["average_gpa"] == 3.6
    assert payload["metrics"]["registered_rate"] == 100.0
    assert "workstudy_ready_count" not in payload["metrics"]
    assert payload["faculty_summary"][0]["count"] == 1
    assert payload["students"][0]["faculty"] == "FAS"
    assert payload["charts"]["students_by_faculty"] == [
        {"label": "FAS", "value": 1, "color": "#7A1831", "detail": "Arts & Sciences"}
    ]
    assert payload["charts"]["work_preferences"][0]["label"] == "Data & Technology"
    assert payload["students"][0]["work_preference"] == "Data analysis"
    assert payload["students"][0]["work_preference_group"] == "Data & Technology"
    assert payload["preferred_work_grouping"]["assigned_count"] == 1
    assert payload["charts"]["attention_rate_by_faculty"][0]["label"] == "FAS"
    assert payload["charts"]["data_completeness"]
    assert "workstudy_readiness_by_faculty" not in payload["charts"]
    assert "readiness_rate" not in payload["faculty_summary"][0]


def test_attention_filter_and_quality_metrics_are_transparent(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "attention.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="1001", STUD_NAME="Alert", MAJR_DESC="Finance", PROBATION=True),
                StudentCurrent(STUD_ID="1002", STUD_NAME="Clear", MAJR_DESC="Finance", PROBATION=False),
            ]
        )
        session.commit()
        payload = build_dashboard_intelligence(session, attention="yes")

    assert payload["total_matches"] == 1
    assert payload["metrics"]["attention_count"] == 1
    assert payload["quality"]["missing_email"] == 1
    assert payload["quality"]["missing_any_core"] == 1
    assert payload["quality_students"][0]["student_id"] == "1001"
    assert payload["students"][0]["attention_label"] == "Probation"


def test_dashboard_supports_multiple_values_per_category(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "dashboard-multiselect.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="fas", STUD_NAME="FAS", MAJR_DESC="Computer Science", CLAS_DESC="Junior"),
                StudentCurrent(STUD_ID="osb", STUD_NAME="OSB", MAJR_DESC="Finance", CLAS_DESC="Senior"),
                StudentCurrent(STUD_ID="hson", STUD_NAME="HSON", MAJR_DESC="Nursing", CLAS_DESC="Freshman"),
            ]
        )
        session.commit()
        payload = build_dashboard_intelligence(
            session,
            faculty="FAS,OSB",
            major="Computer Science,Finance",
            class_year="Junior,Senior",
        )

    assert payload["total_matches"] == 2
    assert payload["selection"]["faculty"] == ("FAS", "OSB")
    assert payload["selection"]["major"] == ("Computer Science", "Finance")
    assert payload["selection"]["class_year"] == ("Junior", "Senior")
    assert {student["student_id"] for student in payload["candidate_students"]} == {"fas", "osb"}


def test_previous_experience_remains_optional_candidate_context(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "optional-experience.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        session.add(
            StudentCurrent(
                STUD_ID="first-job",
                STUD_NAME="First Job Candidate",
                MAJR_DESC="Finance",
                WSP_TECHNICAL_SKILLS="Excel",
                WSP_PREFERRED_TYPE_OF_WORK="Data entry",
            )
        )
        session.commit()
        payload = build_dashboard_intelligence(session)

    assert payload["total_matches"] == 1
    assert payload["candidate_students"][0]["student_id"] == "first-job"
    assert payload["candidate_students"][0]["has_experience"] is False
    assert "workstudy_ready" not in payload["candidate_students"][0]
    assert "Previous experience" not in {point["label"] for point in payload["charts"]["data_completeness"]}


def test_emerging_work_field_is_discovered_from_full_population_before_filtering(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "emerging.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(
                    STUD_ID="1001",
                    STUD_NAME="Animal One",
                    MAJR_DESC="Biology",
                    WSP_PREFERRED_TYPE_OF_WORK="animal shelter care",
                ),
                StudentCurrent(
                    STUD_ID="1002",
                    STUD_NAME="Animal Two",
                    MAJR_DESC="Finance",
                    WSP_PREFERRED_TYPE_OF_WORK="pet and animal support",
                ),
            ]
        )
        session.commit()
        payload = build_dashboard_intelligence(
            session,
            work_grouper=PreferredWorkGrouper(DashboardWorkEmbeddingModel()),
            faculty="FAS",
        )

    assert payload["total_matches"] == 1
    assert payload["preferred_work_grouping"]["emerging_field_count"] == 1
    assert payload["students"][0]["work_preference_is_emerging"] is True
    assert payload["charts"]["work_preferences"][0]["label"].startswith("Emerging ·")


def test_dynamic_skill_topic_uses_cross_student_evidence_before_filtering(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "skill-emerging.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(
                    STUD_ID="1001",
                    STUD_NAME="Drone One",
                    MAJR_DESC="Biology",
                    WSP_TECHNICAL_SKILLS="drone piloting",
                ),
                StudentCurrent(
                    STUD_ID="1002",
                    STUD_NAME="Drone Two",
                    MAJR_DESC="Finance",
                    WSP_TECHNICAL_SKILLS="UAV flight controls",
                ),
            ]
        )
        session.commit()
        payload = build_dashboard_intelligence(
            session,
            skill_grouper=TechnicalSkillGrouper(DashboardSkillEmbeddingModel()),
            faculty="FAS",
        )

    assert payload["total_matches"] == 1
    assert payload["technical_skill_grouping"]["emerging_topic_count"] == 1
    assert payload["technical_skill_grouping"]["emerging_count"] == 1
    assert payload["charts"]["technical_skills"][0]["label"].startswith("Emerging ·")
    assert payload["charts"]["technical_skills"][0]["value"] == 1
