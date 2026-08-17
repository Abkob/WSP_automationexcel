from __future__ import annotations

from typing import Any

from database.models import StudentCurrent
from services.filter_service import FilterResult


STUDENT_TABLE_COLUMNS = (
    {"name": "STUD_ID", "label": "ID", "field": "STUD_ID", "align": "left", "sortable": True},
    {"name": "STUD_NAME", "label": "Name", "field": "STUD_NAME", "align": "left", "sortable": True},
    {"name": "MAJR_DESC", "label": "Major", "field": "MAJR_DESC", "align": "left", "sortable": True},
    {"name": "CLAS_DESC", "label": "Class", "field": "CLAS_DESC", "align": "left", "sortable": True},
    {"name": "CUM_GPA", "label": "GPA", "field": "CUM_GPA", "align": "right", "sortable": True},
    {"name": "added_to_db_at", "label": "Added", "field": "added_to_db_at", "align": "left", "sortable": True},
    {"name": "modified_in_db_at", "label": "Modified", "field": "modified_in_db_at", "align": "left", "sortable": True},
    {"name": "PROBATION", "label": "Probation", "field": "PROBATION", "align": "left", "sortable": True},
    {"name": "FINANCIAL_AID", "label": "Aid", "field": "FINANCIAL_AID", "align": "left", "sortable": True},
    {"name": "DORMS", "label": "Dorms", "field": "DORMS", "align": "left", "sortable": True},
    {"name": "semantic_score", "label": "Match", "field": "semantic_score", "align": "right", "sortable": True},
    {"name": "WSP_TECHNICAL_SKILLS", "label": "Technical skills", "field": "WSP_TECHNICAL_SKILLS", "align": "left"},
    {"name": "WSP_PREFERRED_TYPE_OF_WORK", "label": "Preferred work", "field": "WSP_PREFERRED_TYPE_OF_WORK", "align": "left"},
)


def build_student_table_rows(filter_result: FilterResult) -> list[dict[str, Any]]:
    return [
        student_to_table_row(
            student,
            semantic_score=filter_result.semantic_scores.get(student.STUD_ID),
            semantic_reason=filter_result.semantic_reasons.get(student.STUD_ID),
        )
        for student in filter_result.rows
    ]


def student_to_table_row(
    student: StudentCurrent,
    *,
    semantic_score: float | None = None,
    semantic_reason: str | None = None,
) -> dict[str, Any]:
    return {
        "STUD_ID": student.STUD_ID,
        "STUD_NAME": display_text(student.STUD_NAME),
        "MAJR_DESC": display_text(student.MAJR_DESC),
        "CLAS_DESC": display_text(student.CLAS_DESC),
        "STUD_EMAIL": display_text(student.STUD_EMAIL),
        "CUM_GPA": format_optional_float(student.CUM_GPA),
        "added_to_db_at": format_audit_datetime(student.added_to_db_at),
        "modified_in_db_at": format_audit_datetime(student.modified_in_db_at),
        "PROBATION": format_boolean(student.PROBATION),
        "FINANCIAL_AID": format_boolean(student.FINANCIAL_AID),
        "DORMS": format_boolean(student.DORMS),
        "semantic_score": format_semantic_score(semantic_score),
        "semantic_explanation": truncate_text(semantic_reason, max_length=360),
        "WSP_TECHNICAL_SKILLS": truncate_text(student.WSP_TECHNICAL_SKILLS, max_length=140),
        "WSP_PREFERRED_TYPE_OF_WORK": truncate_text(student.WSP_PREFERRED_TYPE_OF_WORK, max_length=140),
    }


def display_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return text


def format_optional_float(value: float | None) -> str:
    return "" if value is None else f"{value:.2f}"


def format_boolean(value: bool | None) -> str:
    if value is True:
        return "Yes"
    if value is False:
        return "No"
    return ""


def format_semantic_score(value: float | None) -> str:
    return "" if value is None else f"{value:.2f}"


def format_audit_datetime(value: object) -> str:
    if value is None:
        return ""
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d %H:%M")
    return display_text(value)


def truncate_text(value: object, *, max_length: int) -> str:
    text = display_text(value)
    if len(text) <= max_length:
        return text
    return f"{text[: max_length - 1].rstrip()}..."


def render_student_results_table(ui_module, rows: list[dict[str, Any]]):
    table = ui_module.table(
        columns=list(STUDENT_TABLE_COLUMNS),
        rows=rows,
        row_key="STUD_ID",
        pagination={"rowsPerPage": 15},
    ).classes("w-full wsp-results-table")
    table.props("flat bordered dense wrap-cells")
    return table
