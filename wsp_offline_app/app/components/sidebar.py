from __future__ import annotations

from dataclasses import dataclass

from app.theme import SIDEBAR_LINK_CLASS


@dataclass(frozen=True)
class NavItem:
    label: str
    path: str
    icon: str


NAV_ITEMS: tuple[NavItem, ...] = (
    NavItem("Dashboard", "/", "dashboard"),
    NavItem("Filters", "/filters", "filter_alt"),
    NavItem("Import", "/import", "upload_file"),
    NavItem("Students", "/students", "person_search"),
    NavItem("History", "/history", "history"),
    NavItem("Settings", "/settings", "settings"),
)


def get_nav_item(path: str) -> NavItem | None:
    return next((item for item in NAV_ITEMS if item.path == path), None)


def render_sidebar(ui_module, *, active_path: str) -> None:
    with ui_module.left_drawer(value=True).classes("bg-white border-r border-gray-200"):
        with ui_module.column().classes("w-full gap-1 p-3"):
            ui_module.label("WSP Offline").classes("text-lg font-semibold px-2 py-2")
            for item in NAV_ITEMS:
                active = item.path == active_path
                button = ui_module.button(
                    item.label,
                    icon=item.icon,
                    on_click=lambda path=item.path: ui_module.navigate.to(path),
                )
                button.props("flat no-caps align=left")
                button.classes(
                    f"{SIDEBAR_LINK_CLASS} "
                    + ("bg-primary text-white" if active else "text-gray-700")
                )
