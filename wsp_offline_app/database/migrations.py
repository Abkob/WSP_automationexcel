from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def run_lightweight_migrations(engine: Engine) -> None:
    add_semantic_document_hash_column(engine)
    add_semantic_vector_store_name_column(engine)
    add_student_audit_timestamp_columns(engine)


def add_semantic_document_hash_column(engine: Engine) -> None:
    inspector = inspect(engine)
    if "semantic_embeddings" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("semantic_embeddings")}
    if "semantic_document_hash" in existing_columns:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE semantic_embeddings ADD COLUMN semantic_document_hash VARCHAR(128)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_semantic_embeddings_semantic_document_hash ON semantic_embeddings (semantic_document_hash)"))


def add_semantic_vector_store_name_column(engine: Engine) -> None:
    inspector = inspect(engine)
    if "semantic_embeddings" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("semantic_embeddings")}
    if "vector_store_name" in existing_columns:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE semantic_embeddings ADD COLUMN vector_store_name VARCHAR(80) NOT NULL DEFAULT 'faiss'"))


def add_student_audit_timestamp_columns(engine: Engine) -> None:
    inspector = inspect(engine)
    if "students_current" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("students_current")}
    with engine.begin() as connection:
        if "added_to_db_at" not in existing_columns:
            connection.execute(text("ALTER TABLE students_current ADD COLUMN added_to_db_at DATETIME"))
            if "created_at" in existing_columns:
                connection.execute(text("UPDATE students_current SET added_to_db_at = created_at WHERE added_to_db_at IS NULL"))
        if "modified_in_db_at" not in existing_columns:
            connection.execute(text("ALTER TABLE students_current ADD COLUMN modified_in_db_at DATETIME"))
