# `database/models.py`

[Open source](../../../database/models.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Declares the SQLite/SQLAlchemy data model for current students, retained history, imports, schemas, filters, exports, embeddings, and backups.

## File facts

- **Type:** `.py`
- **Size:** 206 lines
- **Layer:** `database`
- **Python module:** `database.models`

## Dependencies and integration

- `__future__`
- `datetime`
- `sqlalchemy`
- `sqlalchemy.orm`
- `typing`

### Referenced by

- `app/components/student_table.py`
- `app/layout.py`
- `app/pages/filter_page.py`
- `app/web_app.py`
- `database/db.py`
- `database/schema_manager.py`
- `scripts/audit_semantic_index.py`
- `scripts/run_bias_testbench.py`
- `scripts/run_preferred_work_edge_case_audit.py`
- `services/analytics_service.py`
- `services/archive_service.py`
- `services/backup_service.py`
- `services/dashboard_intelligence_service.py`
- `services/excel_importer.py`
- `services/filter_service.py`
- `services/semantic_document_service.py`
- `services/semantic_search_service.py`
- `services/semantic_service.py`
- `services/student_profile_service.py`
- `tests/test_analytics_service.py`
- `tests/test_archive_service.py`
- `tests/test_backup_service.py`
- `tests/test_dashboard_intelligence_service.py`
- `tests/test_dashboard_page.py`
- `tests/test_database.py`
- `tests/test_excel_importer.py`
- `tests/test_export_service.py`
- `tests/test_filter_page_components.py`
- `tests/test_filter_service.py`
- `tests/test_schema_manager.py`
- `tests/test_semantic_document_service.py`
- `tests/test_semantic_search_service.py`
- `tests/test_semantic_service.py`
- `tests/test_ui_layout.py`
- `tests/test_web_app.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 10 | function | `utc_now()` | Implementation symbol. |
| 14 | class | `Base` | Implementation symbol. |
| 18 | class | `TimestampMixin` | Implementation symbol. |
| 28 | class | `ImportBatch` | Implementation symbol. |
| 52 | class | `StudentCurrent` | Implementation symbol. |
| 104 | class | `StudentHistory` | Implementation symbol. |
| 121 | class | `ColumnRegistry` | Implementation symbol. |
| 135 | class | `FileImportLog` | Implementation symbol. |
| 150 | class | `FilterPreset` | Implementation symbol. |
| 158 | class | `FilterRun` | Implementation symbol. |
| 168 | class | `ExportLog` | Implementation symbol. |
| 178 | class | `SemanticEmbedding` | Implementation symbol. |
| 192 | class | `BackupLog` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `database/models.py` when its database responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
