from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable, Mapping

from sqlalchemy.orm import Session

from database.models import ColumnRegistry
from services.excel_schema import normalize_header


@dataclass(frozen=True)
class ColumnTypeChange:
    column_name: str
    previous_type: str
    detected_type: str


@dataclass(frozen=True)
class SchemaSyncResult:
    active_columns: tuple[str, ...]
    new_columns: tuple[str, ...]
    repeated_columns: tuple[str, ...]
    missing_columns: tuple[str, ...]
    type_changes: tuple[ColumnTypeChange, ...]


def infer_column_type(values: Iterable[object]) -> str:
    non_empty_values = [value for value in values if value not in (None, "")]

    if not non_empty_values:
        return "empty"

    if all(isinstance(value, bool) for value in non_empty_values):
        return "boolean"

    if all(isinstance(value, int | float) and not isinstance(value, bool) for value in non_empty_values):
        return "number"

    if all(isinstance(value, date | datetime) for value in non_empty_values):
        return "date"

    return "text"


def sync_column_registry(
    session: Session,
    columns: Iterable[object],
    *,
    batch_id: int | None,
    inferred_types: Mapping[str, str] | None = None,
    original_names: Mapping[str, str] | None = None,
) -> SchemaSyncResult:
    inferred_types = inferred_types or {}
    original_names = original_names or {}
    active_columns = tuple(column for column in (normalize_header(value) for value in columns) if column)
    active_column_set = set(active_columns)

    existing_rows = {
        row.column_name: row
        for row in session.query(ColumnRegistry).all()
    }

    new_columns: list[str] = []
    repeated_columns: list[str] = []
    type_changes: list[ColumnTypeChange] = []

    for column_name in active_columns:
        detected_type = inferred_types.get(column_name, "text")
        original_name = original_names.get(column_name, column_name)

        if column_name in existing_rows:
            row = existing_rows[column_name]
            row.last_seen_batch_id = batch_id
            row.is_active = True
            row.is_new_column = False
            if row.detected_type == "empty" and detected_type != "empty":
                row.detected_type = detected_type
            elif row.detected_type != detected_type and detected_type != "empty":
                type_changes.append(
                    ColumnTypeChange(
                        column_name=column_name,
                        previous_type=row.detected_type,
                        detected_type=detected_type,
                    )
                )
                row.notes = _append_note(
                    row.notes,
                    f"Type changed from {row.detected_type} to {detected_type} in batch {batch_id}.",
                )
                row.detected_type = detected_type
            repeated_columns.append(column_name)
            continue

        session.add(
            ColumnRegistry(
                column_name=column_name,
                original_column_name=original_name,
                detected_type=detected_type,
                first_seen_batch_id=batch_id,
                last_seen_batch_id=batch_id,
                is_active=True,
                is_new_column=True,
            )
        )
        new_columns.append(column_name)

    missing_columns: list[str] = []
    for column_name, row in existing_rows.items():
        if column_name not in active_column_set:
            row.is_active = False
            row.is_new_column = False
            missing_columns.append(column_name)

    return SchemaSyncResult(
        active_columns=active_columns,
        new_columns=tuple(new_columns),
        repeated_columns=tuple(repeated_columns),
        missing_columns=tuple(missing_columns),
        type_changes=tuple(type_changes),
    )


def _append_note(existing_notes: str | None, new_note: str) -> str:
    if not existing_notes:
        return new_note
    return f"{existing_notes}\n{new_note}"
