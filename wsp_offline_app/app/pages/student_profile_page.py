from __future__ import annotations

from config import AppSettings


def render_student_profile_page(_settings: AppSettings) -> None:
    from nicegui import ui

    ui.label("Students").classes("text-sm text-gray-600")
