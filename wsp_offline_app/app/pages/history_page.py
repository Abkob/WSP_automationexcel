from __future__ import annotations

from config import AppSettings


def render_history_page(_settings: AppSettings) -> None:
    from nicegui import ui

    ui.label("History").classes("text-sm text-gray-600")
