from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from sqlalchemy.exc import SQLAlchemyError

from app.components.sidebar import render_sidebar
from app.theme import PAGE_PADDING_CLASS, SHELL_MAX_WIDTH_CLASS, STATUS_CHIP_CLASS
from config import AppSettings
from database.db import create_session_factory, create_sqlite_engine, health_check
from database.models import BackupLog
from services.analytics_service import get_latest_import_summary


@dataclass(frozen=True)
class LayoutStatus:
    database_status: str
    database_detail: str
    latest_import_status: str
    latest_import_detail: str
    backup_status: str
    backup_detail: str


PageRenderer = Callable[[AppSettings], None]


def build_layout_status(settings: AppSettings) -> LayoutStatus:
    database_path = settings.database_path
    if not database_path.exists():
        return LayoutStatus(
            database_status="Database not created",
            database_detail=str(database_path),
            latest_import_status="No imports yet",
            latest_import_detail="Waiting for the first Excel import",
            backup_status="No backups yet",
            backup_detail=str(settings.backup_dir),
        )

    try:
        engine = create_sqlite_engine(database_path)
        database_ok = health_check(engine)
        session_factory = create_session_factory(engine)
        with session_factory() as session:
            latest_import = get_latest_import_summary(session)
            backup_count = session.query(BackupLog).count()
            latest_backup = session.query(BackupLog).order_by(BackupLog.backup_id.desc()).first()
    except SQLAlchemyError as exc:
        return LayoutStatus(
            database_status="Database error",
            database_detail=str(exc),
            latest_import_status="Unavailable",
            latest_import_detail="Import summary could not be read",
            backup_status="Unavailable",
            backup_detail="Backup status could not be read",
        )

    return LayoutStatus(
        database_status="Database ready" if database_ok else "Database unavailable",
        database_detail=database_path.name,
        latest_import_status=latest_import.status.title() if latest_import else "No imports yet",
        latest_import_detail=latest_import.filename if latest_import else "Waiting for the first Excel import",
        backup_status=f"{backup_count} backups" if backup_count else "No backups yet",
        backup_detail=Path(latest_backup.backup_path).name if latest_backup else str(settings.backup_dir),
    )


def render_app_shell(
    ui_module,
    *,
    settings: AppSettings,
    active_path: str,
    page_title: str,
    content_renderer: PageRenderer,
    status: LayoutStatus | None = None,
) -> None:
    active_status = status or build_layout_status(settings)
    render_sidebar(ui_module, active_path=active_path)

    with ui_module.header().classes("bg-primary text-white shadow-sm"):
        with ui_module.row().classes("w-full items-center justify-between gap-3 px-3 py-2"):
            with ui_module.row().classes("items-center gap-2"):
                ui_module.icon("school").classes("text-2xl")
                ui_module.label(settings.app_name).classes("text-base font-semibold")
            render_status_bar(ui_module, active_status)

    with ui_module.column().classes(f"{PAGE_PADDING_CLASS} {SHELL_MAX_WIDTH_CLASS} gap-4"):
        ui_module.label(page_title).classes("text-xl font-semibold")
        content_renderer(settings)


def render_status_bar(ui_module, status: LayoutStatus) -> None:
    with ui_module.row().classes("items-center gap-2"):
        render_status_chip(ui_module, "storage", status.database_status, status.database_detail)
        render_status_chip(ui_module, "upload_file", status.latest_import_status, status.latest_import_detail)
        render_status_chip(ui_module, "backup", status.backup_status, status.backup_detail)


def render_status_chip(ui_module, icon_name: str, label: str, detail: str) -> None:
    with ui_module.row().classes(f"{STATUS_CHIP_CLASS} items-center gap-1"):
        ui_module.icon(icon_name).classes("text-sm")
        ui_module.label(label).classes("whitespace-nowrap")
