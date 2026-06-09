from __future__ import annotations

from database.db import create_session_factory, create_sqlite_engine, initialize_database
from database.models import ImportBatch, StudentCurrent
from services.analytics_service import (
    ChartPoint,
    TextFrequencyPoint,
    get_dashboard_charts,
    get_dashboard_metrics,
    get_latest_import_summary,
    get_text_and_semantic_analytics,
    normalize_subjective_term,
    split_subjective_terms,
)


def test_dashboard_metrics_on_empty_database(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        metrics = get_dashboard_metrics(session)

    assert metrics.total_students == 0
    assert metrics.new_students_latest_import == 0
    assert metrics.updated_students_latest_import == 0
    assert metrics.average_gpa is None
    assert metrics.probation_count == 0
    assert metrics.dean_warning_count == 0
    assert metrics.financial_aid_count == 0
    assert metrics.dorm_count == 0
    assert metrics.registered_count == 0
    assert metrics.enrolled_count == 0


def test_dashboard_metrics_on_fixture_database(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add_all(
            [
                ImportBatch(filename="old.xlsx", file_path="C:/old.xlsx", file_hash="old", new_rows=1, updated_rows=0),
                ImportBatch(filename="new.xlsx", file_path="C:/new.xlsx", file_hash="new", new_rows=2, updated_rows=1),
                StudentCurrent(
                    STUD_ID="1001",
                    CUM_GPA=3.0,
                    PROBATION=False,
                    DEANS_WARNING=False,
                    DEAN_WARN=False,
                    FINANCIAL_AID=True,
                    DORMS=False,
                    REGISTERED_IND=True,
                    ENROLLED_IND=True,
                ),
                StudentCurrent(
                    STUD_ID="1002",
                    CUM_GPA=4.0,
                    PROBATION=True,
                    DEANS_WARNING=True,
                    DEAN_WARN=False,
                    FINANCIAL_AID=True,
                    DORMS=True,
                    REGISTERED_IND=True,
                    ENROLLED_IND=False,
                ),
                StudentCurrent(
                    STUD_ID="1003",
                    CUM_GPA=None,
                    PROBATION=False,
                    DEANS_WARNING=False,
                    DEAN_WARN=True,
                    FINANCIAL_AID=False,
                    DORMS=False,
                    REGISTERED_IND=False,
                    ENROLLED_IND=False,
                ),
            ]
        )
        session.commit()

    with session_factory() as session:
        metrics = get_dashboard_metrics(session)

    assert metrics.total_students == 3
    assert metrics.new_students_latest_import == 2
    assert metrics.updated_students_latest_import == 1
    assert metrics.average_gpa == 3.5
    assert metrics.probation_count == 1
    assert metrics.dean_warning_count == 2
    assert metrics.financial_aid_count == 2
    assert metrics.dorm_count == 1
    assert metrics.registered_count == 2
    assert metrics.enrolled_count == 1


def test_dashboard_metrics_can_include_or_exclude_missing_students(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="1001", CUM_GPA=4.0, FINANCIAL_AID=True),
                StudentCurrent(STUD_ID="1002", CUM_GPA=2.0, FINANCIAL_AID=True, missing_from_latest_import=True),
            ]
        )
        session.commit()

    with session_factory() as session:
        excluded = get_dashboard_metrics(session)
        included = get_dashboard_metrics(session, include_missing=True)

    assert excluded.total_students == 1
    assert excluded.average_gpa == 4.0
    assert excluded.financial_aid_count == 1
    assert included.total_students == 2
    assert included.average_gpa == 3.0
    assert included.financial_aid_count == 2


def test_dashboard_chart_data_on_empty_database(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        charts = get_dashboard_charts(session)

    assert charts.students_by_major == ()
    assert charts.students_by_class == ()
    assert charts.average_gpa_by_major == ()
    assert charts.probation_by_major == ()
    assert charts.financial_aid_distribution == ()
    assert charts.gpa_distribution == (
        ChartPoint("0.00-0.99", 0),
        ChartPoint("1.00-1.99", 0),
        ChartPoint("2.00-2.99", 0),
        ChartPoint("3.00-3.49", 0),
        ChartPoint("3.50-4.00", 0),
    )


def test_dashboard_chart_data_shape_and_values(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="1001", MAJR_DESC="Computer Science", CLAS_DESC="Senior", CUM_GPA=3.8, PROBATION=False, FINANCIAL_AID=True),
                StudentCurrent(STUD_ID="1002", MAJR_DESC="Computer Science", CLAS_DESC="Junior", CUM_GPA=3.2, PROBATION=True, FINANCIAL_AID=True),
                StudentCurrent(STUD_ID="1003", MAJR_DESC="Business", CLAS_DESC="Senior", CUM_GPA=2.7, PROBATION=True, FINANCIAL_AID=False),
            ]
        )
        session.commit()

    with session_factory() as session:
        charts = get_dashboard_charts(session)

    assert charts.students_by_major == (
        ChartPoint("Computer Science", 2),
        ChartPoint("Business", 1),
    )
    assert charts.students_by_class == (
        ChartPoint("Senior", 2),
        ChartPoint("Junior", 1),
    )
    assert charts.gpa_distribution == (
        ChartPoint("0.00-0.99", 0),
        ChartPoint("1.00-1.99", 0),
        ChartPoint("2.00-2.99", 1),
        ChartPoint("3.00-3.49", 1),
        ChartPoint("3.50-4.00", 1),
    )
    assert charts.average_gpa_by_major == (
        ChartPoint("Computer Science", 3.5),
        ChartPoint("Business", 2.7),
    )
    assert charts.probation_by_major == (
        ChartPoint("Business", 1),
        ChartPoint("Computer Science", 1),
    )
    assert charts.financial_aid_distribution == (
        ChartPoint("Yes", 2),
        ChartPoint("No", 1),
    )


