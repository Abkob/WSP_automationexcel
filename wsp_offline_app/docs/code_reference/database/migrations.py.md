# `database/migrations.py`

[Open source](../../../database/migrations.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Applies lightweight backwards-compatible schema migrations when older local databases are opened.

## File facts

- **Type:** `.py`
- **Size:** 53 lines
- **Layer:** `database`
- **Python module:** `database.migrations`

## Dependencies and integration

- `__future__`
- `sqlalchemy`
- `sqlalchemy.engine`

### Referenced by

- `database/db.py`
- `tests/test_database.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 7 | function | `run_lightweight_migrations(engine)` | Implementation symbol. |
| 13 | function | `add_semantic_document_hash_column(engine)` | Implementation symbol. |
| 27 | function | `add_semantic_vector_store_name_column(engine)` | Implementation symbol. |
| 40 | function | `add_student_audit_timestamp_columns(engine)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `database/migrations.py` when its database responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
