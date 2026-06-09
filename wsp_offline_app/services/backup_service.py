from __future__ import annotations

import re
import shutil
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from database.models import BackupLog


class BackupError(Exception):
    """Base error for backup failures."""


class BackupIntegrityError(BackupError):
    """Raised when a SQLite backup fails integrity verification."""


class RestoreNotConfirmedError(BackupError):
    """Raised when restore is requested without explicit confirmation."""


@dataclass(frozen=True)
class BackupResult:
    source_database_path: Path
    backup_path: Path
    reason: str
    created_at: datetime


@dataclass(frozen=True)
class RestoreResult:
    restored_database_path: Path
    restored_from_backup_path: Path
    pre_restore_backup_path: Path
    restored_at: datetime


@dataclass(frozen=True)
class BackupRetentionPreview:
    enabled: bool
    keep_latest: int | None
    files_to_keep: tuple[Path, ...]
    files_to_delete: tuple[Path, ...]


def safe_backup_reason(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    cleaned = re.sub(r"_+", "_", cleaned)
    return cleaned.strip("._") or "backup"


def build_backup_filename(reason: str, created_at: datetime) -> str:
    timestamp = created_at.strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{safe_backup_reason(reason)}_wsp.db"


def verify_database_integrity(database_path: Path | str) -> bool:
    path = Path(database_path).resolve()
    try:
        with sqlite3.connect(path) as connection:
            result = connection.execute("PRAGMA integrity_check").fetchone()
    except sqlite3.DatabaseError as exc:
        raise BackupIntegrityError(f"Database integrity check failed for {path}: {exc}") from exc

    if result is None or result[0] != "ok":
        message = result[0] if result else "no result"
        raise BackupIntegrityError(f"Database integrity check failed for {path}: {message}")

    return True


def create_database_backup(
    database_path: Path | str,
    backup_dir: Path | str,
    *,
    reason: str,
    session: Session | None = None,
    created_at: datetime | None = None,
) -> BackupResult:
    source_path = Path(database_path).resolve()
    destination_dir = Path(backup_dir).resolve()

    if not source_path.exists():
        raise FileNotFoundError(f"Database does not exist: {source_path}")

    if destination_dir.exists() and not destination_dir.is_dir():
        raise BackupError(f"Backup path exists but is not a directory: {destination_dir}")

    destination_dir.mkdir(parents=True, exist_ok=True)
    resolved_created_at = created_at or datetime.now(UTC)
    backup_path = destination_dir / build_backup_filename(reason, resolved_created_at)

    counter = 1
    while backup_path.exists():
        backup_path = destination_dir / f"{backup_path.stem}_{counter}.db"
        counter += 1

    source_connection = sqlite3.connect(str(source_path))
    destination_connection = sqlite3.connect(str(backup_path))
    try:
        with destination_connection:
            source_connection.backup(destination_connection)
    finally:
        destination_connection.close()
        source_connection.close()

    integrity_check_passed = verify_database_integrity(backup_path)

    result = BackupResult(
        source_database_path=source_path,
        backup_path=backup_path,
        reason=reason,
        created_at=resolved_created_at,
    )

    if session is not None:
        session.add(
            BackupLog(
                backup_path=str(backup_path),
                reason=reason,
                status="created",
                integrity_check_passed=integrity_check_passed,
            )
        )

    return result


def list_database_backups(backup_dir: Path | str) -> tuple[Path, ...]:
    path = Path(backup_dir).resolve()
    if not path.exists():
        return ()
    if not path.is_dir():
        raise BackupError(f"Backup path exists but is not a directory: {path}")

    return tuple(sorted(path.glob("*.db"), key=lambda item: item.stat().st_mtime, reverse=True))


def _remove_sqlite_sidecars(database_path: Path) -> None:
    for suffix in ("-wal", "-shm"):
        sidecar = Path(str(database_path) + suffix)
        if sidecar.exists():
            sidecar.unlink()


def _log_restore_event(database_path: Path, *, restored_from: Path, pre_restore_backup: Path, restored_at: datetime) -> None:
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO backup_log
                (backup_path, reason, status, integrity_check_passed, error_message, created_at)
            VALUES
                (?, ?, ?, ?, ?, ?)
            """,
            (
                str(pre_restore_backup),
                f"restore_from_backup:{restored_from}",
                "restored",
                1,
                None,
                restored_at.isoformat(),
            ),
        )
        connection.commit()


def restore_database_from_backup(
    database_path: Path | str,
    backup_path: Path | str,
    backup_dir: Path | str,
    *,
    confirmed: bool = False,
    restored_at: datetime | None = None,
) -> RestoreResult:
    if not confirmed:
        raise RestoreNotConfirmedError("Restore requires confirmed=True")

    source_database_path = Path(database_path).resolve()
    selected_backup_path = Path(backup_path).resolve()
    resolved_restored_at = restored_at or datetime.now(UTC)

    verify_database_integrity(selected_backup_path)
    pre_restore_backup = create_database_backup(
        source_database_path,
        backup_dir,
        reason="pre_restore",
        created_at=resolved_restored_at,
    )

    _remove_sqlite_sidecars(source_database_path)
    shutil.copy2(selected_backup_path, source_database_path)
    _remove_sqlite_sidecars(source_database_path)
    verify_database_integrity(source_database_path)
    _log_restore_event(
        source_database_path,
        restored_from=selected_backup_path,
        pre_restore_backup=pre_restore_backup.backup_path,
        restored_at=resolved_restored_at,
    )

    return RestoreResult(
        restored_database_path=source_database_path,
        restored_from_backup_path=selected_backup_path,
        pre_restore_backup_path=pre_restore_backup.backup_path,
        restored_at=resolved_restored_at,
    )


def preview_backup_retention(
    backup_dir: Path | str,
    *,
    enabled: bool = False,
    keep_latest: int | None = None,
) -> BackupRetentionPreview:
    backups = list_database_backups(backup_dir)

    if not enabled or keep_latest is None:
        return BackupRetentionPreview(
            enabled=False,
            keep_latest=keep_latest,
            files_to_keep=backups,
            files_to_delete=(),
        )

    if keep_latest < 0:
        raise ValueError("keep_latest cannot be negative")

    return BackupRetentionPreview(
        enabled=True,
        keep_latest=keep_latest,
        files_to_keep=backups[:keep_latest],
        files_to_delete=backups[keep_latest:],
    )
