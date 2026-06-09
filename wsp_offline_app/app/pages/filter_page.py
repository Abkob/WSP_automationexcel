from __future__ import annotations

from dataclasses import dataclass, replace

from app.components.filter_panel import (
    BOOLEAN_SELECT_OPTIONS,
    PAGE_SIZE_OPTIONS,
    SORT_DIRECTION_OPTIONS,
    SORT_FIELD_OPTIONS,
    FilterOptionSet,
    FilterUiState,
    build_filter_request_from_state,
    build_result_summary,
)
from app.components.student_table import build_student_table_rows, render_student_results_table
from config import AppSettings
from database.db import create_session_factory, create_sqlite_engine, initialize_database
from database.models import StudentCurrent
from services.export_service import export_filtered_results_to_excel
from services.filter_service import FilterRequest, FilterResult, PaginationSpec, execute_filter_request, log_filter_run


@dataclass(frozen=True)
class FilterPageData:
    options: FilterOptionSet
    request: FilterRequest
    result: FilterResult


def load_filter_page_data(settings: AppSettings) -> FilterPageData:
    request = build_filter_request_from_state(FilterUiState())
    result = execute_filter_for_settings(settings, request)
    options = load_filter_options(settings)
    return FilterPageData(options=options, request=request, result=result)


def execute_filter_for_settings(settings: AppSettings, request: FilterRequest, *, log_run: bool = False) -> FilterResult:
    engine = create_sqlite_engine(settings.database_path)
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        result = execute_filter_request(session, request)
        if log_run:
            log_filter_run(session, request=request, result_count=result.total_count)
            session.commit()
        return result


def load_filter_options(settings: AppSettings) -> FilterOptionSet:
    engine = create_sqlite_engine(settings.database_path)
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        return FilterOptionSet(
            majors=load_distinct_text_options(session, "MAJR_DESC"),
            classes=load_distinct_text_options(session, "CLAS_DESC"),
        )


def load_distinct_text_options(session, field_name: str, *, limit: int = 200) -> tuple[str, ...]:
    column = getattr(StudentCurrent, field_name)
    values = (
        session.query(column)
        .filter(column.is_not(None), column != "")
        .distinct()
        .order_by(column.asc())
        .limit(limit)
        .all()
    )
    return tuple(value for (value,) in values if value)


def export_filter_result(settings: AppSettings, request: FilterRequest):
    export_request = replace(request, pagination=PaginationSpec(page=1, page_size=500))
    engine = create_sqlite_engine(settings.database_path)
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    with session_factory() as session:
        result = execute_filter_request(session, export_request)
        filter_run = log_filter_run(session, request=export_request, result_count=result.total_count)
        export_result = export_filtered_results_to_excel(
            result,
            settings.export_dir,
            filename_prefix="filtered_students",
            session=session,
            filter_run_id=filter_run.filter_run_id,
        )
        session.commit()
        return export_result


