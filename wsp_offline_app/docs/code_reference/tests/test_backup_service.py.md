# `tests/test_backup_service.py`

[Open source](../../../tests/test_backup_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for backup service, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 275 lines
- **Layer:** `tests`
- **Python module:** `tests.test_backup_service`

## Dependencies and integration

- `__future__`
- `database.db`
- `database.models`
- `datetime`
- `os`
- `pathlib`
- `pytest`
- `services.backup_service`
- `sqlite3`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 25 | function | `test_safe_backup_reason_removes_unsafe_characters()` | Implementation symbol. |
| 30 | function | `test_build_backup_filename_includes_timestamp_and_reason()` | Implementation symbol. |
| 36 | function | `test_create_database_backup_creates_openable_sqlite_file(tmp_path)` | Implementation symbol. |
| 54 | function | `test_database_backup_contains_expected_tables(tmp_path)` | Implementation symbol. |
| 72 | function | `test_database_backup_captures_existing_data(tmp_path)` | Implementation symbol. |
| 90 | function | `test_database_backup_log_row_is_created(tmp_path)` | Implementation symbol. |
| 109 | function | `test_create_database_backup_rejects_missing_database(tmp_path)` | Implementation symbol. |
| 114 | function | `test_create_database_backup_rejects_file_backup_path(tmp_path)` | Implementation symbol. |
| 125 | function | `test_valid_backup_passes_integrity_check(tmp_path)` | Implementation symbol. |
| 134 | function | `test_invalid_backup_fails_integrity_check(tmp_path)` | Implementation symbol. |
| 142 | function | `test_required_pre_import_backup_failure_is_loud(tmp_path)` | Implementation symbol. |
| 153 | function | `test_list_database_backups_returns_sorted_backups(tmp_path)` | Implementation symbol. |
| 171 | function | `test_restore_requires_explicit_confirmation(tmp_path)` | Implementation symbol. |
| 176 | function | `test_restore_replaces_database_and_logs_restore_event(tmp_path)` | Implementation symbol. |
| 219 | function | `test_restore_creates_pre_restore_backup(tmp_path)` | Implementation symbol. |
| 233 | function | `test_retention_is_disabled_by_default(tmp_path)` | Implementation symbol. |
| 247 | function | `test_retention_preview_lists_files_without_deleting(tmp_path)` | Implementation symbol. |
| 272 | function | `test_retention_preview_rejects_negative_keep_latest(tmp_path)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_backup_service.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
