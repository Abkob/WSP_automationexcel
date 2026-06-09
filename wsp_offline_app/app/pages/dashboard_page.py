from __future__ import annotations

from dataclasses import dataclass

from app.components.chart_card import ChartSpec, render_chart_card
from app.components.import_status_card import render_latest_import_card
from app.components.metric_card import MetricCardData, render_metric_card
from config import AppSettings
from database.db import create_session_factory, create_sqlite_engine, initialize_database
from services.analytics_service import (
    ChartPoint,
    DashboardCharts,
    DashboardMetrics,
    LatestImportSummary,
    TextAndSemanticAnalytics,
    get_dashboard_charts,
    get_dashboard_metrics,
    get_latest_import_summary,
    get_text_and_semantic_analytics,
)


@dataclass(frozen=True)
class DashboardPageData:
    metrics: DashboardMetrics
    charts: DashboardCharts
    text_analytics: TextAndSemanticAnalytics
    latest_import: LatestImportSummary | None


def load_dashboard_page_data(settings: AppSettings) -> DashboardPageData:
    engine = create_sqlite_engine(settings.database_path)
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        return DashboardPageData(
            metrics=get_dashboard_metrics(session),
            charts=get_dashboard_charts(session),
            text_analytics=get_text_and_semantic_analytics(session),
            latest_import=get_latest_import_summary(session),
        )


def build_metric_cards(metrics: DashboardMetrics) -> tuple[MetricCardData, ...]:
    return (
        MetricCardData("Total students", format_count(metrics.total_students), "groups"),
        MetricCardData("New latest", format_count(metrics.new_students_latest_import), "person_add", "positive"),
        MetricCardData("Updated latest", format_count(metrics.updated_students_latest_import), "published_with_changes", "warning"),
        MetricCardData("Average GPA", format_optional_number(metrics.average_gpa), "grade"),
        MetricCardData("Probation", format_count(metrics.probation_count), "report_problem", "negative"),
        MetricCardData("Dean warning", format_count(metrics.dean_warning_count), "warning", "warning"),
        MetricCardData("Financial aid", format_count(metrics.financial_aid_count), "volunteer_activism", "positive"),
        MetricCardData("Dorms", format_count(metrics.dorm_count), "home"),
        MetricCardData("Registered", format_count(metrics.registered_count), "how_to_reg", "positive"),
        MetricCardData("Enrolled", format_count(metrics.enrolled_count), "school", "positive"),
    )


def build_dashboard_chart_specs(charts: DashboardCharts) -> tuple[ChartSpec, ...]:
    return (
        ChartSpec("Students by major", "bar", charts.students_by_major),
        ChartSpec("Students by class", "bar", charts.students_by_class),
        ChartSpec("GPA distribution", "bar", charts.gpa_distribution),
        ChartSpec("Average GPA by major", "bar", charts.average_gpa_by_major),
        ChartSpec("Probation by major", "bar", charts.probation_by_major),
        ChartSpec("Financial aid status", "pie", charts.financial_aid_distribution),
    )


def build_text_analytics_chart_specs(text_analytics: TextAndSemanticAnalytics, *, limit: int = 12) -> tuple[ChartSpec, ...]:
    return (
        ChartSpec(
            "Preferred work themes",
            "bar",
            text_frequency_to_chart_points(text_analytics.preferred_work_distribution, limit=limit),
        ),
        ChartSpec(
            "Technical skills frequency",
            "bar",
            text_frequency_to_chart_points(text_analytics.technical_skills_frequency, limit=limit),
        ),
        ChartSpec(
            "Languages frequency",
            "bar",
            text_frequency_to_chart_points(text_analytics.languages_frequency, limit=limit),
        ),
    )


def text_frequency_to_chart_points(points, *, limit: int) -> tuple[ChartPoint, ...]:
    return tuple(ChartPoint(point.label, point.value) for point in points[:limit])


def format_count(value: int) -> str:
    return f"{value:,}"


def format_optional_number(value: float | None) -> str:
    return "N/A" if value is None else f"{value:.2f}"


def render_dashboard_page(settings: AppSettings) -> None:
    from nicegui import ui

    data = load_dashboard_page_data(settings)

    with ui.row().classes("w-full justify-end"):
        refresh_button = ui.button(icon="refresh", on_click=lambda: ui.run_javascript("location.reload()")).props(
            'flat round aria-label="Refresh dashboard"'
        )
        refresh_button.tooltip("Refresh dashboard")

    with ui.grid(columns="repeat(auto-fit, minmax(180px, 1fr))").classes("w-full gap-3"):
        for metric in build_metric_cards(data.metrics):
            render_metric_card(ui, metric)

    ui.label("Structured overview").classes("text-sm font-semibold text-gray-800 mt-2")
    with ui.grid(columns="repeat(auto-fit, minmax(360px, 1fr))").classes("w-full gap-4"):
        for spec in build_dashboard_chart_specs(data.charts):
            render_chart_card(ui, spec)

    ui.label("Text and semantic overview").classes("text-sm font-semibold text-gray-800 mt-2")
    with ui.grid(columns="repeat(auto-fit, minmax(360px, 1fr))").classes("w-full gap-4"):
        for spec in build_text_analytics_chart_specs(data.text_analytics):
            render_chart_card(ui, spec)

    render_latest_import_card(ui, data.latest_import)
