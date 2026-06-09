from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from app.layout import render_app_shell
from app.pages.dashboard_page import render_dashboard_page
from app.pages.filter_page import render_filter_page
from app.pages.history_page import render_history_page
from app.pages.import_page import render_import_page
from app.pages.settings_page import render_settings_page
from app.pages.student_profile_page import render_student_profile_page
from app.theme import apply_theme
from config import AppSettings


@dataclass(frozen=True)
class PageRoute:
    path: str
    title: str
    renderer: Callable[[AppSettings], None]


PAGE_ROUTES: tuple[PageRoute, ...] = (
    PageRoute("/", "Dashboard", render_dashboard_page),
    PageRoute("/filters", "Filters", render_filter_page),
    PageRoute("/import", "Import", render_import_page),
    PageRoute("/students", "Students", render_student_profile_page),
    PageRoute("/history", "History", render_history_page),
    PageRoute("/settings", "Settings", render_settings_page),
)


def register_routes(settings: AppSettings, ui_module=None) -> tuple[PageRoute, ...]:
    if ui_module is None:
        from nicegui import ui as ui_module

    apply_theme(ui_module)
    for route in PAGE_ROUTES:
        ui_module.page(route.path)(make_page_handler(ui_module, settings, route))
    return PAGE_ROUTES


def make_page_handler(ui_module, settings: AppSettings, route: PageRoute):
    def page_handler() -> None:
        render_app_shell(
            ui_module,
            settings=settings,
            active_path=route.path,
            page_title=route.title,
            content_renderer=route.renderer,
        )

    return page_handler
