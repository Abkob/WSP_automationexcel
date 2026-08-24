# `database/schema_manager.py`

[Open source](../../../database/schema_manager.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Tracks workbook columns, infers data types, and synchronizes the dynamic column registry.

## File facts

- **Type:** `.py`
- **Size:** 129 lines
- **Layer:** `database`
- **Python module:** `database.schema_manager`

## Dependencies and integration

- `__future__`
- `database.models`
- `dataclasses`
- `datetime`
- `services.excel_schema`
- `sqlalchemy.orm`
- `typing`

### Referenced by

- `app/web_app.py`
- `tests/test_schema_manager.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 14 | class | `ColumnTypeChange` | Implementation symbol. |
| 21 | class | `SchemaSyncResult` | Implementation symbol. |
| 29 | function | `infer_column_type(values)` | Implementation symbol. |
| 47 | function | `sync_column_registry(session, columns, batch_id, inferred_types, original_names)` | Implementation symbol. |
| 125 | function | `_append_note(existing_notes, new_note)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `database/schema_manager.py` when its database responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