def render_filter_page(settings: AppSettings) -> None:
    from nicegui import ui

    data = load_filter_page_data(settings)
    current_state = {
        "request": data.request,
        "result": data.result,
    }

    with ui.grid(columns="minmax(300px, 420px) minmax(0, 1fr)").classes("w-full gap-4 items-start"):
        with ui.card().classes("rounded-md shadow-sm border border-gray-100 p-4 w-full gap-4"):
            with ui.row().classes("w-full items-center gap-2"):
                ui.icon("filter_alt").classes("text-primary text-xl")
                ui.label("Structured filters").classes("text-sm font-semibold text-gray-800")

            with ui.grid(columns="repeat(2, minmax(0, 1fr))").classes("w-full gap-3"):
                gpa_min_input = ui.number("Minimum GPA", value=None, min=0, max=4, step=0.05).props("outlined dense clearable")
                gpa_max_input = ui.number("Maximum GPA", value=None, min=0, max=4, step=0.05).props("outlined dense clearable")

            major_select = ui.select(list(data.options.majors), value=None, label="Major").props("outlined dense clearable use-input")
            class_select = ui.select(list(data.options.classes), value=None, label="Class").props("outlined dense clearable use-input")
            name_input = ui.input("Name contains", value="").props("outlined dense clearable")
            skills_input = ui.input("Technical skills contain", value="").props("outlined dense clearable")

            with ui.grid(columns="repeat(3, minmax(0, 1fr))").classes("w-full gap-3"):
                probation_select = ui.select(BOOLEAN_SELECT_OPTIONS, value="any", label="Probation").props("outlined dense")
                financial_aid_select = ui.select(BOOLEAN_SELECT_OPTIONS, value="any", label="Aid").props("outlined dense")
                dorms_select = ui.select(BOOLEAN_SELECT_OPTIONS, value="any", label="Dorms").props("outlined dense")

            with ui.row().classes("w-full items-center gap-2"):
                include_missing_checkbox = ui.checkbox("Include missing", value=False)

            with ui.row().classes("w-full items-center gap-2"):
                ui.icon("travel_explore").classes("text-primary text-xl")
                ui.label("Semantic match").classes("text-sm font-semibold text-gray-800")

            semantic_input = ui.textarea(
                "Semantic query",
                value="",
                placeholder="spreadsheet reporting with careful data entry",
            ).props("outlined dense clearable autogrow")

            with ui.grid(columns="repeat(2, minmax(0, 1fr))").classes("w-full gap-3"):
                sort_field_select = ui.select(SORT_FIELD_OPTIONS, value="STUD_ID", label="Sort by").props("outlined dense")
                sort_direction_select = ui.select(SORT_DIRECTION_OPTIONS, value="asc", label="Order").props("outlined dense")

            page_size_select = ui.select(PAGE_SIZE_OPTIONS, value=50, label="Rows per page").props("outlined dense")

            with ui.row().classes("w-full items-center gap-2 pt-1"):
                apply_button = ui.button("Apply", icon="filter_alt").props('unelevated aria-label="Apply filters"')
                clear_button = ui.button("Clear", icon="restart_alt").props('flat aria-label="Clear filters"')
                export_button = ui.button("Export", icon="file_download").props('flat aria-label="Export filtered rows"')

        with ui.card().classes("rounded-md shadow-sm border border-gray-100 p-4 w-full gap-3"):
            with ui.row().classes("w-full items-center justify-between gap-3"):
                with ui.column().classes("gap-1"):
                    ui.label("Results").classes("text-sm font-semibold text-gray-800")
                    result_summary_label = ui.label(
                        build_result_summary(
                            data.result.total_count,
                            len(data.result.rows),
                            data.result.applied_filter_count,
                        )
                    ).classes("text-xs text-gray-600")
                refresh_button = ui.button(icon="refresh").props('flat round aria-label="Refresh results"')
                refresh_button.tooltip("Refresh results")

            table = render_student_results_table(ui, build_student_table_rows(data.result))
            export_status_label = ui.label("").classes("text-xs text-gray-600 break-all")

    def collect_state() -> FilterUiState:
        return FilterUiState(
            name_query=name_input.value or "",
            technical_skills_query=skills_input.value or "",
            semantic_query=semantic_input.value or "",
            gpa_min=optional_float(gpa_min_input.value),
            gpa_max=optional_float(gpa_max_input.value),
            major=major_select.value,
            class_desc=class_select.value,
            probation=probation_select.value or "any",
            financial_aid=financial_aid_select.value or "any",
            dorms=dorms_select.value or "any",
            include_missing=bool(include_missing_checkbox.value),
            sort_field=sort_field_select.value or "STUD_ID",
            sort_direction=sort_direction_select.value or "asc",
            page_size=int(page_size_select.value or 50),
        )

    def update_results(result: FilterResult, request: FilterRequest) -> None:
        current_state["request"] = request
        current_state["result"] = result
        table.rows = build_student_table_rows(result)
        table.update()
        result_summary_label.set_text(
            build_result_summary(result.total_count, len(result.rows), result.applied_filter_count)
        )

    def apply_filters() -> None:
        request = build_filter_request_from_state(collect_state())
        try:
            result = execute_filter_for_settings(settings, request, log_run=True)
        except Exception as exc:
            ui.notify(f"Filter failed: {exc}", type="negative")
            return
        update_results(result, request)
        export_status_label.set_text("")

    def clear_filters() -> None:
        gpa_min_input.value = None
        gpa_max_input.value = None
        major_select.value = None
        class_select.value = None
        name_input.value = ""
        skills_input.value = ""
        semantic_input.value = ""
        probation_select.value = "any"
        financial_aid_select.value = "any"
        dorms_select.value = "any"
        include_missing_checkbox.value = False
        sort_field_select.value = "STUD_ID"
        sort_direction_select.value = "asc"
        page_size_select.value = 50
        request = build_filter_request_from_state(FilterUiState())
        result = execute_filter_for_settings(settings, request)
        update_results(result, request)
        export_status_label.set_text("")

    def refresh_results() -> None:
        request = current_state["request"]
        result = execute_filter_for_settings(settings, request)
        update_results(result, request)

    def export_results() -> None:
        try:
            export_result = export_filter_result(settings, current_state["request"])
        except Exception as exc:
            ui.notify(f"Export failed: {exc}", type="negative")
            return
        export_status_label.set_text(f"Exported {export_result.row_count:,} rows to {export_result.path}")
        ui.notify("Export complete", type="positive")

    apply_button.on("click", apply_filters)
    clear_button.on("click", clear_filters)
    refresh_button.on("click", refresh_results)
    export_button.on("click", export_results)


def optional_float(value: object) -> float | None:
    if value in (None, ""):
        return None
    return float(value)
