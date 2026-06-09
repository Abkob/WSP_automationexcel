from __future__ import annotations

from services.analytics_service import LatestImportSummary


def build_latest_import_rows(summary: LatestImportSummary | None) -> list[dict[str, str | int]]:
    if summary is None:
        return [{"item": "Status", "value": "No imports yet"}]
    return [
        {"item": "File", "value": summary.filename},
        {"item": "Status", "value": summary.status},
        {"item": "Added", "value": summary.rows_added},
        {"item": "Updated", "value": summary.rows_updated},
        {"item": "Unchanged", "value": summary.rows_unchanged},
        {"item": "Missing", "value": summary.rows_missing},
        {"item": "New columns", "value": len(summary.new_columns)},
        {"item": "Missing columns", "value": len(summary.missing_columns)},
    ]


def render_latest_import_card(ui_module, summary: LatestImportSummary | None) -> None:
    columns = [
        {"name": "item", "label": "Item", "field": "item", "align": "left"},
        {"name": "value", "label": "Value", "field": "value", "align": "left"},
    ]
    with ui_module.card().classes("rounded-md shadow-sm border border-gray-100 p-4"):
        ui_module.label("Latest Import").classes("text-sm font-semibold text-gray-800")
        ui_module.table(columns=columns, rows=build_latest_import_rows(summary), pagination={"rowsPerPage": 8}).classes("w-full")
