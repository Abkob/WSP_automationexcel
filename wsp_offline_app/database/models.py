from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utc_now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class ImportBatch(Base):
    __tablename__ = "import_batches"

    batch_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    archived_file_path: Mapped[str | None] = mapped_column(Text)
    file_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    number_of_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    number_of_columns: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    new_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unchanged_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    missing_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    new_columns_detected: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    missing_columns_detected: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False, index=True)
    error_message: Mapped[str | None] = mapped_column(Text)

    history_rows: Mapped[list[StudentHistory]] = relationship(back_populates="batch")
    import_logs: Mapped[list[FileImportLog]] = relationship(back_populates="batch")


class StudentCurrent(Base, TimestampMixin):
    __tablename__ = "students_current"

    internal_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    STUD_ID: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    STUD_NAME: Mapped[str | None] = mapped_column(String(255))
    MAJR_DESC: Mapped[str | None] = mapped_column(String(255), index=True)
    CLAS_DESC: Mapped[str | None] = mapped_column(String(255), index=True)
    STUD_EMAIL: Mapped[str | None] = mapped_column(String(255))
    WSP_WRITTEN_LANGUAGES: Mapped[str | None] = mapped_column(Text)
    WSP_SPOKEN_LANGUAGES: Mapped[str | None] = mapped_column(Text)
    WSP_ORGANIZATIONAL_SKILLS: Mapped[str | None] = mapped_column(Text)
    WSP_TECHNICAL_SKILLS: Mapped[str | None] = mapped_column(Text)
    WSP_INTERPERSONAL_SKILLS: Mapped[str | None] = mapped_column(Text)
    WSP_ADDITIONAL_SKILLS: Mapped[str | None] = mapped_column(Text)
    WSP_PREV_WORK: Mapped[str | None] = mapped_column(Text)
    WSP_PREVIOUS_TYPE_OF_WORK: Mapped[str | None] = mapped_column(Text)
    WSP_PREFERRED_TYPE_OF_WORK: Mapped[str | None] = mapped_column(Text)
    DEANS_WARNING: Mapped[bool | None] = mapped_column(Boolean)
    ENRL_TERM: Mapped[str | None] = mapped_column(String(50))
    DEAN_WARN: Mapped[bool | None] = mapped_column(Boolean)
    MOBILE_NBR: Mapped[str | None] = mapped_column(String(50))
    PROBATION: Mapped[bool | None] = mapped_column(Boolean, index=True)
    APPLICATION_DATE: Mapped[str | None] = mapped_column(String(50))
    CUM_GPA: Mapped[float | None] = mapped_column(Float, index=True)
    STST_DESC: Mapped[str | None] = mapped_column(String(255))
    STYP_CODE: Mapped[str | None] = mapped_column(String(50))
    STYP_DESC: Mapped[str | None] = mapped_column(String(255))
    ENROLLED_IND: Mapped[bool | None] = mapped_column(Boolean, index=True)
    REGISTERED_IND: Mapped[bool | None] = mapped_column(Boolean, index=True)
    LEVL_CODE: Mapped[str | None] = mapped_column(String(50))
    COLL_CODE: Mapped[str | None] = mapped_column(String(50), index=True)
    TOTAL_CREDIT_HOURS: Mapped[float | None] = mapped_column(Float)
    ASTD_TERM: Mapped[str | None] = mapped_column(String(50))
    ATSD_CODE_END_OF_TERM: Mapped[str | None] = mapped_column(String(50))
    ASTD_DESC: Mapped[str | None] = mapped_column(String(255))
    ASTD_DATE_END_OF_TERM: Mapped[str | None] = mapped_column(String(50))
    USAID: Mapped[bool | None] = mapped_column(Boolean)
    MASTER_CARD: Mapped[bool | None] = mapped_column(Boolean)
    UPP_MEPI: Mapped[bool | None] = mapped_column(Boolean)
    GAS: Mapped[bool | None] = mapped_column(Boolean)
    FINANCIAL_AID: Mapped[bool | None] = mapped_column(Boolean, index=True)
    DORMS: Mapped[bool | None] = mapped_column(Boolean, index=True)
    extra_columns_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    row_hash: Mapped[str | None] = mapped_column(String(128), index=True)
    first_seen_batch_id: Mapped[int | None] = mapped_column(ForeignKey("import_batches.batch_id"))
    last_seen_batch_id: Mapped[int | None] = mapped_column(ForeignKey("import_batches.batch_id"))
    missing_from_latest_import: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    added_to_db_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=utc_now)
    modified_in_db_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class StudentHistory(Base):
    __tablename__ = "students_history"

    history_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    batch_id: Mapped[int | None] = mapped_column(ForeignKey("import_batches.batch_id"), index=True)
    STUD_ID: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    all_excel_columns: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    row_hash: Mapped[str | None] = mapped_column(String(128), index=True)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    valid_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    change_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    batch: Mapped[ImportBatch | None] = relationship(back_populates="history_rows")


class ColumnRegistry(Base, TimestampMixin):
    __tablename__ = "column_registry"

    schema_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    column_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    original_column_name: Mapped[str | None] = mapped_column(String(255))
    detected_type: Mapped[str] = mapped_column(String(50), default="text", nullable=False)
    first_seen_batch_id: Mapped[int | None] = mapped_column(ForeignKey("import_batches.batch_id"))
    last_seen_batch_id: Mapped[int | None] = mapped_column(ForeignKey("import_batches.batch_id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_new_column: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class FileImportLog(Base):
    __tablename__ = "file_import_log"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    batch_id: Mapped[int | None] = mapped_column(ForeignKey("import_batches.batch_id"), index=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    row_number: Mapped[int | None] = mapped_column(Integer)
    STUD_ID: Mapped[str | None] = mapped_column(String(64), index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    batch: Mapped[ImportBatch | None] = relationship(back_populates="import_logs")


class FilterPreset(Base, TimestampMixin):
    __tablename__ = "filter_presets"

    preset_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    preset_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    filter_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)


class FilterRun(Base):
    __tablename__ = "filter_runs"

    filter_run_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    preset_id: Mapped[int | None] = mapped_column(ForeignKey("filter_presets.preset_id"))
    filter_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    result_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class ExportLog(Base):
    __tablename__ = "export_log"

    export_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filter_run_id: Mapped[int | None] = mapped_column(ForeignKey("filter_runs.filter_run_id"), index=True)
    export_path: Mapped[str] = mapped_column(Text, nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class SemanticEmbedding(Base):
    __tablename__ = "semantic_embeddings"

    embedding_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    STUD_ID: Mapped[str] = mapped_column(ForeignKey("students_current.STUD_ID"), nullable=False, index=True)
    source_column: Mapped[str] = mapped_column(String(255), nullable=False)
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    semantic_document_hash: Mapped[str | None] = mapped_column(String(128), index=True)
    embedding_vector_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    embedding_model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    vector_store_name: Mapped[str] = mapped_column(String(80), default="faiss", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class BackupLog(Base):
    __tablename__ = "backup_log"

    backup_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    backup_path: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="created", nullable=False, index=True)
    integrity_check_passed: Mapped[bool | None] = mapped_column(Boolean)
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


Index("ix_students_current_major_class", StudentCurrent.MAJR_DESC, StudentCurrent.CLAS_DESC)
Index("ix_students_current_aid_probation", StudentCurrent.FINANCIAL_AID, StudentCurrent.PROBATION)
