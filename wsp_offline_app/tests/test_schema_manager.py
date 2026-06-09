from __future__ import annotations

from datetime import date
from pathlib import Path

from database.db import create_session_factory, create_sqlite_engine, initialize_database
from database.models import ColumnRegistry, ImportBatch
from database.schema_manager import infer_column_type, sync_column_registry


def create_batch(session, file_hash: str) -> ImportBatch:
    batch = ImportBatch(filename=f"{file_hash}.xlsx", file_path=f"C:/{file_hash}.xlsx", file_hash=file_hash)
    session.add(batch)
    session.commit()
    return batch


def test_infer_column_type_handles_common_values() -> None:
    assert infer_column_type([]) == "empty"
    assert infer_column_type([None, ""]) == "empty"
    assert infer_column_type([True, False]) == "boolean"
    assert infer_column_type([1, 2.5]) == "number"
    assert infer_column_type([date(2026, 6, 3)]) == "date"
    assert infer_column_type(["Python", "Excel"]) == "text"


def test_sync_column_registry_registers_new_columns(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        batch = create_batch(session, "hash-1")
        result = sync_column_registry(
            session,
            ["STUD_ID", "CUM_GPA"],
            batch_id=batch.batch_id,
            inferred_types={"STUD_ID": "text", "CUM_GPA": "number"},
        )
        session.commit()

    with session_factory() as session:
        rows = {row.column_name: row for row in session.query(ColumnRegistry).all()}

    assert result.new_columns == ("STUD_ID", "CUM_GPA")
    assert result.missing_columns == ()
    assert result.type_changes == ()
    assert rows["STUD_ID"].first_seen_batch_id == batch.batch_id
    assert rows["CUM_GPA"].detected_type == "number"
    assert rows["CUM_GPA"].is_active is True
    assert rows["CUM_GPA"].is_new_column is True


def test_sync_column_registry_updates_repeated_columns_last_seen_batch(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        first_batch = create_batch(session, "hash-1")
        sync_column_registry(session, ["STUD_ID"], batch_id=first_batch.batch_id)
        session.commit()

        second_batch = create_batch(session, "hash-2")
        result = sync_column_registry(session, ["STUD_ID", "NEW COLUMN"], batch_id=second_batch.batch_id)
        session.commit()

    with session_factory() as session:
        stud_id = session.query(ColumnRegistry).filter_by(column_name="STUD_ID").one()
        new_column = session.query(ColumnRegistry).filter_by(column_name="NEW_COLUMN").one()

    assert result.repeated_columns == ("STUD_ID",)
    assert result.new_columns == ("NEW_COLUMN",)
    assert stud_id.first_seen_batch_id == first_batch.batch_id
    assert stud_id.last_seen_batch_id == second_batch.batch_id
    assert stud_id.is_new_column is False
    assert new_column.is_new_column is True


def test_sync_column_registry_marks_missing_columns_inactive(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        first_batch = create_batch(session, "hash-1")
        sync_column_registry(session, ["STUD_ID", "CUM_GPA"], batch_id=first_batch.batch_id)
        session.commit()

        second_batch = create_batch(session, "hash-2")
        result = sync_column_registry(session, ["STUD_ID"], batch_id=second_batch.batch_id)
        session.commit()

    with session_factory() as session:
        missing = session.query(ColumnRegistry).filter_by(column_name="CUM_GPA").one()

    assert result.missing_columns == ("CUM_GPA",)
    assert missing.is_active is False
    assert missing.last_seen_batch_id == first_batch.batch_id


def test_sync_column_registry_detects_type_changes(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        first_batch = create_batch(session, "hash-1")
        sync_column_registry(session, ["CUM_GPA"], batch_id=first_batch.batch_id, inferred_types={"CUM_GPA": "number"})
        session.commit()

        second_batch = create_batch(session, "hash-2")
        result = sync_column_registry(session, ["CUM_GPA"], batch_id=second_batch.batch_id, inferred_types={"CUM_GPA": "text"})
        session.commit()

    with session_factory() as session:
        row = session.query(ColumnRegistry).filter_by(column_name="CUM_GPA").one()

    assert len(result.type_changes) == 1
    assert result.type_changes[0].column_name == "CUM_GPA"
    assert result.type_changes[0].previous_type == "number"
    assert result.type_changes[0].detected_type == "text"
    assert row.detected_type == "text"
    assert "Type changed from number to text" in (row.notes or "")


def test_sync_column_registry_preserves_non_empty_type_after_empty_first_seen(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        first_batch = create_batch(session, "hash-1")
        sync_column_registry(session, ["CUM_GPA"], batch_id=first_batch.batch_id, inferred_types={"CUM_GPA": "empty"})
        session.commit()

        second_batch = create_batch(session, "hash-2")
        sync_column_registry(session, ["CUM_GPA"], batch_id=second_batch.batch_id, inferred_types={"CUM_GPA": "number"})
        session.commit()

    with session_factory() as session:
        row = session.query(ColumnRegistry).filter_by(column_name="CUM_GPA").one()

    assert row.detected_type == "number"
