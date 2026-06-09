from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

from database.db import create_session_factory, create_sqlite_engine, initialize_database
from database.models import BackupLog, StudentCurrent
from services.backup_service import (
    BackupError,
    BackupIntegrityError,
    RestoreNotConfirmedError,
    build_backup_filename,
    create_database_backup,
    list_database_backups,
    preview_backup_retention,
    restore_database_from_backup,
    safe_backup_reason,
    verify_database_integrity,
)


def test_safe_backup_reason_removes_unsafe_characters() -> None:
    assert safe_backup_reason(" pre import / WSP ") == "pre_import_WSP"
    assert safe_backup_reason("...") == "backup"


def test_build_backup_filename_includes_timestamp_and_reason() -> None:
    created_at = datetime(2026, 6, 4, 13, 5, 1, tzinfo=UTC)

    assert build_backup_filename("pre import", created_at) == "20260604_130501_pre_import_wsp.db"


def test_create_database_backup_creates_openable_sqlite_file(tmp_path: Path) -> None:
    database_path = tmp_path / "wsp.db"
    engine = create_sqlite_engine(database_path)
    initialize_database(engine)

    result = create_database_backup(
        database_path,
        tmp_path / "backups",
        reason="pre_import",
        created_at=datetime(2026, 6, 4, 13, 5, 1, tzinfo=UTC),
    )

    assert result.backup_path.exists()
    with sqlite3.connect(result.backup_path) as connection:
        value = connection.execute("SELECT 1").fetchone()[0]
    assert value == 1


def test_database_backup_contains_expected_tables(tmp_path: Path) -> None:
    database_path = tmp_path / "wsp.db"
    engine = create_sqlite_engine(database_path)
    initialize_database(engine)

    result = create_database_backup(database_path, tmp_path / "backups", reason="pre_import")

    with sqlite3.connect(result.backup_path) as connection:
        table_names = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        }

    assert "students_current" in table_names
    assert "import_batches" in table_names
    assert "backup_log" in table_names


def test_database_backup_captures_existing_data(tmp_path: Path) -> None:
    database_path = tmp_path / "wsp.db"
    engine = create_sqlite_engine(database_path)
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add(StudentCurrent(STUD_ID="1001", STUD_NAME="Backed Up"))
        session.commit()

    result = create_database_backup(database_path, tmp_path / "backups", reason="pre_import")

    with sqlite3.connect(result.backup_path) as connection:
        name = connection.execute("SELECT STUD_NAME FROM students_current WHERE STUD_ID = '1001'").fetchone()[0]

    assert name == "Backed Up"


def test_database_backup_log_row_is_created(tmp_path: Path) -> None:
    database_path = tmp_path / "wsp.db"
    engine = create_sqlite_engine(database_path)
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        result = create_database_backup(database_path, tmp_path / "backups", reason="pre_import", session=session)
        session.commit()

    with session_factory() as session:
        log = session.query(BackupLog).one()

    assert log.backup_path == str(result.backup_path)
    assert log.reason == "pre_import"
    assert log.status == "created"
    assert log.integrity_check_passed is True


