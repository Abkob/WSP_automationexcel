from __future__ import annotations

from config import AppSettings


def render_settings_page(settings: AppSettings) -> None:
    from nicegui import ui

    ui.label(settings.runtime_mode.title()).classes("text-sm text-gray-600")
