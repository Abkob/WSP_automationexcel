from __future__ import annotations

from pathlib import Path

from app.components.sidebar import NAV_ITEMS, get_nav_item
from app.layout import LayoutStatus, build_layout_status, render_status_chip
from app.routes import PAGE_ROUTES, register_routes
from config import AppSettings
from database.db import create_session_factory, create_sqlite_engine, initialize_database
from database.models import BackupLog, ImportBatch


class FakeUi:
    def __init__(self) -> None:
        self.paths: list[str] = []
        self.handlers: list[object] = []
        self.colors_kwargs: dict[str, str] | None = None
        self.head_html: list[str] = []

    def page(self, path: str):
        self.paths.append(path)

        def decorator(handler):
            self.handlers.append(handler)
            return handler

        return decorator

    def colors(self, **kwargs) -> None:
        self.colors_kwargs = kwargs

    def add_head_html(self, html: str) -> None:
        self.head_html.append(html)


class FakeElement:
    def __init__(self, ui: "FakeRenderUi") -> None:
        self.ui = ui

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _traceback) -> None:
        return None

    def classes(self, value: str):
        self.ui.classes.append(value)
        return self

    def props(self, _value: str):
        self.ui.props_called = True
        return self


class FakeRenderUi:
    def __init__(self) -> None:
        self.labels: list[str] = []
        self.icons: list[str] = []
        self.classes: list[str] = []
        self.props_called = False

    def row(self):
        return FakeElement(self)

    def icon(self, name: str):
        self.icons.append(name)
        return FakeElement(self)

    def label(self, value: str):
        self.labels.append(value)
        return FakeElement(self)


def test_ui_modules_import_successfully() -> None:
    from app import layout, routes, theme
    from app.pages import dashboard_page, filter_page, history_page, import_page, settings_page, student_profile_page

    assert layout.LayoutStatus
    assert routes.PAGE_ROUTES
    assert theme.APP_PRIMARY_COLOR
    assert dashboard_page.render_dashboard_page
    assert filter_page.render_filter_page
    assert history_page.render_history_page
    assert import_page.render_import_page
    assert settings_page.render_settings_page
    assert student_profile_page.render_student_profile_page


def test_sidebar_items_cover_registered_routes() -> None:
    route_paths = {route.path for route in PAGE_ROUTES}
    nav_paths = {item.path for item in NAV_ITEMS}

    assert route_paths == nav_paths
    assert get_nav_item("/") is not None
    assert get_nav_item("/missing") is None


def test_register_routes_registers_all_pages_and_applies_theme(tmp_path: Path) -> None:
    fake_ui = FakeUi()
    settings = AppSettings(data_dir=tmp_path / "data", runtime_mode="testing")

    registered = register_routes(settings, fake_ui)

    assert registered == PAGE_ROUTES
    assert fake_ui.paths == [route.path for route in PAGE_ROUTES]
    assert len(fake_ui.handlers) == len(PAGE_ROUTES)
    assert fake_ui.colors_kwargs is not None
    assert fake_ui.colors_kwargs["primary"] == "#1f6f8b"
    assert fake_ui.head_html


def test_layout_status_reports_missing_database(tmp_path: Path) -> None:
    settings = AppSettings(data_dir=tmp_path / "data", runtime_mode="testing")

    status = build_layout_status(settings)

    assert isinstance(status, LayoutStatus)
    assert status.database_status == "Database not created"
    assert status.latest_import_status == "No imports yet"
    assert status.backup_status == "No backups yet"


def test_layout_status_reports_database_import_and_backup(tmp_path: Path) -> None:
    settings = AppSettings(data_dir=tmp_path / "data", runtime_mode="testing")
    engine = create_sqlite_engine(settings.database_path)
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add(
            ImportBatch(
                filename="WSP.xlsx",
                file_path="C:/WSP.xlsx",
                file_hash="hash-1",
                status="completed",
            )
        )
        session.add(
            BackupLog(
                backup_path=str(settings.backup_dir / "backup.sqlite"),
                reason="manual",
                status="created",
            )
        )
        session.commit()

    status = build_layout_status(settings)

    assert status.database_status == "Database ready"
    assert status.database_detail == "wsp.db"
    assert status.latest_import_status == "Completed"
    assert status.latest_import_detail == "WSP.xlsx"
    assert status.backup_status == "1 backups"
    assert status.backup_detail == "backup.sqlite"


def test_status_chip_handles_windows_path_details_without_props_parser() -> None:
    fake_ui = FakeRenderUi()

    render_status_chip(fake_ui, "storage", "Database ready", r"C:\Users\Example\Documents\WSP\data\wsp.db")

    assert fake_ui.icons == ["storage"]
    assert fake_ui.labels == ["Database ready"]
    assert fake_ui.props_called is False
