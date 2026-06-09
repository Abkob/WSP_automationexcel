from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from database.db import (
    build_sqlite_url,
    create_session_factory,
    create_sqlite_engine,
    health_check,
    initialize_database,
    read_pragma,
)
from database.models import ColumnRegistry, FileImportLog, ImportBatch, StudentCurrent, StudentHistory
from database.migrations import add_student_audit_timestamp_columns
from services.excel_schema import EXPECTED_WSP_COLUMNS


def test_build_sqlite_url_uses_absolute_file_path(tmp_path: Path) -> None:
    database_path = tmp_path / "wsp.db"

    url = build_sqlite_url(database_path)

    assert url.startswith("sqlite:///")
    assert database_path.resolve().as_posix() in url


def test_create_sqlite_engine_creates_database_file(tmp_path: Path) -> None:
    database_path = tmp_path / "wsp.db"
    engine = create_sqlite_engine(database_path)

    with engine.connect() as connection:
        assert connection.execute(text("SELECT 1")).scalar_one() == 1

    assert database_path.exists()


def test_session_factory_can_insert_and_query_record(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    session_factory = create_session_factory(engine)

    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE demo (id INTEGER PRIMARY KEY, name TEXT NOT NULL)"))

    with session_factory() as session:
        session.execute(text("INSERT INTO demo (name) VALUES (:name)"), {"name": "sample"})
        session.commit()

    with session_factory() as session:
        value = session.execute(text("SELECT name FROM demo WHERE id = 1")).scalar_one()

    assert value == "sample"


def test_foreign_keys_are_enabled(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")

    assert read_pragma(engine, "foreign_keys") == 1


def test_busy_timeout_is_set(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db", busy_timeout_ms=4321)

    assert read_pragma(engine, "busy_timeout") == 4321


def test_wal_mode_is_enabled_for_file_database(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db", enable_wal=True)

    assert read_pragma(engine, "journal_mode") == "wal"


def test_health_check_returns_true(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")

    assert health_check(engine) is True


def test_initialize_database_creates_core_tables(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")

    initialize_database(engine)

    table_names = set(inspect(engine).get_table_names())
    assert table_names == {
        "backup_log",
        "column_registry",
        "export_log",
        "file_import_log",
        "filter_presets",
        "filter_runs",
        "import_batches",
        "semantic_embeddings",
        "students_current",
        "students_history",
    }


def test_initialize_database_migrates_existing_semantic_embedding_columns(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE semantic_embeddings (
                    embedding_id INTEGER PRIMARY KEY,
                    STUD_ID VARCHAR(64) NOT NULL,
                    source_column VARCHAR(255) NOT NULL,
                    source_text TEXT NOT NULL,
                    embedding_vector_id VARCHAR(255) NOT NULL,
                    embedding_model_name VARCHAR(255) NOT NULL,
                    updated_at DATETIME NOT NULL
                )
                """
            )
        )

    initialize_database(engine)

    column_names = {column["name"] for column in inspect(engine).get_columns("semantic_embeddings")}
    assert "semantic_document_hash" in column_names
    assert "vector_store_name" in column_names


def test_initialize_database_migrates_existing_student_audit_timestamp_columns(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE students_current (
                    internal_id INTEGER PRIMARY KEY,
                    STUD_ID VARCHAR(64) NOT NULL UNIQUE,
                    created_at DATETIME NOT NULL,
                    updated_at DATETIME NOT NULL,
                    missing_from_latest_import BOOLEAN NOT NULL DEFAULT 0
                )
                """
            )
        )
        connection.execute(
            text(
                """
                INSERT INTO students_current
                    (STUD_ID, created_at, updated_at, missing_from_latest_import)
                VALUES
                    ('1001', '2026-06-01 10:00:00', '2026-06-01 10:00:00', 0)
                """
            )
        )

    add_student_audit_timestamp_columns(engine)

    column_names = {column["name"] for column in inspect(engine).get_columns("students_current")}
    assert "added_to_db_at" in column_names
    assert "modified_in_db_at" in column_names
    with engine.connect() as connection:
        added = connection.execute(text("SELECT added_to_db_at FROM students_current WHERE STUD_ID = '1001'")).scalar_one()
    assert added == "2026-06-01 10:00:00"


def test_students_current_contains_expected_wsp_columns(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)

    column_names = {column["name"] for column in inspect(engine).get_columns("students_current")}

    for expected_column in EXPECTED_WSP_COLUMNS:
        assert expected_column in column_names
    assert "extra_columns_json" in column_names
    assert "row_hash" in column_names
    assert "missing_from_latest_import" in column_names
    assert "added_to_db_at" in column_names
    assert "modified_in_db_at" in column_names


def test_required_indexes_exist(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)

    inspector = inspect(engine)
    student_indexes = {tuple(index["column_names"]) for index in inspector.get_indexes("students_current")}
    import_indexes = {tuple(index["column_names"]) for index in inspector.get_indexes("import_batches")}
    registry_indexes = {tuple(index["column_names"]) for index in inspector.get_indexes("column_registry")}

    assert ("STUD_ID",) in student_indexes
    assert ("MAJR_DESC", "CLAS_DESC") in student_indexes
    assert ("FINANCIAL_AID", "PROBATION") in student_indexes
    assert ("file_hash",) in import_indexes
    assert ("column_name",) in registry_indexes


def test_students_current_unique_student_id_is_enforced(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add(StudentCurrent(STUD_ID="1001", STUD_NAME="First"))
        session.commit()

    with pytest.raises(IntegrityError):
        with session_factory() as session:
            session.add(StudentCurrent(STUD_ID="1001", STUD_NAME="Duplicate"))
            session.commit()


def test_students_current_extra_columns_json_round_trips(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        student = StudentCurrent(
            STUD_ID="1001",
            STUD_NAME="Extra Column Student",
            extra_columns_json={"NEW_COLUMN": "new value"},
        )
        session.add(student)
        session.commit()

    with session_factory() as session:
        student = session.query(StudentCurrent).filter_by(STUD_ID="1001").one()

    assert student.extra_columns_json == {"NEW_COLUMN": "new value"}


def test_students_current_missing_flag_defaults_to_false(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add(StudentCurrent(STUD_ID="1001"))
        session.commit()

    with session_factory() as session:
        student = session.query(StudentCurrent).filter_by(STUD_ID="1001").one()

    assert student.missing_from_latest_import is False


def test_import_batch_file_hash_is_unique(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    first = ImportBatch(filename="WSP.xlsx", file_path="C:/WSP.xlsx", file_hash="abc123")
    second = ImportBatch(filename="WSP-copy.xlsx", file_path="C:/WSP-copy.xlsx", file_hash="abc123")

    with session_factory() as session:
        session.add(first)
        session.commit()

    with pytest.raises(IntegrityError):
        with session_factory() as session:
            session.add(second)
            session.commit()


def test_import_batch_status_can_be_updated(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        batch = ImportBatch(filename="WSP.xlsx", file_path="C:/WSP.xlsx", file_hash="hash-1")
        session.add(batch)
        session.commit()
        batch.status = "completed"
        session.commit()

    with session_factory() as session:
        batch = session.query(ImportBatch).filter_by(file_hash="hash-1").one()

    assert batch.status == "completed"


def test_student_history_can_link_to_import_batch(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        batch = ImportBatch(filename="WSP.xlsx", file_path="C:/WSP.xlsx", file_hash="hash-1")
        session.add(batch)
        session.commit()

        history = StudentHistory(
            batch_id=batch.batch_id,
            STUD_ID="1001",
            all_excel_columns={"STUD_ID": "1001", "CUM_GPA": 3.4},
            row_hash="row-hash",
            change_type="new_student",
        )
        session.add(history)
        session.commit()

    with session_factory() as session:
        history = session.query(StudentHistory).filter_by(STUD_ID="1001").one()

        assert history.batch is not None
        assert history.batch.filename == "WSP.xlsx"
        assert history.all_excel_columns == {"STUD_ID": "1001", "CUM_GPA": 3.4}


def test_import_event_log_can_link_to_batch(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        batch = ImportBatch(filename="WSP.xlsx", file_path="C:/WSP.xlsx", file_hash="hash-1")
        session.add(batch)
        session.commit()

        event = FileImportLog(
            batch_id=batch.batch_id,
            event_type="row_rejected",
            row_number=5,
            STUD_ID=None,
            message="Missing STUD_ID",
            details_json={"column": "STUD_ID"},
        )
        session.add(event)
        session.commit()

    with session_factory() as session:
        event = session.query(FileImportLog).filter_by(event_type="row_rejected").one()

        assert event.batch is not None
        assert event.batch.filename == "WSP.xlsx"
        assert event.details_json == {"column": "STUD_ID"}


def test_column_registry_unique_column_name_is_enforced(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "wsp.db")
    initialize_database(engine)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        session.add(ColumnRegistry(column_name="STUD_ID", detected_type="text"))
        session.commit()

    with pytest.raises(IntegrityError):
        with session_factory() as session:
            session.add(ColumnRegistry(column_name="STUD_ID", detected_type="text"))
            session.commit()
