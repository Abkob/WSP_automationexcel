from __future__ import annotations

import re
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Font
from sqlalchemy.orm import Session

from services.filter_service import FilterResult, log_filter_export


DEFAULT_EXPORT_COLUMNS = (
    "STUD_ID",
    "STUD_NAME",
    "MAJR_DESC",
    "CLAS_DESC",
    "STUD_EMAIL",
    "CUM_GPA",
    "added_to_db_at",
    "modified_in_db_at",
    "PROBATION",
    "FINANCIAL_AID",
    "DORMS",
    "WSP_TECHNICAL_SKILLS",
    "WSP_PREFERRED_TYPE_OF_WORK",
)


@dataclass(frozen=True)
class ExcelExportResult:
    path: Path
    row_count: int
    column_names: tuple[str, ...]
    export_log_id: int | None = None


def safe_export_filename_part(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    cleaned = re.sub(r"_+", "_", cleaned)
    return cleaned.strip("._") or "filtered_results"


def build_export_filename(prefix: str, exported_at: datetime) -> str:
    timestamp = exported_at.strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{safe_export_filename_part(prefix)}.xlsx"


def export_filtered_results_to_excel(
    filter_result: FilterResult,
    export_dir: Path | str,
    *,
    filename_prefix: str = "filtered_results",
    exported_at: datetime | None = None,
    app_version: str = "0.1.0",
    session: Session | None = None,
    filter_run_id: int | None = None,
) -> ExcelExportResult:
    if (session is None) != (filter_run_id is None):
        raise ValueError("session and filter_run_id must be provided together for export logging")

    destination_dir = Path(export_dir).resolve()
    destination_dir.mkdir(parents=True, exist_ok=True)
    resolved_exported_at = exported_at or datetime.now(UTC)
    export_path = destination_dir / build_export_filename(filename_prefix, resolved_exported_at)

    rows = build_export_rows(filter_result)
    column_names = tuple(rows[0].keys()) if rows else DEFAULT_EXPORT_COLUMNS

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Filtered Results"
    worksheet.freeze_panes = "A2"

    worksheet.append(list(column_names))
    for cell in worksheet[1]:
        cell.font = Font(bold=True)

    for row in rows:
        worksheet.append([row.get(column_name) for column_name in column_names])

    worksheet.auto_filter.ref = worksheet.dimensions
    add_filter_metadata_sheet(workbook, filter_result, exported_at=resolved_exported_at, app_version=app_version)
    workbook.save(export_path)
    export_log_id = None

    if session is not None and filter_run_id is not None:
        export_log = log_filter_export(
            session,
            filter_run_id=filter_run_id,
            export_path=str(export_path),
            row_count=len(rows),
        )
        export_log_id = export_log.export_id

    return ExcelExportResult(
        path=export_path,
        row_count=len(rows),
        column_names=column_names,
        export_log_id=export_log_id,
    )


def build_export_rows(filter_result: FilterResult) -> tuple[dict[str, Any], ...]:
    if filter_result.selected_rows:
        return filter_result.selected_rows

    rows: list[dict[str, Any]] = []
    for student in filter_result.rows:
        row = {
            column_name: getattr(student, column_name)
            for column_name in DEFAULT_EXPORT_COLUMNS
        }
        if filter_result.semantic_scores:
            row["semantic_score"] = filter_result.semantic_scores.get(student.STUD_ID)
        if filter_result.semantic_reasons:
            row["semantic_explanation"] = filter_result.semantic_reasons.get(student.STUD_ID)
        rows.append(row)
    return tuple(rows)


def add_filter_metadata_sheet(
    workbook: Workbook,
    filter_result: FilterResult,
    *,
    exported_at: datetime,
    app_version: str,
) -> None:
    worksheet = workbook.create_sheet("Filter Metadata")
    worksheet.append(["key", "value"])
    for cell in worksheet[1]:
        cell.font = Font(bold=True)

    metadata = {
        "filter_json": json.dumps(filter_result.applied_filter_metadata, sort_keys=True, default=str),
        "export_timestamp": exported_at.isoformat(),
        "number_of_rows": len(build_export_rows(filter_result)),
        "source_batch_ids": ",".join(str(batch_id) for batch_id in collect_source_batch_ids(filter_result)),
        "app_version": app_version,
    }

    for key, value in metadata.items():
        worksheet.append([key, value])


def collect_source_batch_ids(filter_result: FilterResult) -> tuple[int, ...]:
    batch_ids = {
        student.last_seen_batch_id
        for student in filter_result.rows
        if student.last_seen_batch_id is not None
    }
    return tuple(sorted(batch_ids))