def test_create_database_backup_rejects_missing_database(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Database does not exist"):
        create_database_backup(tmp_path / "missing.db", tmp_path / "backups", reason="pre_import")


def test_create_database_backup_rejects_file_backup_path(tmp_path: Path) -> None:
    database_path = tmp_path / "wsp.db"
    engine = create_sqlite_engine(database_path)
    initialize_database(engine)
    backup_path = tmp_path / "backups"
    backup_path.write_text("not a directory", encoding="utf-8")

    with pytest.raises(BackupError, match="not a directory"):
        create_database_backup(database_path, backup_path, reason="pre_import")


def test_valid_backup_passes_integrity_check(tmp_path: Path) -> None:
    database_path = tmp_path / "wsp.db"
    engine = create_sqlite_engine(database_path)
    initialize_database(engine)
    result = create_database_backup(database_path, tmp_path / "backups", reason="pre_import")

    assert verify_database_integrity(result.backup_path) is True


def test_invalid_backup_fails_integrity_check(tmp_path: Path) -> None:
    invalid_database = tmp_path / "invalid.db"
    invalid_database.write_text("not sqlite", encoding="utf-8")

    with pytest.raises(BackupIntegrityError, match="integrity check failed"):
        verify_database_integrity(invalid_database)


def test_required_pre_import_backup_failure_is_loud(tmp_path: Path) -> None:
    database_path = tmp_path / "wsp.db"
    engine = create_sqlite_engine(database_path)
    initialize_database(engine)
    backup_path = tmp_path / "backups"
    backup_path.write_text("not a directory", encoding="utf-8")

    with pytest.raises(BackupError):
        create_database_backup(database_path, backup_path, reason="pre_import")


def test_list_database_backups_returns_sorted_backups(tmp_path: Path) -> None:
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    older = backup_dir / "older.db"
    newer = backup_dir / "newer.db"
    older.write_text("older", encoding="utf-8")
    newer.write_text("newer", encoding="utf-8")

    older_time = 1_700_000_000
    newer_time = 1_800_000_000
    import os

    os.utime(older, (older_time, older_time))
    os.utime(newer, (newer_time, newer_time))

    assert list_database_backups(backup_dir) == (newer, older)


def test_restore_requires_explicit_confirmation(tmp_path: Path) -> None:
    with pytest.raises(RestoreNotConfirmedError, match="confirmed=True"):
        restore_database_from_backup(tmp_path / "wsp.db", tmp_path / "backup.db", tmp_path / "backups")


def test_restore_replaces_database_and_logs_restore_event(tmp_path: Path) -> None:
    database_path = tmp_path / "wsp.db"
    backup_dir = tmp_path / "backups"
    engine = create_sqlite_engine(database_path)
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add(StudentCurrent(STUD_ID="1001", STUD_NAME="Original"))
        session.commit()

    original_backup = create_database_backup(
        database_path,
        backup_dir,
        reason="known_good",
        created_at=datetime(2026, 6, 4, 13, 5, 1, tzinfo=UTC),
    )

    with session_factory() as session:
        student = session.query(StudentCurrent).filter_by(STUD_ID="1001").one()
        student.STUD_NAME = "Changed"
        session.commit()

    engine.dispose()
    result = restore_database_from_backup(
        database_path,
        original_backup.backup_path,
        backup_dir,
        confirmed=True,
        restored_at=datetime(2026, 6, 4, 13, 6, 1, tzinfo=UTC),
    )

    with sqlite3.connect(database_path) as connection:
        restored_name = connection.execute("SELECT STUD_NAME FROM students_current WHERE STUD_ID = '1001'").fetchone()[0]
        restore_log_count = connection.execute(
            "SELECT COUNT(*) FROM backup_log WHERE status = 'restored'"
        ).fetchone()[0]

    assert restored_name == "Original"
    assert result.pre_restore_backup_path.exists()
    assert restore_log_count == 1


def test_restore_creates_pre_restore_backup(tmp_path: Path) -> None:
    database_path = tmp_path / "wsp.db"
    backup_dir = tmp_path / "backups"
    engine = create_sqlite_engine(database_path)
    initialize_database(engine)
    original_backup = create_database_backup(database_path, backup_dir, reason="known_good")
    engine.dispose()

    result = restore_database_from_backup(database_path, original_backup.backup_path, backup_dir, confirmed=True)

    assert result.pre_restore_backup_path.exists()
    assert "pre_restore" in result.pre_restore_backup_path.name


def test_retention_is_disabled_by_default(tmp_path: Path) -> None:
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    backup = backup_dir / "backup.db"
    backup.write_text("backup", encoding="utf-8")

    preview = preview_backup_retention(backup_dir)

    assert preview.enabled is False
    assert preview.files_to_keep == (backup,)
    assert preview.files_to_delete == ()
    assert backup.exists()


def test_retention_preview_lists_files_without_deleting(tmp_path: Path) -> None:
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    first = backup_dir / "first.db"
    second = backup_dir / "second.db"
    third = backup_dir / "third.db"
    for path in (first, second, third):
        path.write_text(path.name, encoding="utf-8")

    import os

    os.utime(first, (1, 1))
    os.utime(second, (2, 2))
    os.utime(third, (3, 3))

    preview = preview_backup_retention(backup_dir, enabled=True, keep_latest=1)

    assert preview.enabled is True
    assert preview.files_to_keep == (third,)
    assert preview.files_to_delete == (second, first)
    assert first.exists()
    assert second.exists()
    assert third.exists()


def test_retention_preview_rejects_negative_keep_latest(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="cannot be negative"):
        preview_backup_retention(tmp_path, enabled=True, keep_latest=-1)
