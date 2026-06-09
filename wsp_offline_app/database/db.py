from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


DEFAULT_BUSY_TIMEOUT_MS = 5000


def build_sqlite_url(database_path: Path | str) -> str:
    path = Path(database_path).resolve()
    return f"sqlite:///{path.as_posix()}"


def create_sqlite_engine(
    database_path: Path | str,
    *,
    echo: bool = False,
    enable_wal: bool = True,
    busy_timeout_ms: int = DEFAULT_BUSY_TIMEOUT_MS,
) -> Engine:
    path = Path(database_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(build_sqlite_url(path), echo=echo, future=True)

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragmas(dbapi_connection: Any, _connection_record: Any) -> None:
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute(f"PRAGMA busy_timeout={int(busy_timeout_ms)}")
            if enable_wal:
                cursor.execute("PRAGMA journal_mode=WAL")
        finally:
            cursor.close()

    return engine


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, class_=Session, expire_on_commit=False, future=True)


def health_check(engine: Engine) -> bool:
    with engine.connect() as connection:
        return connection.execute(text("SELECT 1")).scalar_one() == 1


def read_pragma(engine: Engine, pragma_name: str) -> Any:
    with engine.connect() as connection:
        return connection.exec_driver_sql(f"PRAGMA {pragma_name}").scalar()


def initialize_database(engine: Engine) -> None:
    from database.models import Base
    from database.migrations import run_lightweight_migrations

    Base.metadata.create_all(engine)
    run_lightweight_migrations(engine)
