from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from database.models import ImportBatch
from services.excel_importer import calculate_file_hash, validate_excel_file_path


class ArchiveError(Exception):
    """Base error for archive failures."""


class ArchiveIntegrityError(ArchiveError):
    """Raised when an archived file does not match the original hash."""


@dataclass(frozen=True)
class ArchiveResult:
    original_path: Path
    archived_path: Path
    file_hash: str
    archived_at: datetime


def safe_filename_part(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    cleaned = re.sub(r"_+", "_", cleaned)
    return cleaned.strip("._") or "excel"


def build_archive_filename(source_path: Path, file_hash: str, archived_at: datetime) -> str:
    timestamp = archived_at.strftime("%Y%m%d_%H%M%S")
    safe_stem = safe_filename_part(source_path.stem)
    short_hash = file_hash[:12]
    return f"{timestamp}_{safe_stem}_{short_hash}{source_path.suffix.lower()}"


def archive_original_excel_file(
    source_path: Path | str,
    archive_dir: Path | str,
    *,
    file_hash: str | None = None,
    archived_at: datetime | None = None,
) -> ArchiveResult:
    workbook_path = validate_excel_file_path(source_path)
    destination_dir = Path(archive_dir).resolve()

    if destination_dir.exists() and not destination_dir.is_dir():
        raise ArchiveError(f"Archive path exists but is not a directory: {destination_dir}")

    destination_dir.mkdir(parents=True, exist_ok=True)
    resolved_hash = file_hash or calculate_file_hash(workbook_path)
    resolved_archived_at = archived_at or datetime.now(UTC)
    archived_path = destination_dir / build_archive_filename(workbook_path, resolved_hash, resolved_archived_at)

    counter = 1
    while archived_path.exists():
        archived_path = destination_dir / (
            f"{archived_path.stem}_{counter}{workbook_path.suffix.lower()}"
        )
        counter += 1

    shutil.copy2(workbook_path, archived_path)

    archived_hash = calculate_file_hash(archived_path)
    if archived_hash != resolved_hash:
        raise ArchiveIntegrityError(
            f"Archived Excel hash mismatch: expected {resolved_hash}, got {archived_hash}"
        )

    return ArchiveResult(
        original_path=workbook_path,
        archived_path=archived_path,
        file_hash=resolved_hash,
        archived_at=resolved_archived_at,
    )


def archive_and_create_pending_import_batch(
    session: Session,
    source_path: Path | str,
    archive_dir: Path | str,
    *,
    file_hash: str | None = None,
    archived_at: datetime | None = None,
) -> ImportBatch:
    archive_result = archive_original_excel_file(
        source_path,
        archive_dir,
        file_hash=file_hash,
        archived_at=archived_at,
    )

    batch = ImportBatch(
        filename=archive_result.original_path.name,
        file_path=str(archive_result.original_path),
        archived_file_path=str(archive_result.archived_path),
        file_hash=archive_result.file_hash,
        status="pending",
    )
    session.add(batch)
    session.flush()
    return batch
