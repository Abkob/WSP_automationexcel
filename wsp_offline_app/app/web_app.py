from __future__ import annotations

import json
import logging
import shutil
import threading
import time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import func
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.components.student_table import build_student_table_rows
from config import AppSettings, ensure_data_directories
from database.schema_manager import infer_column_type, sync_column_registry
from database.db import create_session_factory, create_sqlite_engine, initialize_database
from database.models import BackupLog, ColumnRegistry, FileImportLog, ImportBatch, StudentCurrent
from services.analytics_service import get_dashboard_charts, get_dashboard_metrics, get_latest_import_summary, get_text_and_semantic_analytics
from services.archive_service import archive_and_create_pending_import_batch
from services.backup_service import create_database_backup, verify_database_integrity
from services.excel_importer import (
    DuplicateExcelFileError,
    MissingStudentIdError,
    NoValidStudentRowsError,
    ensure_file_not_previously_imported,
    execute_import_transaction,
    intake_excel_file,
    log_import_event,
    mark_missing_students,
    read_excel_workbook,
    upsert_student_row,
)
from services.excel_schema import SUPPORTED_EXCEL_EXTENSIONS, normalize_header
from services.export_service import export_filtered_results_to_excel
from services.filter_service import (
    BooleanFilter,
    CategoryFilter,
    FilterRequest,
    NumericFilter,
    PaginationSpec,
    SemanticFilter,
    SortSpec,
    TextFilter,
    execute_filter_request,
    log_filter_run,
)
from services.semantic_service import check_ollama_model_availability, rank_student_rows_semantically
from services.semantic_search_service import _is_index_fresh, _reindex_in_progress, mark_index_fresh, mark_index_stale, mark_reindex_started, rank_student_rows_by_ollama_rag, rank_student_rows_by_vector_search, sync_student_semantic_index
from services.value_normalizer import NormalizationWarning, normalize_boolean, normalize_date, normalize_email, normalize_number, normalize_phone_text, normalize_text


DEFAULT_RESULT_COLUMNS = (
    "STUD_ID",
    "STUD_NAME",
    "MAJR_DESC",
    "CLAS_DESC",
    "STUD_EMAIL",
    "CUM_GPA",
    "added_to_db_at",
    "modified_in_db_at",
    "PROBATION",
    "FINANCIAL_AID",
    "DORMS",
    "WSP_TECHNICAL_SKILLS",
    "WSP_PREFERRED_TYPE_OF_WORK",
)
STATIC_DIR = Path(__file__).resolve().parent / "static"
BOOLEAN_IMPORT_FIELDS = {
    "DEANS_WARNING",
    "DEAN_WARN",
    "PROBATION",
    "ENROLLED_IND",
    "REGISTERED_IND",
    "USAID",
    "MASTER_CARD",
    "UPP_MEPI",
    "GAS",
    "FINANCIAL_AID",
    "DORMS",
}
NUMERIC_IMPORT_FIELDS = {"CUM_GPA", "TOTAL_CREDIT_HOURS"}
DATE_IMPORT_FIELDS = {"APPLICATION_DATE", "ASTD_DATE_END_OF_TERM"}
IMPORT_FOLDER_REFRESH_INTERVAL_SECONDS = 30
LOGGER = logging.getLogger(__name__)
IMPORT_FOLDER_REFRESH_LOCK = threading.Lock()


