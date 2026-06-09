from __future__ import annotations

from datetime import date, datetime

from services.value_normalizer import (
    NormalizationWarning,
    is_empty_value,
    normalize_boolean,
    normalize_date,
    normalize_email,
    normalize_number,
    normalize_phone_text,
    normalize_text,
)


def test_empty_values_are_detected() -> None:
    assert is_empty_value(None)
    assert is_empty_value("")
    assert is_empty_value("  ")
    assert not is_empty_value("0")


def test_supported_boolean_values_are_normalized() -> None:
    for value in ("Y", "Yes", "TRUE", "1", "t", 1, True):
        assert normalize_boolean(value) is True

    for value in ("N", "No", "FALSE", "0", "f", 0, False):
        assert normalize_boolean(value) is False

    assert normalize_boolean("") is None


def test_invalid_boolean_value_is_logged_as_warning() -> None:
    warnings: list[NormalizationWarning] = []

    result = normalize_boolean("maybe", column_name="PROBATION", row_number=4, warnings=warnings)

    assert result is None
    assert warnings == [
        NormalizationWarning(
            column_name="PROBATION",
            raw_value="maybe",
            message="Invalid boolean value",
            row_number=4,
        )
    ]


def test_numeric_values_are_normalized() -> None:
    assert normalize_number(3) == 3.0
    assert normalize_number(3.25) == 3.25
    assert normalize_number("1,234.5") == 1234.5
    assert normalize_number("") is None


def test_invalid_numeric_value_is_logged() -> None:
    warnings: list[NormalizationWarning] = []

    result = normalize_number("not a number", column_name="CUM_GPA", row_number=2, warnings=warnings)

    assert result is None
    assert warnings[0].message == "Invalid numeric value"
    assert warnings[0].column_name == "CUM_GPA"


def test_boolean_is_not_accepted_as_number() -> None:
    warnings: list[NormalizationWarning] = []

    assert normalize_number(True, column_name="CUM_GPA", warnings=warnings) is None
    assert warnings[0].message == "Boolean is not valid numeric input"


def test_dates_are_normalized_to_iso_strings() -> None:
    assert normalize_date(date(2026, 6, 4)) == "2026-06-04"
    assert normalize_date(datetime(2026, 6, 4, 10, 30)) == "2026-06-04"
    assert normalize_date("2026-06-04") == "2026-06-04"
    assert normalize_date("06/04/2026") == "2026-06-04"


def test_invalid_date_is_logged() -> None:
    warnings: list[NormalizationWarning] = []

    assert normalize_date("not a date", column_name="APPLICATION_DATE", warnings=warnings) is None
    assert warnings[0].message == "Invalid date value"


def test_text_whitespace_is_normalized() -> None:
    assert normalize_text("  Python   and \n Excel  ") == "Python and Excel"
    assert normalize_text("   ") is None


def test_email_is_lowercased() -> None:
    assert normalize_email(" STUDENT@EXAMPLE.COM ") == "student@example.com"


def test_phone_number_is_preserved_as_text() -> None:
    assert normalize_phone_text(70123456) == "70123456"
    assert normalize_phone_text("70123456.0") == "70123456"
    assert normalize_phone_text("+961 70 123 456") == "+961 70 123 456"
