# `database/db.py`

[Open source](../../../database/db.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Creates and configures SQLite engines/sessions, enables safety pragmas, initializes tables, and exposes database health helpers.

## File facts

- **Type:** `.py`
- **Size:** 65 lines
- **Layer:** `database`
- **Python module:** `database.db`

## Dependencies and integration

- `__future__`
- `database.migrations`
- `database.models`
- `pathlib`
- `sqlalchemy`
- `sqlalchemy.engine`
- `sqlalchemy.orm`
- `typing`

### Referenced by

- `app/layout.py`
- `app/pages/dashboard_page.py`
- `app/pages/filter_page.py`
- `app/web_app.py`
- `main.py`
- `scripts/audit_semantic_index.py`
- `scripts/run_bias_testbench.py`
- `scripts/run_preferred_work_edge_case_audit.py`
- `tests/test_analytics_service.py`
- `tests/test_archive_service.py`
- `tests/test_backup_service.py`
- `tests/test_dashboard_intelligence_service.py`
- `tests/test_dashboard_page.py`
- `tests/test_database.py`
- `tests/test_excel_importer.py`
- `tests/test_export_service.py`
- `tests/test_filter_service.py`
- `tests/test_schema_manager.py`
- `tests/test_semantic_search_service.py`
- `tests/test_semantic_service.py`
- `tests/test_ui_layout.py`
- `tests/test_web_app.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 14 | function | `build_sqlite_url(database_path)` | Implementation symbol. |
| 19 | function | `create_sqlite_engine(database_path, echo, enable_wal, busy_timeout_ms)` | Implementation symbol. |
| 45 | function | `create_session_factory(engine)` | Implementation symbol. |
| 49 | function | `health_check(engine)` | Implementation symbol. |
| 54 | function | `read_pragma(engine, pragma_name)` | Implementation symbol. |
| 59 | function | `initialize_database(engine)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `database/db.py` when its database responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
