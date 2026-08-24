# `services/excel_importer.py`

[Open source](../../../services/excel_importer.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Reads Excel workbooks, rejects unsafe inputs, detects duplicates, merges current students, retains history, and logs transactional import results.

## File facts

- **Type:** `.py`
- **Size:** 533 lines
- **Layer:** `services`
- **Python module:** `services.excel_importer`

## Dependencies and integration

- `__future__`
- `database.models`
- `dataclasses`
- `datetime`
- `hashlib`
- `json`
- `pandas`
- `pathlib`
- `services.excel_schema`
- `services.value_normalizer`
- `sqlalchemy.orm`
- `time`
- `typing`

### Referenced by

- `app/web_app.py`
- `services/archive_service.py`
- `tests/test_archive_service.py`
- `tests/test_excel_importer.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 33 | class | `ExcelIntakeError` | Base error for Excel intake failures. |
| 37 | class | `TemporaryExcelFileIgnored` | Raised when an Excel temporary lock file should be ignored. |
| 41 | class | `UnsupportedExcelFileError` | Raised when the supplied file path is not a supported Excel workbook. |
| 45 | class | `FileNotStableError` | Raised when a file keeps changing and should not be imported yet. |
| 49 | class | `DuplicateExcelFileError` | Raised when the exact same file was already imported. |
| 53 | class | `MissingStudentIdError` | Raised when an imported row does not contain a usable STUD_ID. |
| 57 | class | `NoValidStudentRowsError` | Raised when a workbook has no usable student records to import. |
| 62 | class | `ExcelIntakeResult` | Implementation symbol. |
| 69 | class | `ExcelWorkbookData` | Implementation symbol. |
| 86 | class | `StudentUpsertResult` | Implementation symbol. |
| 93 | class | `MissingStudentDetectionResult` | Implementation symbol. |
| 105 | function | `is_temporary_excel_file(path)` | Implementation symbol. |
| 109 | function | `validate_excel_file_path(path)` | Implementation symbol. |
| 127 | function | `_default_size_reader(path)` | Implementation symbol. |
| 131 | function | `wait_for_file_size_to_stabilize(path, required_stable_reads, poll_interval_seconds, timeout_seconds, size_reader, sleep_func, clock_func)` | Implementation symbol. |
| 170 | function | `intake_excel_file(path, required_stable_reads, poll_interval_seconds, timeout_seconds)` | Implementation symbol. |
| 192 | function | `calculate_file_hash(path, chunk_size)` | Implementation symbol. |
| 206 | function | `find_import_batch_by_hash(session, file_hash)` | Implementation symbol. |
| 210 | function | `log_import_event(session, batch_id, event_type, message, row_number, stud_id, details_json)` | Implementation symbol. |
| 232 | function | `ensure_file_not_previously_imported(session, path, file_hash, log_duplicate)` | Implementation symbol. |
| 263 | function | `_none_if_missing(value)` | Implementation symbol. |
| 269 | function | `read_excel_workbook(path, sheet_name)` | Implementation symbol. |
| 302 | function | `normalize_student_id(value)` | Implementation symbol. |
| 319 | function | `extract_required_student_id(row, session, batch_id, row_number)` | Implementation symbol. |
| 347 | function | `build_row_hash_payload(row, excluded_fields)` | Implementation symbol. |
| 360 | function | `generate_row_hash(row)` | Implementation symbol. |
| 366 | function | `split_current_and_extra_columns(row)` | Implementation symbol. |
| 380 | function | `snapshot_student_current(student)` | Implementation symbol. |
| 395 | function | `apply_row_to_student(student, row, row_hash, batch_id, modified_at)` | Implementation symbol. |
| 415 | function | `upsert_student_row(session, row, batch_id)` | Implementation symbol. |
| 470 | function | `mark_missing_students(session, seen_student_ids, batch_id)` | Implementation symbol. |
| 509 | function | `execute_import_transaction(session_factory, batch_id, operation)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `services/excel_importer.py` when its services responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
