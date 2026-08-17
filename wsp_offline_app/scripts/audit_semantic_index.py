from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_DIRECTORY = Path(__file__).resolve().parents[1]
if str(PROJECT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIRECTORY))

from config import PROJECT_ROOT, get_default_settings
from database.db import create_sqlite_engine
from database.models import SemanticEmbedding, StudentCurrent
from services.semantic_document_service import build_student_semantic_profiles
from services.vector_store_service import FaissVectorStore
from sqlalchemy.orm import Session


def audit_semantic_index() -> dict[str, object]:
    settings = get_default_settings()
    engine = create_sqlite_engine(settings.database_path)
    with Session(engine) as session:
        students = tuple(
            session.query(StudentCurrent)
            .filter(StudentCurrent.missing_from_latest_import.is_(False))
            .all()
        )
        profiles = build_student_semantic_profiles(students)
        profile_by_id = {profile.STUD_ID: profile for profile in profiles}
        row_by_id = {row.STUD_ID: row for row in session.query(SemanticEmbedding).all()}
    engine.dispose()

    store = FaissVectorStore(settings.semantic_index_dir, collection_name="students")
    record_by_id = {record.record_id: record for record in store.load_records()}
    profile_ids = set(profile_by_id)
    row_ids = set(row_by_id)
    record_ids = set(record_by_id)
    shared_rows = profile_ids & row_ids
    shared_records = profile_ids & record_ids

    report: dict[str, object] = {
        "database_path": str(settings.database_path),
        "index_directory": str(settings.semantic_index_dir),
        "configured_model": settings.embedding_model_name,
        "active_profiles": len(profile_ids),
        "embedding_rows": len(row_ids),
        "vector_records": len(record_ids),
        "missing_embedding_rows": len(profile_ids - row_ids),
        "extra_embedding_rows": len(row_ids - profile_ids),
        "missing_vectors": len(profile_ids - record_ids),
        "extra_vectors": len(record_ids - profile_ids),
        "stale_database_hashes": sum(
            row_by_id[student_id].semantic_document_hash != profile_by_id[student_id].document_hash
            for student_id in shared_rows
        ),
        "database_source_text_mismatches": sum(
            row_by_id[student_id].source_text != profile_by_id[student_id].text
            for student_id in shared_rows
        ),
        "stale_vector_hashes": sum(
            str(record_by_id[student_id].metadata.get("semantic_hash") or "")
            != profile_by_id[student_id].document_hash
            for student_id in shared_records
        ),
        "vector_document_mismatches": sum(
            record_by_id[student_id].document != profile_by_id[student_id].text
            for student_id in shared_records
        ),
    }
    mismatch_keys = (
        "missing_embedding_rows",
        "extra_embedding_rows",
        "missing_vectors",
        "extra_vectors",
        "stale_database_hashes",
        "database_source_text_mismatches",
        "stale_vector_hashes",
        "vector_document_mismatches",
    )
    report["original_text_index_verified"] = all(report[key] == 0 for key in mismatch_keys)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify that semantic vectors correspond to current original student text.")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "testbench_reports" / "semantic_index_audit.json",
    )
    args = parser.parse_args()
    report = audit_semantic_index()
    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output_path), **report}, indent=2))
    return 0 if report["original_text_index_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
