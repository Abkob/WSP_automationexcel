# `tests/test_schema_manager.py`

[Open source](../../../tests/test_schema_manager.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for schema manager, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 145 lines
- **Layer:** `tests`
- **Python module:** `tests.test_schema_manager`

## Dependencies and integration

- `__future__`
- `database.db`
- `database.models`
- `database.schema_manager`
- `datetime`
- `pathlib`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 11 | function | `create_batch(session, file_hash)` | Implementation symbol. |
| 18 | function | `test_infer_column_type_handles_common_values()` | Implementation symbol. |
| 27 | function | `test_sync_column_registry_registers_new_columns(tmp_path)` | Implementation symbol. |
| 54 | function | `test_sync_column_registry_updates_repeated_columns_last_seen_batch(tmp_path)` | Implementation symbol. |
| 80 | function | `test_sync_column_registry_marks_missing_columns_inactive(tmp_path)` | Implementation symbol. |
| 102 | function | `test_sync_column_registry_detects_type_changes(tmp_path)` | Implementation symbol. |
| 127 | function | `test_sync_column_registry_preserves_non_empty_type_after_empty_first_seen(tmp_path)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_schema_manager.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
