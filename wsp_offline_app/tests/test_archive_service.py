from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from openpyxl import Workbook

from database.db import create_session_factory, create_sqlite_engine, initialize_database
from database.models import ImportBatch
from services.archive_service import (
    ArchiveError,
    archive_and_create_pending_import_batch,
    archive_original_excel_file,
    build_archive_filename,
    safe_filename_part,
)
from services.excel_importer import calculate_file_hash


def create_workbook(path: Path) -> Path:
    workbook = Workbook()
    workbook.active.append(["STUD_ID"])
    workbook.active.append(["1001"])
    workbook.save(path)
    return path


def test_safe_filename_part_removes_unsafe_characters() -> None:
    assert safe_filename_part(" WSP Import / June ") == "WSP_Import_June"
    assert safe_filename_part("...") == "excel"


def test_build_archive_filename_includes_timestamp_stem_and_hash() -> None:
    archived_at = datetime(2026, 6, 4, 12, 30, 5, tzinfo=UTC)

    name = build_archive_filename(Path("WSP.xlsx"), "abcdef1234567890", archived_at)

    assert name == "20260604_123005_WSP_abcdef123456.xlsx"


def test_archive_original_excel_file_creates_verified_copy(tmp_path: Path) -> None:
    source = create_workbook(tmp_path / "WSP.xlsx")
    file_hash = calculate_file_hash(source)
    archive_dir = tmp_path / "archive"
    archived_at = datetime(2026, 6, 4, 12, 30, 5, tzinfo=UTC)

    result = archive_original_excel_file(source, archive_dir, file_hash=file_hash, archived_at=archived_at)

    assert result.archived_path.exists()
    assert result.archived_path.parent == archive_dir.resolve()
    assert result.archived_path.name == "20260604_123005_WSP_" + file_hash[:12] + ".xlsx"
    assert calculate_file_hash(result.archived_path) == file_hash


def test_archive_original_excel_file_avoids_filename_collision(tmp_path: Path) -> None:
    source = create_workbook(tmp_path / "WSP.xlsx")
    file_hash = calculate_file_hash(source)
    archive_dir = tmp_path / "archive"
    archived_at = datetime(2026, 6, 4, 12, 30, 5, tzinfo=UTC)

    first = archive_original_excel_file(source, archive_dir, file_hash=file_hash, archived_at=archived_at)
    second = archive_original_excel_file(source, archive_dir, file_hash=file_hash, archived_at=archived_at)

    assert first.archived_path.exists()
    assert second.archived_path.exists()
    assert first.archived_path != second.archived_path


def test_archive_original_excel_file_rejects_file_archive_path(tmp_path: Path) -> None:
    source = create_workbook(tmp_path / "WSP.xlsx")
    archive_path = tmp_path / "archive-is-file"
    archive_path.write_text("not a folder", encoding="utf-8")

    with pytest.raises(ArchiveError, match="not a directory"):
        archive_original_excel_file(source, archive_path)


def test_archive_and_create_pending_import_batch_records_archive_path(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    source = create_workbook(tmp_path / "WSP.xlsx")
    file_hash = calculate_file_hash(source)

    with session_factory() as session:
        batch = archive_and_create_pending_import_batch(
            session,
            source,
            tmp_path / "archive",
            file_hash=file_hash,
            archived_at=datetime(2026, 6, 4, 12, 30, 5, tzinfo=UTC),
        )
        session.commit()
        batch_id = batch.batch_id

    with session_factory() as session:
        batch = session.query(ImportBatch).filter_by(batch_id=batch_id).one()

    assert batch.file_hash == file_hash
    assert batch.archived_file_path is not None
    assert Path(batch.archived_file_path).exists()
    assert batch.status == "pending"


def test_archive_failure_prevents_import_batch_creation(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    source = create_workbook(tmp_path / "WSP.xlsx")
    archive_path = tmp_path / "archive-is-file"
    archive_path.write_text("not a folder", encoding="utf-8")

    with session_factory() as session:
        with pytest.raises(ArchiveError):
            archive_and_create_pending_import_batch(session, source, archive_path)
        session.rollback()

    with session_factory() as session:
        assert session.query(ImportBatch).count() == 0
