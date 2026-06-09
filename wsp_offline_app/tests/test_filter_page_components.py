from __future__ import annotations

from datetime import UTC, datetime

from app.components.filter_panel import FilterUiState, build_filter_request_from_state, build_result_summary
from app.components.student_table import (
    build_student_table_rows,
    format_boolean,
    format_optional_float,
    format_semantic_score,
    student_to_table_row,
    truncate_text,
)
from database.models import StudentCurrent
from services.filter_service import FilterResult


def test_filter_state_builds_structured_and_semantic_request() -> None:
    request = build_filter_request_from_state(
        FilterUiState(
            name_query="  sara  ",
            technical_skills_query=" excel reporting ",
            semantic_query="data entry with spreadsheets",
            gpa_min=3.7,
            major="Computer Science",
            class_desc="Senior",
            probation="no",
            financial_aid="yes",
            dorms="any",
            include_missing=True,
            sort_field="CUM_GPA",
            sort_direction="desc",
            page_size=100,
        )
    )

    assert request.numeric_filters[0].field_name == "CUM_GPA"
    assert request.numeric_filters[0].operator == ">="
    assert request.numeric_filters[0].value == 3.7
    assert [(item.field_name, item.value) for item in request.boolean_filters] == [
        ("PROBATION", False),
        ("FINANCIAL_AID", True),
    ]
    assert [(item.field_name, item.values) for item in request.category_filters] == [
        ("MAJR_DESC", ("Computer Science",)),
        ("CLAS_DESC", ("Senior",)),
    ]
    assert [(item.field_name, item.value) for item in request.text_filters] == [
        ("STUD_NAME", "sara"),
        ("WSP_TECHNICAL_SKILLS", "excel reporting"),
    ]
    assert request.semantic_filter is not None
    assert request.semantic_filter.query == "data entry with spreadsheets"
    assert request.include_missing is True
    assert request.sort is not None
    assert request.sort.field_name == "CUM_GPA"
    assert request.sort.direction == "desc"
    assert request.pagination.page_size == 100


def test_filter_state_uses_between_filter_when_gpa_bounds_are_reversed() -> None:
    request = build_filter_request_from_state(FilterUiState(gpa_min=3.9, gpa_max=3.2))

    assert len(request.numeric_filters) == 1
    assert request.numeric_filters[0].operator == "between"
    assert request.numeric_filters[0].value == 3.2
    assert request.numeric_filters[0].value_to == 3.9


def test_result_summary_handles_pluralization() -> None:
    assert build_result_summary(1, 1, 1) == "1 result - 1 visible - 1 filter"
    assert build_result_summary(120, 50, 0) == "120 results - 50 visible - 0 filters"


def test_student_table_formatters_are_readable() -> None:
    assert format_optional_float(None) == ""
    assert format_optional_float(3.456) == "3.46"
    assert format_boolean(True) == "Yes"
    assert format_boolean(False) == "No"
    assert format_boolean(None) == ""
    assert format_semantic_score(0.876) == "0.88"
    assert truncate_text("short", max_length=20) == "short"
    assert truncate_text("a" * 30, max_length=10) == "aaaaaaaaa..."


def test_student_table_row_formats_student_values() -> None:
    student = StudentCurrent(
        STUD_ID="1001",
        STUD_NAME="Test Student",
        MAJR_DESC="Computer Science",
        CLAS_DESC="Senior",
        STUD_EMAIL="student@example.test",
        CUM_GPA=3.8123,
        PROBATION=False,
        FINANCIAL_AID=True,
        DORMS=None,
        WSP_TECHNICAL_SKILLS="Excel, Python, SQL",
        WSP_PREFERRED_TYPE_OF_WORK="I like spreadsheet reporting and careful office data entry.",
        added_to_db_at=datetime(2026, 6, 8, 10, 30, tzinfo=UTC),
        modified_in_db_at=datetime(2026, 6, 9, 11, 45, tzinfo=UTC),
    )

    row = student_to_table_row(student, semantic_score=0.91)

    assert row["STUD_ID"] == "1001"
    assert row["CUM_GPA"] == "3.81"
    assert row["PROBATION"] == "No"
    assert row["FINANCIAL_AID"] == "Yes"
    assert row["DORMS"] == ""
    assert row["added_to_db_at"] == "2026-06-08 10:30"
    assert row["modified_in_db_at"] == "2026-06-09 11:45"
    assert row["semantic_score"] == "0.91"
    assert row["semantic_explanation"] == ""
    assert row["WSP_TECHNICAL_SKILLS"] == "Excel, Python, SQL"


def test_filter_result_rows_convert_to_table_rows_with_semantic_scores() -> None:
    student = StudentCurrent(STUD_ID="1001", STUD_NAME="Ranked Student")
    result = FilterResult(
        rows=(student,),
        selected_rows=(),
        total_count=1,
        page=1,
        page_size=50,
        applied_filter_count=1,
        applied_filter_metadata={},
        semantic_scores={"1001": 0.72},
        semantic_reasons={"1001": "Embedding match 0.72."},
    )

    rows = build_student_table_rows(result)

    assert rows[0]["STUD_ID"] == "1001"
    assert rows[0]["semantic_score"] == "0.72"
    assert rows[0]["semantic_explanation"] == "Embedding match 0.72."