def test_dashboard_chart_data_handles_null_values(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="1001", MAJR_DESC=None, CLAS_DESC="", CUM_GPA=None, PROBATION=True, FINANCIAL_AID=None),
                StudentCurrent(STUD_ID="1002", MAJR_DESC="Computer Science", CLAS_DESC="Senior", CUM_GPA=4.0, PROBATION=False, FINANCIAL_AID=True),
            ]
        )
        session.commit()

    with session_factory() as session:
        charts = get_dashboard_charts(session)

    assert charts.students_by_major == (
        ChartPoint("Computer Science", 1),
        ChartPoint("Unknown", 1),
    )
    assert charts.students_by_class == (
        ChartPoint("Senior", 1),
        ChartPoint("Unknown", 1),
    )
    assert charts.average_gpa_by_major == (ChartPoint("Computer Science", 4.0),)
    assert charts.probation_by_major == (ChartPoint("Unknown", 1),)
    assert charts.financial_aid_distribution == (
        ChartPoint("Yes", 1),
        ChartPoint("Unknown", 1),
    )


def test_dashboard_chart_data_ordering_is_deterministic(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="1001", MAJR_DESC="B Major", CLAS_DESC="B Class", CUM_GPA=3.0),
                StudentCurrent(STUD_ID="1002", MAJR_DESC="A Major", CLAS_DESC="A Class", CUM_GPA=3.0),
            ]
        )
        session.commit()

    with session_factory() as session:
        charts = get_dashboard_charts(session)

    assert charts.students_by_major == (
        ChartPoint("A Major", 1),
        ChartPoint("B Major", 1),
    )
    assert charts.students_by_class == (
        ChartPoint("A Class", 1),
        ChartPoint("B Class", 1),
    )


def test_dashboard_charts_can_include_or_exclude_missing_students(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="1001", MAJR_DESC="Active Major", CUM_GPA=4.0),
                StudentCurrent(STUD_ID="1002", MAJR_DESC="Missing Major", CUM_GPA=2.0, missing_from_latest_import=True),
            ]
        )
        session.commit()

    with session_factory() as session:
        excluded = get_dashboard_charts(session)
        included = get_dashboard_charts(session, include_missing=True)

    assert excluded.students_by_major == (ChartPoint("Active Major", 1),)
    assert included.students_by_major == (
        ChartPoint("Active Major", 1),
        ChartPoint("Missing Major", 1),
    )


