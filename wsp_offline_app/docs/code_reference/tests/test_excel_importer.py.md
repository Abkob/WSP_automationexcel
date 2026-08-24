# `tests/test_excel_importer.py`

[Open source](../../../tests/test_excel_importer.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for excel importer, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 640 lines
- **Layer:** `tests`
- **Python module:** `tests.test_excel_importer`

## Dependencies and integration

- `__future__`
- `collections`
- `database.db`
- `database.models`
- `openpyxl`
- `pathlib`
- `pytest`
- `services.excel_importer`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 35 | function | `create_minimal_workbook(path)` | Implementation symbol. |
| 42 | function | `test_valid_xlsx_file_is_accepted(tmp_path)` | Implementation symbol. |
| 52 | function | `test_missing_file_raises_clear_error(tmp_path)` | Implementation symbol. |
| 57 | function | `test_txt_file_is_rejected(tmp_path)` | Implementation symbol. |
| 65 | function | `test_directory_path_is_rejected(tmp_path)` | Implementation symbol. |
| 70 | function | `test_temporary_excel_file_is_ignored(tmp_path)` | Implementation symbol. |
| 78 | function | `test_file_size_stability_wait_accepts_stable_size(tmp_path)` | Implementation symbol. |
| 101 | function | `test_unstable_file_times_out_predictably(tmp_path)` | Implementation symbol. |
| 123 | function | `test_wait_for_file_size_to_stabilize_validates_settings(tmp_path)` | Implementation symbol. |
| 136 | function | `test_same_file_produces_same_hash(tmp_path)` | Implementation symbol. |
| 146 | function | `test_changed_file_produces_different_hash(tmp_path)` | Implementation symbol. |
| 158 | function | `test_calculate_file_hash_validates_chunk_size(tmp_path)` | Implementation symbol. |
| 165 | function | `test_duplicate_import_is_detected_and_logged(tmp_path)` | Implementation symbol. |
| 188 | function | `test_new_file_hash_is_returned_when_not_previously_imported(tmp_path)` | Implementation symbol. |
| 200 | function | `test_find_import_batch_by_hash_returns_existing_batch(tmp_path)` | Implementation symbol. |
| 216 | function | `test_duplicate_skip_does_not_modify_students(tmp_path)` | Implementation symbol. |
| 239 | function | `test_read_excel_workbook_loads_fixture(sample_workbook_path)` | Implementation symbol. |
| 248 | function | `test_read_excel_workbook_detects_headers(sample_workbook_path)` | Implementation symbol. |
| 255 | function | `test_read_excel_workbook_preserves_empty_cells_as_none(tmp_path)` | Implementation symbol. |
| 268 | function | `test_read_excel_workbook_uses_first_sheet_by_default(tmp_path)` | Implementation symbol. |
| 287 | function | `test_read_excel_workbook_allows_future_sheet_selection(tmp_path)` | Implementation symbol. |
| 305 | function | `test_read_excel_workbook_rejects_missing_sheet(sample_workbook_path)` | Implementation symbol. |
| 310 | function | `test_normalize_student_id_trims_and_normalizes_excel_numeric_values()` | Implementation symbol. |
| 317 | function | `test_normalize_student_id_rejects_empty_or_boolean_values()` | Implementation symbol. |
| 323 | function | `test_extract_required_student_id_returns_valid_id()` | Implementation symbol. |
| 327 | function | `test_extract_required_student_id_rejects_and_logs_missing_id(tmp_path)` | Implementation symbol. |
| 355 | function | `test_same_normalized_row_produces_same_hash()` | Implementation symbol. |
| 361 | function | `test_changed_gpa_changes_row_hash()` | Implementation symbol. |
| 368 | function | `test_changed_extra_column_changes_row_hash()` | Implementation symbol. |
| 375 | function | `test_column_order_does_not_change_row_hash()` | Implementation symbol. |
| 382 | function | `test_volatile_database_fields_are_excluded_from_row_hash()` | Implementation symbol. |
| 389 | function | `test_upsert_student_row_inserts_new_student(tmp_path)` | Implementation symbol. |
| 419 | function | `test_upsert_student_row_marks_unchanged_without_history(tmp_path)` | Implementation symbol. |
| 445 | function | `test_upsert_student_row_updates_changed_student_and_creates_history(tmp_path)` | Implementation symbol. |
| 472 | function | `test_upsert_student_row_clears_missing_flag_for_restored_student(tmp_path)` | Implementation symbol. |
| 498 | function | `test_mark_missing_students_marks_absent_student_without_deleting(tmp_path)` | Implementation symbol. |
| 522 | function | `test_mark_missing_students_does_not_duplicate_history_for_already_missing_student(tmp_path)` | Implementation symbol. |
| 545 | function | `test_mark_missing_students_leaves_seen_students_active(tmp_path)` | Implementation symbol. |
| 565 | function | `test_execute_import_transaction_commits_successful_import(tmp_path)` | Implementation symbol. |
| 591 | function | `test_execute_import_transaction_rolls_back_student_changes_and_records_failed_batch(tmp_path)` | Implementation symbol. |
| 627 | function | `test_execute_import_transaction_records_missing_batch_error_without_partial_rows(tmp_path)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_excel_importer.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
