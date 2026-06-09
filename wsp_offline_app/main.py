from __future__ import annotations

from dataclasses import dataclass

from config import AppSettings, ensure_data_directories, get_default_settings
from database.db import create_sqlite_engine, initialize_database


@dataclass(frozen=True)
class StartupContext:
    settings: AppSettings
    created_directories: tuple[str, ...]


def build_startup_context(settings: AppSettings | None = None) -> StartupContext:
    active_settings = settings or get_default_settings()
    directories = ensure_data_directories(active_settings)
    initialize_runtime_database(active_settings)
    return StartupContext(
        settings=active_settings,
        created_directories=tuple(str(path) for path in directories),
    )


def initialize_runtime_database(settings: AppSettings) -> None:
    engine = create_sqlite_engine(settings.database_path)
    initialize_database(engine)


def run(settings: AppSettings | None = None) -> None:
    context = build_startup_context(settings)

    try:
        import uvicorn
    except ModuleNotFoundError as exc:
        raise RuntimeError("FastAPI/Uvicorn UI dependencies are not installed yet.") from exc

    from app.web_app import create_web_app

    uvicorn.run(
        create_web_app(context.settings),
        host=context.settings.ui_host,
        port=context.settings.ui_port,
        log_level="info",
    )


if __name__ == "__main__":
    run()