def create_web_app(settings: AppSettings) -> FastAPI:
    initialize_runtime_database(settings)
    _prewarm_embedding_model(settings)
    app = FastAPI(title=settings.app_name)
    app.state.settings = settings
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    if settings.runtime_mode != "testing":
        configure_import_folder_background_refresher(app, settings)

    @app.post("/api/shutdown")
    def api_shutdown() -> dict:
        import os, threading
        threading.Timer(0.4, lambda: os._exit(0)).start()
        return {"status": "shutting down"}

    @app.post("/api/admin/reindex")
    def admin_reindex() -> dict[str, Any]:
        if _reindex_in_progress():
            return {"status": "already_running", "message": "Reindex already in progress"}
        threading.Thread(target=_startup_reindex, args=(settings,), daemon=True, name="manual-reindex").start()
        return {"status": "started", "message": "Full reindex started in background"}

    @app.get("/api/admin/index-status")
    def admin_index_status() -> dict[str, Any]:
        from services.vector_store_service import FaissVectorStore
        store = FaissVectorStore(settings.semantic_index_dir)
        index_count = store.count() if store.vectors_path.exists() else 0
        with open_session(settings) as session:
            db_count = session.query(StudentCurrent).count()
        return {
            "index_count": index_count,
            "db_count": db_count,
            "coverage_pct": round(index_count / db_count * 100, 1) if db_count else 0,
            "reindex_running": _reindex_in_progress(),
            "index_fresh": _is_index_fresh(),
        }

    @app.get("/", response_class=HTMLResponse)
    def dashboard_page() -> str:
        return render_html_shell(settings, active_path="/")

    @app.get("/filters", response_class=HTMLResponse)
    def filters_page() -> str:
        return render_html_shell(settings, active_path="/filters")

    @app.get("/excel-sheets", response_class=HTMLResponse)
    def excel_sheets_page() -> str:
        return render_html_shell(settings, active_path="/excel-sheets")

    @app.get("/import", response_class=HTMLResponse)
    def import_page() -> str:
        return render_html_shell(settings, active_path="/import")

    @app.get("/system-status", response_class=HTMLResponse)
    def system_status_page() -> str:
        return render_html_shell(settings, active_path="/system-status")

    @app.get("/api/dashboard")
    def dashboard_data() -> dict[str, Any]:
        with open_session(settings) as session:
            metrics = get_dashboard_metrics(session)
            charts = get_dashboard_charts(session)
            text_analytics = get_text_and_semantic_analytics(session)
            latest_import = get_latest_import_summary(session)
        return {
            "metrics": asdict(metrics),
            "charts": {
                "students_by_major": chart_points_to_json(charts.students_by_major),
                "students_by_class": chart_points_to_json(charts.students_by_class),
                "gpa_distribution": chart_points_to_json(charts.gpa_distribution),
                "average_gpa_by_major": chart_points_to_json(charts.average_gpa_by_major),
                "probation_by_major": chart_points_to_json(charts.probation_by_major),
                "financial_aid_distribution": chart_points_to_json(charts.financial_aid_distribution),
            },
            "text_analytics": {
                "preferred_work_distribution": text_points_to_json(text_analytics.preferred_work_distribution),
                "technical_skills_frequency": text_points_to_json(text_analytics.technical_skills_frequency),
                "languages_frequency": text_points_to_json(text_analytics.languages_frequency),
            },
            "latest_import": asdict(latest_import) if latest_import else None,
        }

    @app.get("/api/filter-options")
    def filter_options() -> dict[str, Any]:
        with open_session(settings) as session:
            return {
                "majors": load_distinct_text_options(session, "MAJR_DESC"),
                "classes": load_distinct_text_options(session, "CLAS_DESC"),
            }

    @app.post("/api/search")
    def search_students(payload: dict[str, Any]) -> dict[str, Any]:
        request = build_filter_request_from_payload(payload)
        with open_session(settings) as session:
            result = execute_filter_request(
                session,
                request,
                semantic_ranker=lambda sf, rows: rank_student_rows_by_vector_search(settings, session, sf, rows),
            )
            log_filter_run(session, request=request, result_count=result.total_count)
            session.commit()
        return serialize_filter_response(result)

    @app.post("/api/export")
    def export_students(payload: dict[str, Any]) -> dict[str, Any]:
        request = build_filter_request_from_payload(payload, page_size=100_000)
        with open_session(settings) as session:
            result = execute_filter_request(
                session,
                request,
                semantic_ranker=lambda sf, rows: rank_student_rows_by_vector_search(settings, session, sf, rows),
            )
            filter_run = log_filter_run(session, request=request, result_count=result.total_count)
            export_result = export_filtered_results_to_excel(
                result,
                configured_export_dir(settings),
                filename_prefix="filtered_students",
                session=session,
                filter_run_id=filter_run.filter_run_id,
            )
            session.commit()
        return {
            "path": str(export_result.path),
            "row_count": export_result.row_count,
            "columns": export_result.column_names,
        }

    @app.get("/api/excel-sheets")
    def excel_sheets_data() -> dict[str, Any]:
        with open_session(settings) as session:
            return build_excel_sheets_payload(settings, session)

    @app.patch("/api/students/update")
    def update_students(payload: dict[str, Any]) -> dict[str, Any]:
        updates = payload.get("updates", [])
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided.")
        EDITABLE_FIELDS = {"STUD_NAME", "MAJR_DESC", "CLAS_DESC", "CUM_GPA", "STUD_EMAIL", "FINANCIAL_AID", "PROBATION", "DORMS"}
        with open_session(settings) as session:
            create_database_backup(settings.database_path, settings.backup_dir, reason="manual_edit", session=session)
            changed = 0
            for upd in updates:
                stud_id = str(upd.get("stud_id", "")).strip()
                fields = {k: v for k, v in upd.get("fields", {}).items() if k in EDITABLE_FIELDS}
                if not stud_id or not fields:
                    continue
                student = session.query(StudentCurrent).filter(StudentCurrent.STUD_ID == stud_id).first()
                if not student:
                    continue
                for field, value in fields.items():
                    setattr(student, field, value)
                from datetime import timezone
                student.modified_in_db_at = datetime.now(timezone.utc)
                changed += 1
            session.commit()
        return {"updated": changed, "message": f"Saved {changed} student record(s). Backup created automatically."}

    @app.get("/api/backups")
    def list_all_backups() -> dict[str, Any]:
        with open_session(settings) as session:
            backups = (
                session.query(BackupLog)
                .order_by(BackupLog.created_at.desc())
                .limit(50)
                .all()
            )
        archive_folder = import_folder_archive_path(settings)
        excel_archives = []
        if archive_folder.exists():
            excel_archives = [
                {
                    "filename": f.name,
                    "path": str(f),
                    "size": format_bytes(f.stat().st_size),
                    "modified_at": format_datetime_from_timestamp(f.stat().st_mtime),
                }
                for f in sorted(archive_folder.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
                if f.is_file() and f.suffix.lower() in {".xlsx", ".xls"}
            ]
        return {
            "backups": [
                {
                    "path": b.backup_path,
                    "filename": Path(b.backup_path).name if b.backup_path else "—",
                    "reason": b.reason,
                    "status": b.status,
                    "integrity": b.integrity_check_passed,
                    "created_at": format_datetime(b.created_at),
                    "size": format_bytes(Path(b.backup_path).stat().st_size) if b.backup_path and Path(b.backup_path).exists() else "—",
                }
                for b in backups
            ],
            "backup_folder": str(settings.backup_dir),
            "excel_archive_folder": str(archive_folder),
            "excel_archives": excel_archives,
        }

    @app.post("/api/backup/restore")
    def restore_backup_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
        backup_path = Path(str(payload.get("backup_path", ""))).resolve()
        if not backup_path.exists() or not backup_path.is_file():
            raise HTTPException(status_code=404, detail=f"Backup file not found: {backup_path}")
        with open_session(settings) as session:
            create_database_backup(settings.database_path, settings.backup_dir, reason="pre_restore", session=session)
            session.commit()
        engine = create_sqlite_engine(settings.database_path)
        engine.dispose()
        shutil.copy2(str(backup_path), str(settings.database_path))
        new_engine = create_sqlite_engine(settings.database_path)
        initialize_database(new_engine)
        return {"message": f"Database restored from {backup_path.name}. Emergency backup created before restore."}

    @app.get("/api/import-center")
    def import_center_data() -> dict[str, Any]:
        with open_session(settings) as session:
            return build_import_center_payload(settings, session)

    @app.post("/api/import/run")
    def run_import(payload: dict[str, Any]) -> dict[str, Any]:
        source_path = clean_optional_text(payload.get("path"))
        if not source_path:
            raise HTTPException(status_code=400, detail="Import path is required.")
        try:
            result = run_excel_import_from_path(settings, source_path)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except DuplicateExcelFileError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return result

    @app.post("/api/import/refresh-folder")
    def refresh_import_folder() -> dict[str, Any]:
        return refresh_upload_folder_imports(settings)

    @app.post("/api/import-folder")
    def save_import_folder(payload: dict[str, Any]) -> dict[str, Any]:
        folder_path = clean_optional_text(payload.get("path"))
        if not folder_path:
            raise HTTPException(status_code=400, detail="Import Folder path is required.")
        try:
            folder = save_configured_import_folder(settings, folder_path)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        archive_folder = import_folder_archive_path(settings)
        return {
            "folder": str(folder),
            "archive_folder": str(archive_folder),
            "message": "Import Folder saved. Drop Excel files here and the app will consume them automatically.",
        }

    @app.get("/api/system-status")
    def system_status_data() -> dict[str, Any]:
        with open_session(settings) as session:
            return build_system_status_payload(settings, session)

    @app.post("/api/system-status/diagnostics")
    def run_diagnostics_endpoint(payload: dict[str, Any] = {}) -> dict[str, Any]:
        checks = payload.get("checks") or None
        with open_session(settings) as session:
            results = run_diagnostics(settings, session, checks=checks)
        passed = sum(1 for r in results if r["status"] == "pass")
        warned = sum(1 for r in results if r["status"] == "warn")
        failed = sum(1 for r in results if r["status"] == "fail")
        return {"results": results, "passed": passed, "warned": warned, "failed": failed}

    @app.post("/api/system-status/diagnostics/single")
    def run_single_diagnostic_endpoint(payload: dict[str, Any]) -> dict[str, Any]:
        key = str(payload.get("check", ""))
        if key not in DIAGNOSTIC_CHECK_KEYS:
            raise HTTPException(status_code=400, detail=f"Unknown check: {key}")
        with open_session(settings) as session:
            return run_single_diagnostic(key, settings, session)

    @app.get("/api/system-status/diagnostics/checks")
    def list_diagnostic_checks() -> dict[str, Any]:
        labels = {
            "db_connect": "DB Connectivity",
            "db_integrity": "DB Integrity",
            "embedding_model": "Embedding Model",
            "semantic_search": "Semantic Search",
            "import_folder": "Import Folder",
            "export_folder": "Export Folder",
            "backup_vault": "Backup Vault",
            "vector_index": "Vector Index",
        }
        return {"checks": [{"key": k, "label": labels.get(k, k)} for k in DIAGNOSTIC_CHECK_KEYS]}

    return app


def initialize_runtime_database(settings: AppSettings) -> None:
    engine = create_sqlite_engine(settings.database_path)
    initialize_database(engine)


def _prewarm_embedding_model(settings: AppSettings) -> None:
    try:
        from services.embedding_service import get_default_embedding_model
        from services.vector_store_service import FaissVectorStore
        model = get_default_embedding_model(settings)
        model.encode(["warmup"], kind="query")
        LOGGER.info("Embedding model pre-warmed: %s", settings.embedding_model_name)
        store = FaissVectorStore(settings.semantic_index_dir)
        index_count = store.count() if store.vectors_path.exists() else 0
        if index_count > 0:
            # Validate coverage: only mark fresh if the index covers ≥90% of DB students.
            # A stale/partial index (e.g. from a crashed reindex) must NOT be marked fresh
            # or searches will be silently biased to whichever students made it in.
            engine = create_sqlite_engine(settings.database_path)
            initialize_database(engine)
            with engine.connect() as conn:
                db_count = conn.execute(__import__("sqlalchemy").text("SELECT COUNT(*) FROM students_current")).scalar() or 0
            coverage = index_count / db_count if db_count > 0 else 1.0
            if coverage >= 0.90:
                mark_index_fresh()
                LOGGER.info("Existing FAISS index (%d/%d students, %.0f%%) — marked fresh", index_count, db_count, coverage * 100)
            else:
                LOGGER.warning(
                    "FAISS index is stale: %d indexed vs %d in DB (%.0f%% coverage) — scheduling startup reindex",
                    index_count, db_count, coverage * 100,
                )
                threading.Thread(target=_startup_reindex, args=(settings,), daemon=True, name="startup-reindex").start()
    except Exception as exc:
        LOGGER.warning("Embedding model pre-warm skipped: %s", exc)


def _startup_reindex(settings: AppSettings, chunk_size: int = 200) -> None:
    try:
        mark_reindex_started()
        engine = create_sqlite_engine(settings.database_path)
        initialize_database(engine)
        from sqlalchemy.orm import Session as _Session
        from services.embedding_service import get_default_embedding_model
        from services.vector_store_service import FaissVectorStore
        from services.semantic_document_service import build_student_semantic_profiles
        from services.semantic_search_service import (
            load_existing_semantic_rows, profile_needs_embedding,
            upsert_semantic_embedding_rows,
        )
        from services.vector_store_service import VectorRecord
        model = get_default_embedding_model(settings)
        store = FaissVectorStore(settings.semantic_index_dir, collection_name="students")

        with _Session(engine) as session:
            all_students = (
                session.query(StudentCurrent)
                .filter(StudentCurrent.missing_from_latest_import == False)
                .all()
            )
            profiles = build_student_semantic_profiles(all_students)
            existing_rows = load_existing_semantic_rows(session, model.model_name)
            indexed_ids = store.record_ids()
            changed = [p for p in profiles if profile_needs_embedding(p, existing_rows.get(p.STUD_ID), indexed_ids)]
            LOGGER.info("Startup reindex: %d students need encoding", len(changed))

            for i in range(0, len(changed), chunk_size):
                chunk = changed[i:i + chunk_size]
                vectors = model.encode([p.text for p in chunk], kind="document")
                records = tuple(
                    VectorRecord(
                        record_id=p.STUD_ID,
                        embedding=vectors[j],
                        metadata=p.metadata | {"semantic_hash": p.document_hash, "model_name": model.model_name},
                        document=p.text,
                    )
                    for j, p in enumerate(chunk)
                )
                store.upsert(records)
                upsert_semantic_embedding_rows(session, chunk, model_name=model.model_name, vector_store_name=store.vector_store_name)
                session.commit()
                LOGGER.info("Startup reindex: %d/%d done", min(i + chunk_size, len(changed)), len(changed))

        mark_index_fresh()
        LOGGER.info("Startup reindex complete")
    except Exception as exc:
        LOGGER.error("Startup reindex failed: %s", exc)
        mark_index_stale()


def open_session(settings: AppSettings):
    engine = create_sqlite_engine(settings.database_path)
    initialize_database(engine)
    return create_session_factory(engine)()


def configure_import_folder_background_refresher(app: FastAPI, settings: AppSettings) -> None:
    @app.on_event("startup")
    def start_import_folder_refresher() -> None:
        stop_event = threading.Event()
        app.state.import_folder_stop_event = stop_event

        def worker() -> None:
            if stop_event.wait(5):
                return
            while not stop_event.is_set():
                try:
                    refresh_upload_folder_imports(settings, automatic=True)
                except Exception:
                    LOGGER.exception("Import Folder background refresh failed.")
                stop_event.wait(IMPORT_FOLDER_REFRESH_INTERVAL_SECONDS)

        thread = threading.Thread(target=worker, name="wsp-import-folder-refresher", daemon=True)
        app.state.import_folder_thread = thread
        thread.start()

    @app.on_event("shutdown")
    def stop_import_folder_refresher() -> None:
        stop_event = getattr(app.state, "import_folder_stop_event", None)
        if stop_event is not None:
            stop_event.set()


def read_import_folder_config(settings: AppSettings) -> dict[str, Any]:
    path = settings.import_folder_config_path
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def resolve_user_folder_path(settings: AppSettings, folder_path: str | Path) -> Path:
    path = Path(folder_path).expanduser()
    if not path.is_absolute():
        path = settings.project_root.parent / path
    return path.resolve()


def configured_import_folder(settings: AppSettings) -> Path:
    config = read_import_folder_config(settings)
    configured_path = clean_optional_text(config.get("import_folder_path"))
    if configured_path:
        return resolve_user_folder_path(settings, configured_path)
    return settings.incoming_excel_dir.resolve()


def import_folder_archive_path(settings: AppSettings) -> Path:
    return configured_import_folder(settings) / "archive"


def configured_export_dir(settings: AppSettings) -> Path:
    export_dir = configured_import_folder(settings).parent / "Export Folder"
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir


def ensure_import_folder_ready(settings: AppSettings) -> Path:
    folder = configured_import_folder(settings)
    archive = import_folder_archive_path(settings)
    for directory in (folder, archive):
        if directory.exists() and not directory.is_dir():
            raise NotADirectoryError(f"Import Folder path exists but is not a directory: {directory}")
        directory.mkdir(parents=True, exist_ok=True)
    return folder


def save_configured_import_folder(settings: AppSettings, folder_path: str | Path) -> Path:
    ensure_data_directories(settings)
    folder = resolve_user_folder_path(settings, folder_path)
    archive = folder / "archive"
    for directory in (folder, archive):
        if directory.exists() and not directory.is_dir():
            raise NotADirectoryError(f"Import Folder path exists but is not a directory: {directory}")
        directory.mkdir(parents=True, exist_ok=True)
    settings.import_folder_config_path.write_text(
        json.dumps({"import_folder_path": str(folder)}, indent=2),
        encoding="utf-8",
    )
    return folder


def run_excel_import_from_path(settings: AppSettings, source_path: str | Path, *, archive_dir: Path | None = None) -> dict[str, Any]:
    mark_index_stale()
    ensure_data_directories(settings)
    engine = create_sqlite_engine(settings.database_path)
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    intake = intake_excel_file(source_path, poll_interval_seconds=0.05, timeout_seconds=5.0)

    with session_factory() as session:
        file_hash = ensure_file_not_previously_imported(session, intake.path)
        create_database_backup(settings.database_path, settings.backup_dir, reason="pre_import", session=session)
        batch = archive_and_create_pending_import_batch(
            session,
            intake.path,
            archive_dir or settings.original_excel_archive_dir,
            file_hash=file_hash,
        )
        session.commit()
        batch_id = batch.batch_id

    workbook = read_excel_workbook(intake.path)

    def operation(session, batch):
        if workbook.row_count == 0:
            raise NoValidStudentRowsError(
                f"Import rejected: {intake.path.name} has headers but no student rows. "
                "Add at least one row with a usable STUD_ID before importing."
            )

        inferred_types = {
            normalize_header(header): infer_column_type(row.get(header) for row in workbook.rows)
            for header in workbook.headers
            if normalize_header(header)
        }
        original_names = {
            normalize_header(header): header
            for header in workbook.headers
            if normalize_header(header)
        }
        schema_result = sync_column_registry(
            session,
            workbook.headers,
            batch_id=batch.batch_id,
            inferred_types=inferred_types,
            original_names=original_names,
        )
        change_counts = {
            "new_student": 0,
            "updated_student": 0,
            "unchanged_student": 0,
            "restored_student": 0,
            "row_rejected": 0,
        }
        seen_student_ids: set[str] = set()
        warnings: list[NormalizationWarning] = []

        for row_number, row in enumerate(workbook.rows, start=2):
            normalized_row = normalize_import_row(row, row_number=row_number, warnings=warnings)
            try:
                result = upsert_student_row(session, normalized_row, batch_id=batch.batch_id)
            except MissingStudentIdError as exc:
                change_counts["row_rejected"] += 1
                log_import_event(
                    session,
                    batch_id=batch.batch_id,
                    event_type="row_rejected",
                    row_number=row_number,
                    message=str(exc),
                    details_json={"reason": "missing_stud_id"},
                )
                continue
            seen_student_ids.add(result.stud_id)
            change_counts[result.change_type] += 1

        for warning in warnings[:200]:
            log_import_event(
                session,
                batch_id=batch.batch_id,
                event_type="normalization_warning",
                row_number=warning.row_number,
                message=f"{warning.column_name}: {warning.message}",
                details_json={"raw_value": str(warning.raw_value)},
            )

        if not seen_student_ids:
            raise NoValidStudentRowsError(
                f"Import rejected: {intake.path.name} contains {workbook.row_count} row(s), "
                "but none had a usable STUD_ID. Active students were left unchanged."
            )

        missing_result = mark_missing_students(
            session,
            seen_student_ids=seen_student_ids,
            batch_id=batch.batch_id,
        )
        batch.number_of_rows = workbook.row_count
        batch.number_of_columns = workbook.column_count
        batch.new_rows = change_counts["new_student"]
        batch.updated_rows = change_counts["updated_student"]
        batch.unchanged_rows = change_counts["unchanged_student"] + change_counts["restored_student"]
        batch.missing_rows = len(missing_result.newly_missing_student_ids)
        batch.new_columns_detected = list(schema_result.new_columns)
        batch.missing_columns_detected = list(schema_result.missing_columns)
        log_import_event(
            session,
            batch_id=batch.batch_id,
            event_type="import_completed",
            message=(
                f"Imported {workbook.row_count} rows: {batch.new_rows} new, "
                f"{batch.updated_rows} updated/restored, {batch.unchanged_rows} unchanged, "
                f"{batch.missing_rows} newly missing."
            ),
            details_json={
                "sheet": workbook.active_sheet,
                "warnings": len(warnings),
                "rejected_rows": change_counts["row_rejected"],
            },
        )
        return {
            "batch_id": batch.batch_id,
            "filename": batch.filename,
            "status": "completed",
            "rows": workbook.row_count,
            "columns": workbook.column_count,
            "new_rows": batch.new_rows,
            "updated_rows": batch.updated_rows,
            "unchanged_rows": batch.unchanged_rows,
            "missing_rows": batch.missing_rows,
            "new_columns": list(schema_result.new_columns),
            "missing_columns": list(schema_result.missing_columns),
            "warnings": len(warnings),
            "rejected_rows": change_counts["row_rejected"],
        }

    result = execute_import_transaction(session_factory, batch_id=batch_id, operation=operation)

    with session_factory() as session:
        create_database_backup(settings.database_path, settings.backup_dir, reason="post_import", session=session)
        session.commit()

    def _background_reindex() -> None:
        try:
            with session_factory() as bg_session:
                active_students = (
                    bg_session.query(StudentCurrent)
                    .filter(StudentCurrent.missing_from_latest_import == False)
                    .all()
                )
                sync_student_semantic_index(bg_session, settings, active_students)
                bg_session.commit()
            mark_index_fresh()
        except Exception:
            pass  # never crash the import response; search will lazy-sync on next query

    mark_reindex_started()
    threading.Thread(target=_background_reindex, daemon=True, name="semantic-reindex").start()

    return result


def refresh_upload_folder_imports(settings: AppSettings, *, automatic: bool = False) -> dict[str, Any]:
    ensure_data_directories(settings)
    folder = ensure_import_folder_ready(settings)
    archive_folder = import_folder_archive_path(settings)
    if not IMPORT_FOLDER_REFRESH_LOCK.acquire(blocking=False):
        return {
            "folder": str(folder),
            "archive_folder": str(archive_folder),
            "checked": 0,
            "imported": 0,
            "skipped": 0,
            "failed": 0,
            "busy": True,
            "results": [],
            "archived_files": [],
            "message": "Import Folder refresh is already running.",
        }

    try:
        return consume_import_folder(settings, folder=folder, archive_folder=archive_folder, automatic=automatic)
    finally:
        IMPORT_FOLDER_REFRESH_LOCK.release()


def consume_import_folder(settings: AppSettings, *, folder: Path, archive_folder: Path, automatic: bool) -> dict[str, Any]:
    candidates = tuple(reversed(find_upload_folder_candidates(settings)))
    results: list[dict[str, Any]] = []
    newest_candidate = max(candidates, key=lambda path: path.stat().st_mtime, default=None)
    accepted_current: Path | None = None

    for candidate in candidates:
        try:
            import_result = run_excel_import_from_path(settings, candidate, archive_dir=archive_folder)
            accepted_current = candidate
            results.append(
                {
                    "path": str(candidate),
                    "filename": candidate.name,
                    "status": "imported",
                    "batch_id": import_result["batch_id"],
                    "new_rows": import_result["new_rows"],
                    "updated_rows": import_result["updated_rows"],
                    "unchanged_rows": import_result["unchanged_rows"],
                    "missing_rows": import_result["missing_rows"],
                }
            )
        except DuplicateExcelFileError as exc:
            accepted_current = candidate
            results.append(
                {
                    "path": str(candidate),
                    "filename": candidate.name,
                    "status": "skipped_duplicate",
                    "message": str(exc),
                }
            )
        except Exception as exc:
            results.append(
                {
                    "path": str(candidate),
                    "filename": candidate.name,
                    "status": "failed",
                    "message": str(exc),
                }
            )

    archived_files: list[dict[str, str]] = []
    if accepted_current is not None and newest_candidate is not None and accepted_current.resolve() == newest_candidate.resolve():
        archived_files = archive_retired_import_folder_files(settings, keep_path=accepted_current)

    return {
        "folder": str(folder),
        "archive_folder": str(archive_folder),
        "active_file": str(accepted_current) if accepted_current else None,
        "checked": len(candidates),
        "imported": sum(1 for item in results if item["status"] == "imported"),
        "skipped": sum(1 for item in results if item["status"] == "skipped_duplicate"),
        "failed": sum(1 for item in results if item["status"] == "failed"),
        "busy": False,
        "automatic": automatic,
        "results": results,
        "archived_files": archived_files,
    }


def archive_retired_import_folder_files(settings: AppSettings, *, keep_path: Path) -> list[dict[str, str]]:
    folder = configured_import_folder(settings)
    archive_folder = import_folder_archive_path(settings)
    keep = keep_path.resolve()
    archived_files: list[dict[str, str]] = []

    for candidate in find_upload_folder_candidates(settings):
        if candidate.resolve() == keep:
            continue
        if candidate.parent.resolve() != folder.resolve():
            continue
        target = build_import_folder_archive_target(archive_folder, candidate)
        shutil.move(str(candidate), str(target))
        archived_files.append(
            {
                "filename": candidate.name,
                "archived_to": str(target),
            }
        )
    return archived_files


def build_import_folder_archive_target(archive_folder: Path, source_path: Path) -> Path:
    archive_folder.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = archive_folder / f"{timestamp}_retired_{source_path.name}"
    counter = 1
    while target.exists():
        target = archive_folder / f"{timestamp}_retired_{source_path.stem}_{counter}{source_path.suffix}"
        counter += 1
    return target


def normalize_import_row(row: dict[str, object | None], *, row_number: int, warnings: list[NormalizationWarning]) -> dict[str, object | None]:
    normalized: dict[str, object | None] = {}
    for raw_column, value in row.items():
        column = normalize_header(raw_column) or str(raw_column)
        if column in BOOLEAN_IMPORT_FIELDS:
            normalized[column] = normalize_boolean(value, column_name=column, row_number=row_number, warnings=warnings)
        elif column in NUMERIC_IMPORT_FIELDS:
            normalized[column] = normalize_number(value, column_name=column, row_number=row_number, warnings=warnings)
        elif column in DATE_IMPORT_FIELDS:
            normalized[column] = normalize_date(value, column_name=column, row_number=row_number, warnings=warnings)
        elif column == "STUD_EMAIL":
            normalized[column] = normalize_email(value)
        elif column == "MOBILE_NBR":
            normalized[column] = normalize_phone_text(value)
        else:
            normalized[column] = normalize_text(value)
    return normalized


def build_excel_sheets_payload(settings: AppSettings, session) -> dict[str, Any]:
    students = (
        session.query(StudentCurrent)
        .order_by(StudentCurrent.STUD_ID.asc())
        .all()
    )
    rejected_logs = (
        session.query(FileImportLog)
        .filter(FileImportLog.event_type.in_(("row_rejected", "normalization_warning")))
        .order_by(FileImportLog.created_at.desc())
        .limit(50)
        .all()
    )
    columns = (
        session.query(ColumnRegistry)
        .order_by(ColumnRegistry.is_active.desc(), ColumnRegistry.column_name.asc())
        .limit(100)
        .all()
    )
    major_counts = (
        session.query(StudentCurrent.MAJR_DESC, func.count(StudentCurrent.internal_id))
        .filter(StudentCurrent.missing_from_latest_import.is_(False))
        .group_by(StudentCurrent.MAJR_DESC)
        .order_by(func.count(StudentCurrent.internal_id).desc(), StudentCurrent.MAJR_DESC.asc())
        .limit(30)
        .all()
    )

    sheets = [
        {
            "key": "Student_Directory",
            "label": "Current Students",
            "description": "Read-only database view used by Filtering",
            "headers": ["ID", "Name", "Major", "Class", "GPA", "Added", "Modified", "Email", "Aid", "Probation", "Dorms"],
            "rows": [
                [
                    student.STUD_ID,
                    student.STUD_NAME,
                    student.MAJR_DESC,
                    student.CLAS_DESC,
                    format_optional_number(student.CUM_GPA),
                    format_datetime(student.added_to_db_at),
                    format_datetime(student.modified_in_db_at),
                    student.STUD_EMAIL,
                    format_bool(student.FINANCIAL_AID),
                    format_bool(student.PROBATION),
                    format_bool(student.DORMS),
                ]
                for student in students
            ],
        },
        {
            "key": "Skipped_Rows",
            "label": "Import Issues",
            "description": "Rejected rows and normalization warnings from imports",
            "headers": ["Time", "Batch", "Row", "Student ID", "Event", "Message"],
            "rows": [
                [
                    format_datetime(log.created_at),
                    log.batch_id or "",
                    log.row_number or "",
                    log.STUD_ID or "",
                    log.event_type,
                    log.message,
                ]
                for log in rejected_logs
            ],
        },
        {
            "key": "Column_Schema",
            "label": "Column Schema",
            "description": "Registered workbook columns and DB mappings",
            "headers": ["Column", "Detected Type", "Status", "First Batch", "Last Batch", "Notes"],
            "rows": [
                [
                    column.column_name,
                    column.detected_type,
                    "Active" if column.is_active else "Missing",
                    column.first_seen_batch_id or "",
                    column.last_seen_batch_id or "",
                    column.notes or "",
                ]
                for column in columns
            ],
        },
        {
            "key": "Major_Analytics",
            "label": "Major Analytics",
            "description": "Database-generated distribution by major",
            "headers": ["Major", "Student Count"],
            "rows": [
                [major or "Unknown", count]
                for major, count in major_counts
            ],
        },
    ]
    latest_import = get_latest_import_summary(session)
    return {
        "source_map": [
            {
                "label": "Import Folder",
                "value": str(configured_import_folder(settings)),
                "detail": "Drop the daily workbook here; the app consumes it automatically.",
            },
            {
                "label": "Current workbook source",
                "value": latest_import.filename if latest_import else "No completed import yet",
                "detail": "Only imported workbook data reaches the database.",
            },
            {
                "label": "Filtering source",
                "value": "SQLite students_current",
                "detail": "The filtering page reads this table, not raw Excel files.",
            },
            {
                "label": "Filtered exports",
                "value": str(configured_export_dir(settings)),
                "detail": "Export creates Excel files with Filtered Results and Filter Metadata sheets.",
            },
        ],
        "sheets": sheets,
    }


def build_import_center_payload(settings: AppSettings, session) -> dict[str, Any]:
    import_folder = ensure_import_folder_ready(settings)
    archive_folder = import_folder_archive_path(settings)
    latest_import = get_latest_import_summary(session)
    recent_batches = (
        session.query(ImportBatch)
        .order_by(ImportBatch.imported_at.desc())
        .limit(8)
        .all()
    )
    recent_logs = (
        session.query(FileImportLog)
        .order_by(FileImportLog.created_at.desc())
        .limit(12)
        .all()
    )
    recent_backups = (
        session.query(BackupLog)
        .order_by(BackupLog.created_at.desc())
        .limit(6)
        .all()
    )
    columns = (
        session.query(ColumnRegistry)
        .order_by(ColumnRegistry.is_active.desc(), ColumnRegistry.column_name.asc())
        .limit(16)
        .all()
    )
    current_files = find_upload_folder_candidates(settings)
    current_file = current_files[0] if current_files else None
    return {
        "paths": {
            "watched_folder": str(import_folder),
            "upload_folder": str(import_folder),
            "import_folder": str(import_folder),
            "export_folder": str(configured_export_dir(settings)),
            "backup_folder": str(settings.backup_dir),
            "archive_folder": str(archive_folder),
            "legacy_archive_folder": str(settings.original_excel_archive_dir),
            "default_workbook": str(default_workbook_path(settings)),
        },
        "import_folder": {
            "path": str(import_folder),
            "archive_folder": str(archive_folder),
            "current_file": serialize_file_candidate(current_file, settings) if current_file else None,
            "root_file_count": len(current_files),
            "archive_file_count": count_excel_files(archive_folder),
            "poll_interval_seconds": IMPORT_FOLDER_REFRESH_INTERVAL_SECONDS,
            "instructions": "Drop the newest Excel workbook into this folder. The app imports it, keeps it as the current workbook, and moves older workbook files into archive.",
        },
        "candidate_files": [str(path) for path in find_excel_candidates(settings)],
        "candidate_file_options": [serialize_file_candidate(path, settings) for path in find_excel_candidates(settings)],
        "upload_folder_files": [serialize_file_candidate(path, settings) for path in find_upload_folder_candidates(settings)],
        "backup_policy": {
            "pre_import": "Created before the database is changed.",
            "archive": "Older workbook files move into the Import Folder archive after the newest file is accepted.",
            "transaction": "Rows merge in one transaction; failed imports roll back.",
            "post_import": "Created after successful imports so the new state is recoverable.",
        },
        "auto_refresh": {
            "enabled": True,
            "interval_seconds": IMPORT_FOLDER_REFRESH_INTERVAL_SECONDS,
            "folder": str(import_folder),
        },
        "latest_import": asdict(latest_import) if latest_import else None,
        "recent_batches": [serialize_import_batch(batch) for batch in recent_batches],
        "recent_logs": [serialize_import_log(log) for log in recent_logs],
        "recent_backups": [serialize_backup_log(backup) for backup in recent_backups],
        "columns": [serialize_column_registry(column) for column in columns],
    }


def build_system_status_payload(settings: AppSettings, session) -> dict[str, Any]:
    import sys, platform, shutil as _shutil

    db_exists = settings.database_path.exists()
    db_size = settings.database_path.stat().st_size if db_exists else 0
    student_count = session.query(StudentCurrent).count()
    active_count = session.query(StudentCurrent).filter(StudentCurrent.missing_from_latest_import.is_(False)).count()
    batch_count = session.query(ImportBatch).count()
    backup_count = session.query(BackupLog).count()
    latest_batch = session.query(ImportBatch).order_by(ImportBatch.imported_at.desc()).first()
    latest_backup = session.query(BackupLog).order_by(BackupLog.created_at.desc()).first()

    from database.models import SemanticEmbedding
    indexed_count = session.query(SemanticEmbedding).count()
    index_dir = settings.semantic_index_dir
    index_size = sum(f.stat().st_size for f in index_dir.glob("*") if f.is_file()) if index_dir.exists() else 0

    disk = _shutil.disk_usage(settings.project_root)

    return {
        "health": {
            "students": {"active": active_count, "total": student_count},
            "database": {"ok": db_exists, "size": format_bytes(db_size)},
            "last_import": format_datetime(latest_batch.imported_at) if latest_batch else None,
            "import_filename": latest_batch.filename if latest_batch else None,
            "import_count": batch_count,
            "backup_count": backup_count,
            "latest_backup": format_datetime(latest_backup.created_at) if latest_backup else None,
            "indexed_students": indexed_count,
        },
        "system": {
            "python_version": sys.version.split()[0],
            "platform": platform.system() + " " + platform.release(),
            "embedding_model": settings.embedding_model_name,
            "database_path": str(settings.database_path),
            "database_size": format_bytes(db_size),
            "index_path": str(index_dir),
            "index_size": format_bytes(index_size),
            "import_folder": str(configured_import_folder(settings)),
            "export_folder": str(configured_export_dir(settings)),
            "backup_folder": str(settings.backup_dir),
            "disk_total": format_bytes(disk.total),
            "disk_free": format_bytes(disk.free),
            "disk_used_pct": int(disk.used / disk.total * 100),
            "port": settings.ui_port,
        },
    }


DIAGNOSTIC_CHECK_KEYS = [
    "db_connect", "db_integrity", "embedding_model", "semantic_search",
    "import_folder", "export_folder", "backup_vault", "vector_index",
]


def run_single_diagnostic(key: str, settings: AppSettings, session) -> dict[str, Any]:
    import time as _time, shutil as _shutil
    from pathlib import Path as _Path

    t = _time.perf_counter()

    def elapsed():
        return int((_time.perf_counter() - t) * 1000)

    try:
        if key == "db_connect":
            total = session.query(StudentCurrent).count()
            active = session.query(StudentCurrent).filter(StudentCurrent.missing_from_latest_import.is_(False)).count()
            missing = total - active
            batches = session.query(ImportBatch).count()
            backups = session.query(BackupLog).count()
            return {
                "key": key, "name": "Database connectivity", "status": "pass",
                "value": f"{active} active / {total} total",
                "detail": "SQLite connection healthy. All tables accessible.",
                "ms": elapsed(),
                "details": {
                    "Active students": active, "Total rows": total,
                    "Missing students": missing, "Import batches": batches, "Backup records": backups,
                },
            }

        if key == "db_integrity":
            import sqlite3
            ok = verify_database_integrity(settings.database_path)
            conn = sqlite3.connect(str(settings.database_path))
            cur = conn.cursor()
            journal = cur.execute("PRAGMA journal_mode").fetchone()[0]
            page_size = cur.execute("PRAGMA page_size").fetchone()[0]
            page_count = cur.execute("PRAGMA page_count").fetchone()[0]
            wal_size = 0
            wal_path = _Path(str(settings.database_path) + "-wal")
            if wal_path.exists():
                wal_size = wal_path.stat().st_size
            conn.close()
            db_size = settings.database_path.stat().st_size if settings.database_path.exists() else 0
            return {
                "key": key, "name": "Database integrity",
                "status": "pass" if ok else "fail",
                "value": "Passed" if ok else "FAILED",
                "detail": f"PRAGMA integrity_check {'passed' if ok else 'FAILED'}.",
                "ms": elapsed(),
                "details": {
                    "Integrity": "OK" if ok else "FAILED", "Journal mode": journal.upper(),
                    "Page size": f"{page_size:,} B", "Pages": f"{page_count:,}",
                    "DB size": format_bytes(db_size), "WAL size": format_bytes(wal_size) if wal_size else "none",
                },
            }

        if key == "embedding_model":
            import time as _t2
            from services.embedding_service import get_default_embedding_model
            model = get_default_embedding_model(settings)
            test_texts = ["student with Python and data analysis skills", "design and visual communication", "research and writing"]
            t2 = _t2.perf_counter()
            vecs = model.encode(test_texts, kind="document")
            encode_ms = int((_t2.perf_counter() - t2) * 1000)
            dims = vecs.shape[1]
            model_slug = settings.embedding_model_name.replace("/", "--")
            cache_dir = _Path.home() / ".cache" / "huggingface" / "hub" / f"models--{model_slug}"
            cache_size = sum(f.stat().st_size for f in (cache_dir / "blobs").glob("*") if f.is_file()) if (cache_dir / "blobs").exists() else 0
            return {
                "key": key, "name": "Embedding model", "status": "pass",
                "value": f"{dims}-dim",
                "detail": f"Encoded {len(test_texts)} sentences in {encode_ms}ms.",
                "ms": elapsed(),
                "details": {
                    "Model": settings.embedding_model_name.split("/")[-1],
                    "Dimensions": dims, "Texts encoded": len(test_texts),
                    "Encode time": f"{encode_ms}ms ({encode_ms // len(test_texts)}ms/text)",
                    "Cache size": format_bytes(cache_size),
                    "Offline mode": "Yes" if settings.embedding_local_files_only else "No",
                },
            }

        if key == "semantic_search":
            from services.filter_service import SemanticFilter
            from services.semantic_search_service import rank_student_rows_by_vector_search
            import time as _t2
            rows = tuple(session.query(StudentCurrent).filter(StudentCurrent.missing_from_latest_import.is_(False)).limit(20).all())
            if not rows:
                return {"key": key, "name": "Semantic search", "status": "warn", "value": "No students",
                        "detail": "Import a workbook to enable semantic search.", "ms": elapsed(), "details": {}}
            query = "students with technical and communication skills"
            sf = SemanticFilter(query, top_k=5, minimum_score=0.0)
            t2 = _t2.perf_counter()
            matches = rank_student_rows_by_vector_search(settings, session, sf, rows)
            search_ms = int((_t2.perf_counter() - t2) * 1000)
            top = matches[0] if matches else None
            top_row = next((r for r in rows if r.STUD_ID == top.STUD_ID), None) if top else None
            return {
                "key": key, "name": "Semantic search", "status": "pass",
                "value": f"{len(matches)} matches",
                "detail": f"Full pipeline over {len(rows)} students in {search_ms}ms.",
                "ms": elapsed(),
                "details": {
                    "Query": f'"{query}"', "Candidates": len(rows), "Matches": len(matches),
                    "Top result": f"{top_row.STUD_NAME} ({top.score:.2f})" if top_row else "—",
                    "Search time": f"{search_ms}ms",
                },
            }

        if key == "import_folder":
            folder = configured_import_folder(settings)
            exists = folder.exists()
            files = []
            archive_count = 0
            if exists:
                files = sorted(
                    [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in {".xlsx", ".xls"}],
                    key=lambda f: f.stat().st_mtime, reverse=True,
                )
                archive = folder / "archive"
                archive_count = sum(1 for f in archive.iterdir() if f.is_file()) if archive.exists() else 0
            latest = files[0].name if files else "None"
            return {
                "key": key, "name": "Import folder",
                "status": "pass" if exists else "warn",
                "value": f"{len(files)} workbook(s)" if exists else "Not found",
                "detail": str(folder),
                "ms": elapsed(),
                "details": {
                    "Path": str(folder), "Active workbooks": len(files),
                    "Latest file": latest, "Archive count": archive_count,
                    "Auto-refresh": "30s",
                },
            }

        if key == "export_folder":
            export_dir = configured_export_dir(settings)
            exists = export_dir.exists()
            exports = sorted(export_dir.glob("*.xlsx"), key=lambda f: f.stat().st_mtime, reverse=True) if exists else []
            free = _shutil.disk_usage(export_dir).free if exists else 0
            latest = exports[0].name if exports else "None"
            return {
                "key": key, "name": "Export folder",
                "status": "pass" if exists else "warn",
                "value": f"{len(exports)} exports" if exists else "Not found",
                "detail": f"{format_bytes(free)} free on disk",
                "ms": elapsed(),
                "details": {
                    "Path": str(export_dir), "Total exports": len(exports),
                    "Latest export": latest, "Disk free": format_bytes(free),
                },
            }

        if key == "backup_vault":
            count = session.query(BackupLog).count()
            latest = session.query(BackupLog).order_by(BackupLog.created_at.desc()).first()
            pre = session.query(BackupLog).filter(BackupLog.reason == "pre_import").count()
            post = session.query(BackupLog).filter(BackupLog.reason == "post_import").count()
            if not latest:
                return {"key": key, "name": "Backup vault", "status": "warn", "value": "No backups",
                        "detail": "Run an import to generate the first backup.", "ms": elapsed(), "details": {}}
            age_h = (datetime.utcnow() - latest.created_at.replace(tzinfo=None)).total_seconds() / 3600
            backup_size = _Path(latest.backup_path).stat().st_size if _Path(latest.backup_path).exists() else 0
            return {
                "key": key, "name": "Backup vault",
                "status": "pass" if age_h < 48 else "warn",
                "value": f"{count} backups",
                "detail": f"Latest backup {age_h:.1f}h ago — {format_bytes(backup_size)}",
                "ms": elapsed(),
                "details": {
                    "Total backups": count, "Pre-import": pre, "Post-import": post,
                    "Latest": format_datetime(latest.created_at),
                    "Latest size": format_bytes(backup_size),
                    "Age": f"{age_h:.1f}h ago",
                },
            }

        if key == "vector_index":
            from database.models import SemanticEmbedding
            total_students = session.query(StudentCurrent).filter(StudentCurrent.missing_from_latest_import.is_(False)).count()
            indexed = session.query(SemanticEmbedding).filter(
                SemanticEmbedding.embedding_model_name == settings.embedding_model_name
            ).count()
            index_dir = settings.semantic_index_dir
            index_size = sum(f.stat().st_size for f in index_dir.glob("*") if f.is_file()) if index_dir.exists() else 0
            latest_row = session.query(SemanticEmbedding).order_by(SemanticEmbedding.embedding_id.desc()).first()
            status = "pass" if indexed == total_students else ("warn" if indexed > 0 else "warn")
            return {
                "key": key, "name": "Vector index",
                "status": status,
                "value": f"{indexed} / {total_students} indexed",
                "detail": f"FAISS index: {format_bytes(index_size)}",
                "ms": elapsed(),
                "details": {
                    "Indexed students": indexed, "Active students": total_students,
                    "Coverage": f"{int(indexed/total_students*100) if total_students else 0}%",
                    "Index size": format_bytes(index_size),
                    "Model": settings.embedding_model_name.split("/")[-1],
                    "Last updated": format_datetime(latest_row.updated_at) if latest_row and hasattr(latest_row, "updated_at") else "—",
                },
            }

        return {"key": key, "name": key, "status": "fail", "value": "Unknown check", "detail": f"No check named '{key}'", "ms": 0, "details": {}}

    except Exception as exc:
        return {"key": key, "name": key, "status": "fail", "value": "Error", "detail": str(exc), "ms": elapsed(), "details": {}}


def run_diagnostics(settings: AppSettings, session, checks: list[str] | None = None) -> list[dict[str, Any]]:
    keys = checks if checks else DIAGNOSTIC_CHECK_KEYS
    return [run_single_diagnostic(k, settings, session) for k in keys]


def find_excel_candidates(settings: AppSettings) -> tuple[Path, ...]:
    candidates: list[Path] = []
    for folder in (configured_import_folder(settings), settings.project_root.parent, settings.project_root):
        if not folder.exists() or not folder.is_dir():
            continue
        candidates.extend(
            path.resolve()
            for path in folder.iterdir()
            if path.is_file()
            and path.suffix.lower() in SUPPORTED_EXCEL_EXTENSIONS
            and not path.name.startswith("~$")
        )
    unique = {str(path): path for path in candidates}
    return tuple(sorted(unique.values(), key=lambda path: path.stat().st_mtime, reverse=True)[:20])


def find_upload_folder_candidates(settings: AppSettings) -> tuple[Path, ...]:
    ensure_import_folder_ready(settings)
    folder = configured_import_folder(settings)
    return tuple(
        sorted(
            (
                path.resolve()
                for path in folder.iterdir()
                if path.is_file()
                and path.suffix.lower() in SUPPORTED_EXCEL_EXTENSIONS
                and not path.name.startswith("~$")
            ),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
    )


def serialize_file_candidate(path: Path, settings: AppSettings) -> dict[str, Any]:
    import_folder = configured_import_folder(settings)
    source = "Import Folder" if path.parent.resolve() == import_folder.resolve() else "Workspace"
    return {
        "path": str(path),
        "filename": path.name,
        "source": source,
        "modified_at": format_datetime_from_timestamp(path.stat().st_mtime),
        "size": format_bytes(path.stat().st_size),
    }


def default_workbook_path(settings: AppSettings) -> Path:
    candidates = find_upload_folder_candidates(settings)
    if candidates:
        return candidates[0]
    return configured_import_folder(settings) / "WSP.xlsx"


def count_excel_files(folder: Path) -> int:
    if not folder.exists() or not folder.is_dir():
        return 0
    return sum(
        1
        for path in folder.iterdir()
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXCEL_EXTENSIONS
        and not path.name.startswith("~$")
    )


def serialize_import_batch(batch: ImportBatch) -> dict[str, Any]:
    return {
        "batch_id": batch.batch_id,
        "filename": batch.filename,
        "status": batch.status,
        "imported_at": format_datetime(batch.imported_at),
        "rows": batch.number_of_rows,
        "columns": batch.number_of_columns,
        "new_rows": batch.new_rows,
        "updated_rows": batch.updated_rows,
        "unchanged_rows": batch.unchanged_rows,
        "missing_rows": batch.missing_rows,
        "error_message": batch.error_message,
    }


def serialize_import_log(log: FileImportLog) -> dict[str, Any]:
    return {
        "created_at": format_datetime(log.created_at),
        "batch_id": log.batch_id,
        "event_type": log.event_type,
        "row_number": log.row_number,
        "stud_id": log.STUD_ID,
        "message": log.message,
    }


def serialize_backup_log(backup: BackupLog) -> dict[str, Any]:
    return {
        "created_at": format_datetime(backup.created_at),
        "path": backup.backup_path,
        "reason": backup.reason,
        "status": backup.status,
        "integrity": backup.integrity_check_passed,
    }


def serialize_column_registry(column: ColumnRegistry) -> dict[str, Any]:
    return {
        "column_name": column.column_name,
        "detected_type": column.detected_type,
        "status": "Active" if column.is_active else "Missing",
        "first_seen_batch_id": column.first_seen_batch_id,
        "last_seen_batch_id": column.last_seen_batch_id,
        "notes": column.notes or "",
    }


def format_bool(value: bool | None) -> str:
    if value is True:
        return "Yes"
    if value is False:
        return "No"
    return ""


def format_optional_number(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.2f}"


def format_datetime(value) -> str:
    return value.strftime("%Y-%m-%d %H:%M") if value else ""


def format_datetime_from_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")


def format_bytes(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    if size < 1024 ** 3:
        return f"{size / (1024 * 1024):.1f} MB"
    return f"{size / (1024 ** 3):.2f} GB"


def render_html_shell(settings: AppSettings, *, active_path: str) -> str:
    filters_active = "active" if active_path == "/filters" else ""
    dashboard_active = "active" if active_path == "/" else ""
    sheets_active = "active" if active_path == "/excel-sheets" else ""
    import_active = "active" if active_path == "/import" else ""
    status_active = "active" if active_path == "/system-status" else ""
    import os as _os
    _v = str(int(_os.path.getmtime(STATIC_DIR / "wsp.css") * 1000))[-6:]
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{settings.app_name}</title>
  <link rel="stylesheet" href="/static/wsp.css?v={_v}">
</head>
<body data-active-path="{active_path}">
<div class="admin-shell">
  <aside class="sidebar" aria-label="Primary navigation">
    <div class="brand">
      <img src="/static/aub-logo-vertical.jpg" class="brand-logo" alt="American University of Beirut">
      <span class="brand-subtitle">Work Study Program</span>
    </div>
    <nav>
      <div class="nav-label">Admin Workspace</div>
      <a class="{dashboard_active}" href="/"><span class="nav-glyph">OV</span>Dashboard</a>
      <a class="{filters_active}" href="/filters"><span class="nav-glyph">FL</span>Filtering</a>
      <a class="{sheets_active}" href="/excel-sheets"><span class="nav-glyph">XL</span>Excel Sheets</a>
      <a class="{import_active}" href="/import"><span class="nav-glyph">IM</span>Import / Export</a>
      <a class="{status_active}" href="/system-status"><span class="nav-glyph">TS</span>Test/System Status</a>
    </nav>

  </aside>
  <div class="workspace">
    <header class="topbar">
      <div class="runtime-state">
        <span class="pulse-dot"></span>
        <span>Offline workspace active · Port {settings.ui_port}</span>
      </div>
      <div class="admin-account">
        <button class="icon-button" id="refresh-dashboard" type="button" aria-label="Refresh dashboard">Refresh</button>
        <img src="/static/aub-logo-horizontal.png" class="topbar-logo" alt="American University of Beirut">
      </div>
    </header>
    <main class="app-main">
    <section id="dashboard-view" class="view" aria-labelledby="dashboard-title">
      <div class="page-heading">
        <div>
          <h1 id="dashboard-title">Overview</h1>
          <p>Live snapshot of the current student population from the last imported workbook.</p>
        </div>
        <button class="secondary-button report-button" type="button">Export Report</button>
      </div>
      <div id="metric-grid" class="metric-grid" aria-live="polite"></div>
      <div id="latest-import"></div>
      <div class="section-title">Population Analytics</div>
      <div id="structured-charts" class="chart-grid"></div>
    </section>

    <section id="filters-view" class="view" aria-labelledby="filters-title">
      <div class="page-heading">
        <div>
          <h1 id="filters-title">Filter Builder</h1>
          <p>Refine student results using AI semantic matching and database filters.</p>
        </div>
        <div style="display:flex;align-items:center;gap:9px;">
          <span id="prefs-badge" class="prefs-badge"></span>
          <button class="secondary-button" id="clear-filter-prefs" type="button" title="Clear saved preferences">Clear saved</button>
          <div class="mode-pill">Offline RAG search</div>
        </div>
      </div>
      <div class="source-strip">
        <strong>Filtering source</strong>
        <span>Reads `students_current` in SQLite. Excel files update this table only after Import Center ingests them.</span>
      </div>
      <div class="global-search-bar">
        <input id="global-search-input" name="global_query" type="search" autocomplete="off" placeholder="Search everything — name, ID, email, major, skills, preferred work…" aria-label="Global search across all student fields">
      </div>
      <div id="active-filter-tags" class="filter-tags" aria-live="polite"></div>
      <div class="search-layout">
        <form id="search-form" class="search-panel">
          <div class="semantic-card">
            <div class="semantic-card-head">
              <span>Semantic Query</span>
              <span id="index-coverage-badge" class="index-coverage-badge">Checking index...</span>
            </div>
            <label>
              Ask local AI
              <textarea name="semantic_query" rows="3" placeholder="Find students good for social media posters, Canva, and design communications"></textarea>
            </label>
            <div class="rag-controls">
              <label>
                Threshold Match
                <div class="range-row">
                  <input name="semantic_threshold" type="range" min="0" max="1" step="0.05" value="0.10">
                  <output id="threshold-output">10%</output>
                </div>
              </label>
              <label>
                Top-K Results
                <input name="page_size" type="number" min="1" max="100" value="25">
              </label>
            </div>
          </div>
          <div class="two-col">
            <label>Name contains<input name="name_query" type="search" autocomplete="off"></label>
            <label>Skills contain<input name="technical_skills_query" type="search" autocomplete="off"></label>
          </div>
          <div class="two-col">
            <label>Minimum GPA<input name="gpa_min" type="number" min="0" max="4" step="0.05"></label>
            <label>Maximum GPA<input name="gpa_max" type="number" min="0" max="4" step="0.05"></label>
          </div>
          <div class="two-col">
            <div class="ms-field">
              <span class="ms-field-label">Major</span>
              <div class="ms-root" id="ms-major" data-name="majors" data-placeholder="Any major"></div>
            </div>
            <div class="ms-field">
              <span class="ms-field-label">Class / Year</span>
              <div class="ms-root" id="ms-class" data-name="classes" data-placeholder="Any year"></div>
            </div>
          </div>
          <div class="three-col">
            <label>Probation<select name="probation"><option value="any">Any</option><option value="yes">Yes</option><option value="no">No</option></select></label>
            <label>Aid<select name="financial_aid"><option value="any">Any</option><option value="yes">Yes</option><option value="no">No</option></select></label>
            <label>Dorms<select name="dorms"><option value="any">Any</option><option value="yes">Yes</option><option value="no">No</option></select></label>
          </div>
          <div class="two-col">
            <label>Sort by<select name="sort_field"><option value="STUD_ID">Student ID</option><option value="STUD_NAME">Name</option><option value="CUM_GPA">GPA</option><option value="MAJR_DESC">Major</option></select></label>
            <label>Order<select name="sort_direction"><option value="asc">Ascending</option><option value="desc">Descending</option></select></label>
          </div>
          <label class="check-row"><input name="include_missing" type="checkbox"> Include missing students</label>
          <div class="action-row">
            <button class="primary-button" type="submit">Apply AI Filter</button>
            <button class="secondary-button" id="reset-search" type="button">Reset</button>
            <button class="secondary-button" id="export-results" type="button">Export</button>
          </div>
        </form>
        <section class="results-panel" aria-live="polite">
          <div class="results-toolbar">
            <div>
              <p class="eyebrow">Results</p>
              <h2 id="result-count">Loading students</h2>
            </div>
            <div id="search-time" class="mode-pill">Ready</div>
          </div>
          <div id="export-status" class="export-status"></div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th><th>Name</th><th>Major</th><th>Class</th><th>GPA</th><th>Added</th><th>Modified</th><th>Probation</th><th>Aid</th><th>Match</th><th>Why</th><th>Skills</th><th>Preferred work</th>
                </tr>
              </thead>
              <tbody id="results-body"></tbody>
            </table>
          </div>
        </section>
      </div>
    </section>

    <section id="sheets-view" class="view" aria-labelledby="sheets-title">
      <div class="page-heading">
        <div>
          <h1 id="sheets-title">Excel Sheets</h1>
          <p>Inspect read-only worksheet views generated from imported database data.</p>
        </div>
        <div class="mode-pill">Database worksheet views</div>
      </div>
      <div id="sheet-source-map" class="source-map-grid"></div>
      <div class="global-search-bar">
        <input id="sheets-global-search" type="search" autocomplete="off" placeholder="Search across all sheets — any column, any value…" aria-label="Global search across all sheets">
      </div>
      <div id="sheets-global-results" class="sheets-global-results" aria-live="polite" hidden></div>
      <div class="sheet-workspace">
        <div class="sheet-toolbar no-print">
          <div class="sheet-tabs" id="sheet-tabs" role="tablist" aria-label="Available sheets"></div>
          <div class="sheet-toolbar-right">
            <button class="secondary-button sheet-edit-toggle" id="sheet-edit-toggle" type="button" hidden>Edit</button>
            <label class="sheet-search">
              <input id="sheet-search" type="search" autocomplete="off" placeholder="Search sheet…">
            </label>
          </div>
        </div>
        <div id="sheet-edit-banner" class="sheet-edit-banner" hidden>
          <span>⚠ Edit mode — changes saved to the database. Will be overwritten on next import.</span>
          <div style="display:flex;gap:8px;">
            <button class="primary-button" id="sheet-save-edits" type="button" style="min-height:32px;padding:0 12px;font-size:12px">Save Changes</button>
            <button class="secondary-button" id="sheet-cancel-edits" type="button" style="min-height:32px;padding:0 12px;font-size:12px">Cancel</button>
          </div>
        </div>
        <div class="formula-bar">
          <strong id="active-cell-label">A1</strong>
          <span>fx</span>
          <input id="formula-preview" type="text" readonly value="Select a row to preview cell data">
        </div>
        <div id="sheet-summary" class="sheet-summary"></div>
        <div class="sheet-grid-wrap">
          <table id="sheet-table" class="sheet-grid-table"></table>
        </div>
        <div id="sheet-status" class="sheet-status-bar"></div>
      </div>
    </section>

    <section id="import-view" class="view" aria-labelledby="import-title">
      <div class="page-heading">
        <div>
          <h1 id="import-title">Import / Export Center</h1>
          <p>Import workbooks automatically and export filtered results using your saved preferences.</p>
        </div>
        <div class="mode-pill">Auto-consume active</div>
      </div>

      <section class="operation-card" id="auto-export-card" style="margin-bottom:18px"></section>
      <div class="import-layout">
        <section class="operation-card import-action-card">
          <div class="drop-zone" id="import-drop-zone">
            <div class="drop-icon">XL</div>
            <h2>Drop Folder</h2>
            <p>Drop a new Excel workbook into this folder — it is automatically imported and the previous file is archived. Checked every 30 s while this page is open.</p>
            <label>
              Import Folder path
              <input id="import-folder-path" type="text" autocomplete="off">
            </label>
            <div class="action-row">
              <button class="primary-button" id="save-import-folder" type="button">Save Folder</button>
              <button class="secondary-button" id="open-refresh-folder" type="button">Check Now</button>
            </div>
            <div id="import-folder-summary" class="folder-summary"></div>
            <div id="import-run-status" class="inline-status" aria-live="polite"></div>
          </div>
          <div id="semantic-index-widget" class="semantic-index-widget">
            <div class="semantic-index-widget-head">
              <div>
                <strong>AI Search Index</strong>
                <span id="index-coverage-badge" class="index-coverage-badge">Checking...</span>
              </div>
              <button type="button" id="index-reindex-btn" class="index-reindex-btn" style="display:none">Rebuild Index</button>
            </div>
            <div id="index-reindex-msg" class="semantic-index-msg"></div>
            <div class="semantic-index-bar-wrap">
              <div id="index-coverage-bar" class="semantic-index-bar" style="width:0%"></div>
            </div>
          </div>
          <div id="backup-policy" class="policy-grid"></div>
          <div id="import-paths" class="path-stack"></div>
        </section>

        <section class="operation-card">
          <div class="panel-head">
            <div>
              <h2>Import Pipeline Progress</h2>
              <p>Current safety steps for the latest or selected import action.</p>
            </div>
            <span class="mode-pill">Strict mode</span>
          </div>
          <div id="import-pipeline" class="pipeline-list"></div>
        </section>
      </div>

      <div class="ops-grid">
        <section class="operation-card">
          <div class="panel-head">
            <div>
              <h2>Detected Columns Schema</h2>
              <p>Column registry status from imported Excel workbooks.</p>
            </div>
            <span id="schema-count" class="mode-pill">Loading</span>
          </div>
          <div class="compact-table-wrap">
            <table id="schema-table" class="admin-table"></table>
          </div>
        </section>

        <section class="operation-card">
          <div class="panel-head">
            <div>
              <h2>Validation Execution Log</h2>
              <p>Recent importer events, rejected rows, duplicates, and safety notices.</p>
            </div>
            <span id="log-count" class="mode-pill">Loading</span>
          </div>
          <div id="import-console" class="console-log"></div>
        </section>
      </div>
      <section class="operation-card" style="margin-top:18px" id="backup-vault-card">
        <div class="panel-head">
          <div>
            <h2>Backup Vault</h2>
            <p>Database snapshots created automatically before and after every import. Click Restore to roll back.</p>
          </div>
          <button class="secondary-button" id="refresh-backups" type="button" style="flex:0 0 auto">Refresh</button>
        </div>
        <div id="backup-vault-content">Loading…</div>
      </section>
    </section>

    <section id="status-view" class="view" aria-labelledby="status-title">
      <div class="page-heading">
        <div>
          <h1 id="status-title">System Diagnostics</h1>
          <p>Live health checks, diagnostic tests, and system information.</p>
        </div>
        <div style="display:flex;gap:9px;align-items:center;">
          <button class="secondary-button" id="refresh-system-status" type="button">Refresh</button>
          <button class="primary-button" id="run-diagnostics-btn" type="button">Run All Diagnostics</button>
        </div>
      </div>

      <div id="health-overview" class="health-overview" aria-live="polite"></div>

      <div class="diag-section-header" style="margin-top:24px;margin-bottom:10px;">
        <span class="section-title" style="margin:0">Diagnostic Checks</span>
        <span id="diag-summary-pill" class="mode-pill"></span>
      </div>
      <div id="diag-controls" class="diag-controls"></div>

      <div id="diag-progress-wrap" class="diag-progress-wrap" hidden>
        <div class="diag-progress-track"><div id="diag-progress-bar" class="diag-progress-bar"></div></div>
        <span id="diag-progress-label" class="diag-progress-label"></span>
      </div>

      <div id="diagnostics-section" hidden>
        <div id="diagnostic-results" class="diagnostic-grid" aria-live="polite"></div>
      </div>

      <div class="section-title" style="margin-top:28px">System Information</div>
      <div id="system-info-panel" class="system-info-panel" aria-live="polite"></div>
    </section>
    </main>
    <footer class="app-footer">American University of Beirut · WSP Offline Systems · 2026 Admin Portal</footer>
  </div>
</div>
  <script src="/static/chart.umd.min.js" defer></script>
  <script src="/static/wsp.js?v={_v}" defer></script>
</body>
</html>"""


def build_filter_request_from_payload(payload: dict[str, Any], *, page_size: int | None = None) -> FilterRequest:
    numeric_filters = build_numeric_filters(payload)
    boolean_filters = tuple(
        item
        for item in (
            build_boolean_filter("PROBATION", payload.get("probation")),
            build_boolean_filter("FINANCIAL_AID", payload.get("financial_aid")),
            build_boolean_filter("DORMS", payload.get("dorms")),
        )
        if item is not None
    )
    category_filters = tuple(
        item
        for item in (
            build_category_filter("MAJR_DESC", payload.get("majors") or payload.get("major")),
            build_category_filter("CLAS_DESC", payload.get("classes") or payload.get("class_desc")),
        )
        if item is not None
    )
    text_filters = tuple(
        item
        for item in (
            build_text_filter("STUD_NAME", payload.get("name_query")),
            build_text_filter("WSP_TECHNICAL_SKILLS", payload.get("technical_skills_query")),
        )
        if item is not None
    )
    semantic_query = clean_optional_text(payload.get("semantic_query"))
    semantic_threshold = optional_float(payload.get("semantic_threshold"))
    _top_k = page_size or int(payload.get("page_size") or 100)
    semantic_filter = (
        SemanticFilter(
            semantic_query,
            top_k=_top_k,
            minimum_score=semantic_threshold if semantic_threshold is not None else 0.1,
        )
        if semantic_query
        else None
    )

    return FilterRequest(
        numeric_filters=numeric_filters,
        boolean_filters=boolean_filters,
        category_filters=category_filters,
        text_filters=text_filters,
        semantic_filter=semantic_filter,
        global_query=clean_optional_text(payload.get("global_query")),
        sort=SortSpec(payload.get("sort_field") or "STUD_ID", payload.get("sort_direction") or "asc"),
        pagination=PaginationSpec(page=1, page_size=page_size or int(payload.get("page_size") or 100)),
        include_missing=bool(payload.get("include_missing")),
        selected_columns=DEFAULT_RESULT_COLUMNS,
    )


def build_numeric_filters(payload: dict[str, Any]) -> tuple[NumericFilter, ...]:
    gpa_min = optional_float(payload.get("gpa_min"))
    gpa_max = optional_float(payload.get("gpa_max"))
    if gpa_min is not None and gpa_max is not None:
        lower, upper = sorted((gpa_min, gpa_max))
        return (NumericFilter("CUM_GPA", "between", lower, upper),)
    if gpa_min is not None:
        return (NumericFilter("CUM_GPA", ">=", gpa_min),)
    if gpa_max is not None:
        return (NumericFilter("CUM_GPA", "<=", gpa_max),)
    return ()


def build_boolean_filter(field_name: str, value: Any) -> BooleanFilter | None:
    if value == "yes":
        return BooleanFilter(field_name, True)
    if value == "no":
        return BooleanFilter(field_name, False)
    return None


def build_category_filter(field_name: str, value: Any) -> CategoryFilter | None:
    if isinstance(value, list):
        values = tuple(v for v in (clean_optional_text(x) for x in value) if v)
        return CategoryFilter(field_name, values) if values else None
    clean_value = clean_optional_text(value)
    return CategoryFilter(field_name, (clean_value,)) if clean_value else None


def build_text_filter(field_name: str, value: Any) -> TextFilter | None:
    clean_value = clean_optional_text(value)
    return TextFilter(field_name, "contains", clean_value) if clean_value else None


def serialize_filter_response(result) -> dict[str, Any]:
    return {
        "total_count": result.total_count,
        "page": result.page,
        "page_size": result.page_size,
        "applied_filter_count": result.applied_filter_count,
        "rows": build_student_table_rows(result),
        "semantic_scores": result.semantic_scores,
        "semantic_reasons": result.semantic_reasons,
    }


def load_distinct_text_options(session, field_name: str, *, limit: int = 250) -> list[str]:
    column = getattr(StudentCurrent, field_name)
    return [
        value
        for (value,) in (
            session.query(column)
            .filter(column.is_not(None), column != "")
            .distinct()
            .order_by(column.asc())
            .limit(limit)
            .all()
        )
        if value
    ]


def chart_points_to_json(points) -> list[dict[str, int | float | str]]:
    return [{"label": point.label, "value": point.value} for point in points]


def text_points_to_json(points, *, limit: int = 12) -> list[dict[str, int | str]]:
    return [{"label": point.label, "value": point.value} for point in points[:limit]]


def clean_optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).strip().split())
    return text or None


def optional_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return float(value)
