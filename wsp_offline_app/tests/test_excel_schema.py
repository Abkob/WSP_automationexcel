from __future__ import annotations

from pathlib import Path

import pytest
from openpyxl import Workbook

from services.excel_schema import (
    DuplicateHeaderError,
    EXPECTED_WSP_COLUMNS,
    clean_headers,
    compare_headers,
    find_duplicates,
    normalize_header,
    read_header_row_and_row_count,
    read_workbook_schema,
)


def test_normalize_header_creates_stable_database_safe_name() -> None:
    assert normalize_header(" WSP Technical Skills ") == "WSP_TECHNICAL_SKILLS"
    assert normalize_header("Dean's Warning") == "DEAN_S_WARNING"
    assert normalize_header(None) == ""


def test_clean_headers_trims_normalizes_and_preserves_original_names() -> None:
    result = clean_headers([" STUD ID ", "WSP Technical Skills", None])

    assert result.original_headers == ("STUD ID", "WSP Technical Skills", "")
    assert result.normalized_headers == ("STUD_ID", "WSP_TECHNICAL_SKILLS", "")
    assert result.original_by_normalized == {
        "STUD_ID": "STUD ID",
        "WSP_TECHNICAL_SKILLS": "WSP Technical Skills",
    }


def test_clean_headers_detects_duplicate_headers_after_cleaning() -> None:
    result = clean_headers(["Stud ID", "STUD_ID"], reject_duplicates=False)

    assert result.duplicate_headers == ("STUD_ID",)


def test_clean_headers_rejects_duplicate_headers_by_default() -> None:
    with pytest.raises(DuplicateHeaderError, match="Duplicate headers"):
        clean_headers(["Stud ID", "STUD_ID"])


def test_find_duplicates_preserves_first_duplicate_order() -> None:
    assert find_duplicates(["A", "B", "A", "C", "B", "A"]) == ("A", "B")


def test_compare_headers_matches_expected_columns() -> None:
    comparison = compare_headers(EXPECTED_WSP_COLUMNS)

    assert comparison.matches_expected
    assert comparison.missing_columns == ()
    assert comparison.new_columns == ()
    assert comparison.duplicate_columns == ()


def test_compare_headers_detects_missing_new_and_duplicate_columns() -> None:
    actual = list(EXPECTED_WSP_COLUMNS)
    actual.remove("CUM_GPA")
    actual.append("NEW FUTURE COLUMN")
    actual.append("STUD_ID")

    comparison = compare_headers(actual)

    assert not comparison.matches_expected
    assert comparison.missing_columns == ("CUM_GPA",)
    assert comparison.new_columns == ("NEW_FUTURE_COLUMN",)
    assert comparison.duplicate_columns == ("STUD_ID",)


def test_read_workbook_schema_reads_fixture(sample_workbook_path: Path) -> None:
    schema = read_workbook_schema(sample_workbook_path)

    assert schema.sheet_names == ("Sheet1",)
    assert schema.active_sheet == "Sheet1"
    assert schema.row_count == 2
    assert schema.data_row_count == 1
    assert schema.column_count == len(EXPECTED_WSP_COLUMNS)
    assert schema.headers == EXPECTED_WSP_COLUMNS


def test_read_workbook_schema_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        read_workbook_schema(tmp_path / "missing.xlsx")


def test_read_workbook_schema_rejects_unsupported_extension(tmp_path: Path) -> None:
    path = tmp_path / "not_excel.txt"
    path.write_text("not an excel workbook", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported Excel extension"):
        read_workbook_schema(path)


def test_read_workbook_schema_rejects_missing_sheet(sample_workbook_path: Path) -> None:
    with pytest.raises(ValueError, match="was not found"):
        read_workbook_schema(sample_workbook_path, sheet_name="Missing")


def test_user_added_wsp_workbook_matches_initial_column_contract() -> None:
    workbook_path = Path(__file__).resolve().parents[2] / "WSP.xlsx"
    if not workbook_path.exists():
        pytest.skip("User workbook has not been added yet.")

    schema = read_workbook_schema(workbook_path)
    comparison = compare_headers(schema.headers)

    assert schema.sheet_names == ("Sheet1",)
    assert schema.column_count == len(EXPECTED_WSP_COLUMNS)
    assert comparison.matches_expected


def test_duplicate_headers_can_be_seen_after_normalization(tmp_path: Path) -> None:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["Stud ID", "STUD_ID"])
    path = tmp_path / "duplicate_headers.xlsx"
    workbook.save(path)

    schema = read_workbook_schema(path)
    comparison = compare_headers(schema.headers)

    assert comparison.duplicate_columns == ("STUD_ID",)


class WorksheetWithoutDimensionMetadata:
    max_column = None
    max_row = None

    def __init__(self, rows: list[tuple[object, ...]]) -> None:
        self.rows = rows

    def iter_rows(self, values_only: bool = True):
        assert values_only is True
        return iter(self.rows)


def test_schema_reader_header_fallback_handles_missing_dimension_metadata() -> None:
    worksheet = WorksheetWithoutDimensionMetadata(
        [
            ("STUD_ID", "STUD_NAME", "CUM_GPA"),
            ("1001", "Student", 3.5),
            ("1002", "Student Two", 3.8),
        ]
    )

    headers, row_count = read_header_row_and_row_count(worksheet)

    assert headers == ("STUD_ID", "STUD_NAME", "CUM_GPA")
    assert row_count == 3
