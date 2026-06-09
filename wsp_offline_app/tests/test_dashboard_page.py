from __future__ import annotations

from config import AppSettings
from database.db import create_session_factory, create_sqlite_engine, initialize_database
from database.models import ImportBatch, StudentCurrent
from services.analytics_service import ChartPoint, DashboardCharts, DashboardMetrics, LatestImportSummary, TextAndSemanticAnalytics, TextFrequencyPoint
from app.components.chart_card import ChartSpec, build_bar_figure, build_chart_alt_text, build_pie_figure
from app.components.import_status_card import build_latest_import_rows
from app.components.metric_card import MetricCardData
from app.pages.dashboard_page import (
    build_dashboard_chart_specs,
    build_metric_cards,
    build_text_analytics_chart_specs,
    format_count,
    format_optional_number,
    load_dashboard_page_data,
)


def test_dashboard_formatters() -> None:
    assert format_count(1200) == "1,200"
    assert format_optional_number(None) == "N/A"
    assert format_optional_number(3.456) == "3.46"


def test_dashboard_metric_cards_are_built_from_metrics() -> None:
    metrics = DashboardMetrics(
        total_students=12,
        new_students_latest_import=3,
        updated_students_latest_import=2,
        average_gpa=3.42,
        probation_count=1,
        dean_warning_count=4,
        financial_aid_count=5,
        dorm_count=6,
        registered_count=7,
        enrolled_count=8,
    )

    cards = build_metric_cards(metrics)

    assert len(cards) == 10
    assert cards[0] == MetricCardData("Total students", "12", "groups")
    assert cards[3].label == "Average GPA"
    assert cards[3].value == "3.42"
    assert cards[4].tone == "negative"


def test_dashboard_chart_specs_are_built_from_chart_data() -> None:
    charts = DashboardCharts(
        students_by_major=(ChartPoint("CS", 2),),
        students_by_class=(ChartPoint("Senior", 1),),
        gpa_distribution=(ChartPoint("3.50-4.00", 1),),
        average_gpa_by_major=(ChartPoint("CS", 3.7),),
        probation_by_major=(ChartPoint("Business", 1),),
        financial_aid_distribution=(ChartPoint("Yes", 2),),
    )

    specs = build_dashboard_chart_specs(charts)

    assert specs[0] == ChartSpec("Students by major", "bar", (ChartPoint("CS", 2),))
    assert specs[-1].chart_type == "pie"
    assert specs[-1].points == (ChartPoint("Yes", 2),)


def test_plotly_figures_preserve_data_and_title_metadata() -> None:
    points = (ChartPoint("A", 2), ChartPoint("B", 1))

    bar = build_bar_figure(points, title="Bar Chart")
    pie = build_pie_figure(points, title="Pie Chart")

    assert list(bar.data[0].x) == [2, 1]
    assert list(bar.data[0].y) == ["A", "B"]
    assert bar.data[0].orientation == "h"
    assert bar.layout.meta == {"title": "Bar Chart"}
    assert list(pie.data[0].labels) == ["A", "B"]
    assert list(pie.data[0].values) == [2, 1]
    assert pie.layout.meta == {"title": "Pie Chart"}


def test_chart_alt_text_summarizes_points_for_accessibility() -> None:
    spec = ChartSpec("Skills", "bar", tuple(ChartPoint(f"Item {index}", index) for index in range(1, 7)))

    assert build_chart_alt_text(spec) == "Skills: Item 1 1, Item 2 2, Item 3 3, Item 4 4, Item 5 5, and 1 more."


def test_text_analytics_chart_specs_limit_subjective_terms() -> None:
    analytics = TextAndSemanticAnalytics(
        preferred_work_distribution=tuple(TextFrequencyPoint(f"Work {index}", index) for index in range(5)),
        technical_skills_frequency=(TextFrequencyPoint("Excel", 4), TextFrequencyPoint("Python", 3)),
        languages_frequency=(TextFrequencyPoint("English", 5),),
        raw_source_text={},
    )

    specs = build_text_analytics_chart_specs(analytics, limit=2)

    assert specs[0].title == "Preferred work themes"
    assert specs[0].points == (ChartPoint("Work 0", 0), ChartPoint("Work 1", 1))
    assert specs[1].title == "Technical skills frequency"
    assert specs[2].points == (ChartPoint("English", 5),)


def test_latest_import_rows_for_empty_and_successful_import() -> None:
    assert build_latest_import_rows(None) == [{"item": "Status", "value": "No imports yet"}]

    summary = LatestImportSummary(
        filename="WSP.xlsx",
        imported_at="2026-06-04T12:00:00+00:00",
        rows_added=3,
        rows_updated=2,
        rows_unchanged=1,
        rows_missing=4,
        new_columns=("NEW",),
        missing_columns=("OLD",),
        status="completed",
        error_message=None,
    )

    rows = build_latest_import_rows(summary)

    assert rows[0] == {"item": "File", "value": "WSP.xlsx"}
    assert {"item": "New columns", "value": 1} in rows
    assert {"item": "Missing columns", "value": 1} in rows


def test_load_dashboard_page_data_creates_empty_database(tmp_path) -> None:
    settings = AppSettings(data_dir=tmp_path / "data", runtime_mode="testing")

    data = load_dashboard_page_data(settings)

    assert settings.database_path.exists()
    assert data.metrics.total_students == 0
    assert data.latest_import is None
    assert data.charts.gpa_distribution


def test_load_dashboard_page_data_reads_seeded_database(tmp_path) -> None:
    settings = AppSettings(data_dir=tmp_path / "data", runtime_mode="testing")
    engine = create_sqlite_engine(settings.database_path)
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add(ImportBatch(filename="WSP.xlsx", file_path="C:/WSP.xlsx", file_hash="hash-1", new_rows=1, status="completed"))
        session.add(StudentCurrent(STUD_ID="1001", MAJR_DESC="Computer Science", CLAS_DESC="Senior", CUM_GPA=3.8))
        session.commit()

    data = load_dashboard_page_data(settings)

    assert data.metrics.total_students == 1
    assert data.metrics.average_gpa == 3.8
    assert data.charts.students_by_major == (ChartPoint("Computer Science", 1),)
    assert data.latest_import is not None
    assert data.latest_import.filename == "WSP.xlsx"
