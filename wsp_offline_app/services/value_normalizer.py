from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any


TRUE_VALUES = {"1", "Y", "YES", "TRUE", "T"}
FALSE_VALUES = {"0", "N", "NO", "FALSE", "F"}


@dataclass(frozen=True)
class NormalizationWarning:
    column_name: str
    raw_value: object
    message: str
    row_number: int | None = None


def is_empty_value(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def add_warning(
    warnings: list[NormalizationWarning] | None,
    *,
    column_name: str,
    raw_value: object,
    message: str,
    row_number: int | None = None,
) -> None:
    if warnings is not None:
        warnings.append(
            NormalizationWarning(
                column_name=column_name,
                raw_value=raw_value,
                message=message,
                row_number=row_number,
            )
        )


def normalize_text(value: object) -> str | None:
    if is_empty_value(value):
        return None
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    return text or None


def normalize_boolean(
    value: object,
    *,
    column_name: str = "",
    row_number: int | None = None,
    warnings: list[NormalizationWarning] | None = None,
) -> bool | None:
    if is_empty_value(value):
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, int | float) and not isinstance(value, bool):
        if value == 1:
            return True
        if value == 0:
            return False

    normalized = normalize_text(value)
    normalized_upper = normalized.upper() if normalized else ""

    if normalized_upper in TRUE_VALUES:
        return True
    if normalized_upper in FALSE_VALUES:
        return False

    add_warning(
        warnings,
        column_name=column_name,
        raw_value=value,
        message="Invalid boolean value",
        row_number=row_number,
    )
    return None


def normalize_number(
    value: object,
    *,
    column_name: str = "",
    row_number: int | None = None,
    warnings: list[NormalizationWarning] | None = None,
) -> float | None:
    if is_empty_value(value):
        return None

    if isinstance(value, bool):
        add_warning(
            warnings,
            column_name=column_name,
            raw_value=value,
            message="Boolean is not valid numeric input",
            row_number=row_number,
        )
        return None

    if isinstance(value, int | float):
        return float(value)

    normalized = normalize_text(value)
    if normalized is None:
        return None

    try:
        return float(normalized.replace(",", ""))
    except ValueError:
        add_warning(
            warnings,
            column_name=column_name,
            raw_value=value,
            message="Invalid numeric value",
            row_number=row_number,
        )
        return None


def normalize_date(value: object, *, column_name: str = "", row_number: int | None = None, warnings: list[NormalizationWarning] | None = None) -> str | None:
    if is_empty_value(value):
        return None

    if isinstance(value, datetime):
        return value.date().isoformat()

    if isinstance(value, date):
        return value.isoformat()

    normalized = normalize_text(value)
    if normalized is None:
        return None

    for date_format in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(normalized, date_format).date().isoformat()
        except ValueError:
            continue

    add_warning(
        warnings,
        column_name=column_name,
        raw_value=value,
        message="Invalid date value",
        row_number=row_number,
    )
    return None


def normalize_email(value: object) -> str | None:
    text = normalize_text(value)
    return text.lower() if text else None


def normalize_phone_text(value: object) -> str | None:
    text = normalize_text(value)
    if text is None:
        return None
    if text.endswith(".0") and text[:-2].isdigit():
        return text[:-2]
    return text
