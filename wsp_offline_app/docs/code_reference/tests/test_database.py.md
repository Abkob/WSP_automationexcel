# `tests/test_database.py`

[Open source](../../../tests/test_database.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for database, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 353 lines
- **Layer:** `tests`
- **Python module:** `tests.test_database`

## Dependencies and integration

- `__future__`
- `database.db`
- `database.migrations`
- `database.models`
- `pathlib`
- `pytest`
- `services.excel_schema`
- `sqlalchemy`
- `sqlalchemy.exc`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 23 | function | `test_build_sqlite_url_uses_absolute_file_path(tmp_path)` | Implementation symbol. |
| 32 | function | `test_create_sqlite_engine_creates_database_file(tmp_path)` | Implementation symbol. |
| 42 | function | `test_session_factory_can_insert_and_query_record(tmp_path)` | Implementation symbol. |
| 59 | function | `test_foreign_keys_are_enabled(tmp_path)` | Implementation symbol. |
| 65 | function | `test_busy_timeout_is_set(tmp_path)` | Implementation symbol. |
| 71 | function | `test_wal_mode_is_enabled_for_file_database(tmp_path)` | Implementation symbol. |
| 77 | function | `test_health_check_returns_true(tmp_path)` | Implementation symbol. |
| 83 | function | `test_initialize_database_creates_core_tables(tmp_path)` | Implementation symbol. |
| 103 | function | `test_initialize_database_migrates_existing_semantic_embedding_columns(tmp_path)` | Implementation symbol. |
| 129 | function | `test_initialize_database_migrates_existing_student_audit_timestamp_columns(tmp_path)` | Implementation symbol. |
| 166 | function | `test_students_current_contains_expected_wsp_columns(tmp_path)` | Implementation symbol. |
| 181 | function | `test_required_indexes_exist(tmp_path)` | Implementation symbol. |
| 197 | function | `test_students_current_unique_student_id_is_enforced(tmp_path)` | Implementation symbol. |
| 212 | function | `test_students_current_extra_columns_json_round_trips(tmp_path)` | Implementation symbol. |
| 232 | function | `test_students_current_missing_flag_defaults_to_false(tmp_path)` | Implementation symbol. |
| 247 | function | `test_import_batch_file_hash_is_unique(tmp_path)` | Implementation symbol. |
| 265 | function | `test_import_batch_status_can_be_updated(tmp_path)` | Implementation symbol. |
| 283 | function | `test_student_history_can_link_to_import_batch(tmp_path)` | Implementation symbol. |
| 311 | function | `test_import_event_log_can_link_to_batch(tmp_path)` | Implementation symbol. |
| 340 | function | `test_column_registry_unique_column_name_is_enforced(tmp_path)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_database.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