def test_latest_import_summary_with_no_imports(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        summary = get_latest_import_summary(session)

    assert summary is None


def test_latest_import_summary_with_successful_import(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add(
            ImportBatch(
                filename="WSP.xlsx",
                file_path="C:/WSP.xlsx",
                file_hash="hash-1",
                number_of_rows=10,
                number_of_columns=39,
                new_rows=3,
                updated_rows=2,
                unchanged_rows=5,
                missing_rows=1,
                new_columns_detected=["NEW_COLUMN"],
                missing_columns_detected=["OLD_COLUMN"],
                status="completed",
            )
        )
        session.commit()

    with session_factory() as session:
        summary = get_latest_import_summary(session)

    assert summary is not None
    assert summary.filename == "WSP.xlsx"
    assert summary.rows_added == 3
    assert summary.rows_updated == 2
    assert summary.rows_unchanged == 5
    assert summary.rows_missing == 1
    assert summary.new_columns == ("NEW_COLUMN",)
    assert summary.missing_columns == ("OLD_COLUMN",)
    assert summary.status == "completed"
    assert summary.error_message is None
    assert "T" in summary.imported_at


def test_latest_import_summary_with_failed_import(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add_all(
            [
                ImportBatch(filename="old.xlsx", file_path="C:/old.xlsx", file_hash="old", status="completed"),
                ImportBatch(
                    filename="failed.xlsx",
                    file_path="C:/failed.xlsx",
                    file_hash="failed",
                    status="failed",
                    error_message="Bad file",
                ),
            ]
        )
        session.commit()

    with session_factory() as session:
        summary = get_latest_import_summary(session)

    assert summary is not None
    assert summary.filename == "failed.xlsx"
    assert summary.status == "failed"
    assert summary.error_message == "Bad file"


def test_preferred_work_normalization_and_distribution(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="1001", WSP_PREFERRED_TYPE_OF_WORK=" data-analysis "),
                StudentCurrent(STUD_ID="1002", WSP_PREFERRED_TYPE_OF_WORK="Data Analysis"),
                StudentCurrent(STUD_ID="1003", WSP_PREFERRED_TYPE_OF_WORK="Admin / data analysis"),
            ]
        )
        session.commit()

    with session_factory() as session:
        analytics = get_text_and_semantic_analytics(session)

    assert normalize_subjective_term(" data-analysis ") == "Data Analysis"
    assert analytics.preferred_work_distribution == (
        TextFrequencyPoint("Data Analysis", 3, ("Data Analysis", "data analysis", "data-analysis")),
        TextFrequencyPoint("Admin", 1, ("Admin",)),
    )


def test_technical_skills_frequency_splits_and_dedupes_per_student(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="1001", WSP_TECHNICAL_SKILLS="Python, python; Excel / SQL and Excel"),
                StudentCurrent(STUD_ID="1002", WSP_TECHNICAL_SKILLS="python programming; spreadsheets"),
            ]
        )
        session.commit()

    with session_factory() as session:
        analytics = get_text_and_semantic_analytics(session)

    assert split_subjective_terms("Python, Excel and SQL", split_on_and=True) == ("Python", "Excel", "SQL")
    assert analytics.technical_skills_frequency == (
        TextFrequencyPoint("Python", 2, ("Python", "python", "python programming")),
        TextFrequencyPoint("Excel", 1, ("Excel",)),
        TextFrequencyPoint("SQL", 1, ("SQL",)),
        TextFrequencyPoint("Spreadsheets", 1, ("spreadsheets",)),
    )


def test_languages_frequency_combines_written_and_spoken_with_deduping(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(
                    STUD_ID="1001",
                    WSP_WRITTEN_LANGUAGES="English, Arabic",
                    WSP_SPOKEN_LANGUAGES="english / French and Arabic",
                ),
                StudentCurrent(STUD_ID="1002", WSP_SPOKEN_LANGUAGES="English"),
            ]
        )
        session.commit()

    with session_factory() as session:
        analytics = get_text_and_semantic_analytics(session)

    assert analytics.languages_frequency == (
        TextFrequencyPoint("English", 2, ("English", "english")),
        TextFrequencyPoint("Arabic", 1, ("Arabic",)),
        TextFrequencyPoint("French", 1, ("French",)),
    )


def test_text_analytics_can_cluster_similar_terms_with_mocked_semantic_clusterer(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="1001", WSP_TECHNICAL_SKILLS="Excel"),
                StudentCurrent(STUD_ID="1002", WSP_TECHNICAL_SKILLS="spreadsheets"),
            ]
        )
        session.commit()

    def clusterer(category: str, term: str) -> str:
        if category == "technical_skills" and term == "Spreadsheets":
            return "Excel"
        return term

    with session_factory() as session:
        analytics = get_text_and_semantic_analytics(session, term_clusterer=clusterer)

    assert analytics.technical_skills_frequency == (
        TextFrequencyPoint("Excel", 2, ("Excel", "spreadsheets")),
    )


def test_text_analytics_keeps_raw_source_text_and_does_not_mutate_students(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    raw_skills = "  python,   Excel  "

    with session_factory() as session:
        session.add(StudentCurrent(STUD_ID="1001", WSP_TECHNICAL_SKILLS=raw_skills))
        session.commit()

    with session_factory() as session:
        student = session.query(StudentCurrent).filter_by(STUD_ID="1001").one()
        analytics = get_text_and_semantic_analytics(session)

    assert analytics.raw_source_text["WSP_TECHNICAL_SKILLS"] == ("python, Excel",)
    assert student.WSP_TECHNICAL_SKILLS == raw_skills


def test_text_analytics_excludes_missing_students_by_default(tmp_path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add_all(
            [
                StudentCurrent(STUD_ID="1001", WSP_PREFERRED_TYPE_OF_WORK="Research"),
                StudentCurrent(
                    STUD_ID="1002",
                    WSP_PREFERRED_TYPE_OF_WORK="Admin",
                    missing_from_latest_import=True,
                ),
            ]
        )
        session.commit()

    with session_factory() as session:
        excluded = get_text_and_semantic_analytics(session)
        included = get_text_and_semantic_analytics(session, include_missing=True)

    assert excluded.preferred_work_distribution == (TextFrequencyPoint("Research", 1, ("Research",)),)
    assert included.preferred_work_distribution == (
        TextFrequencyPoint("Admin", 1, ("Admin",)),
        TextFrequencyPoint("Research", 1, ("Research",)),
    )
