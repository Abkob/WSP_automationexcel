from __future__ import annotations

from config import AppSettings


def render_import_page(settings: AppSettings) -> None:
    from nicegui import ui

    ui.label(str(settings.incoming_excel_dir)).classes("text-sm text-gray-600")
