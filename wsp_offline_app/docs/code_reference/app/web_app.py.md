# `app/web_app.py`

[Open source](../../../app/web_app.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Defines the production FastAPI routes, HTML shell, import orchestration, dashboard APIs, diagnostics, backup endpoints, and request/response adapters.

## File facts

- **Type:** `.py`
- **Size:** 2,151 lines
- **Layer:** `app`
- **Python module:** `app.web_app`

## Dependencies and integration

- `__future__`
- `app.components.student_table`
- `config`
- `database.db`
- `database.models`
- `database.schema_manager`
- `dataclasses`
- `datetime`
- `fastapi`
- `fastapi.responses`
- `fastapi.staticfiles`
- `html`
- `json`
- `logging`
- `os`
- `pathlib`
- `platform`
- `services.analytics_service`
- `services.archive_service`
- `services.backup_service`
- `services.dashboard_intelligence_service`
- `services.embedding_service`
- `services.excel_importer`
- `services.excel_schema`
- `services.export_service`
- `services.filter_service`
- `services.preferred_work_grouping_service`
- `services.semantic_document_service`
- `services.semantic_search_service`
- `services.semantic_service`
- `services.student_profile_service`
- `services.technical_skill_grouping_service`
- `services.value_normalizer`
- `services.vector_store_service`
- `shutil`
- `sqlalchemy`
- `sqlalchemy.orm`
- `sqlite3`
- `sys`
- `threading`
- `time`
- `typing`

### Referenced by

- `main.py`
- `scripts/verify_install.py`
- `tests/test_web_app.py`
- `wsp_launcher.pyw`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 98 | function | `create_web_app(settings)` | Implementation symbol. |
| 462 | function | `initialize_runtime_database(settings)` | Implementation symbol. |
| 472 | function | `_prewarm_embedding_model(settings)` | Implementation symbol. |
| 514 | function | `_startup_reindex(settings, force)` | Implementation symbol. |
| 599 | function | `open_session(settings)` | Implementation symbol. |
| 605 | function | `configure_import_folder_background_refresher(app, settings)` | Implementation symbol. |
| 632 | function | `read_import_folder_config(settings)` | Implementation symbol. |
| 642 | function | `resolve_user_folder_path(settings, folder_path)` | Implementation symbol. |
| 649 | function | `configured_import_folder(settings)` | Implementation symbol. |
| 657 | function | `import_folder_archive_path(settings)` | Implementation symbol. |
| 661 | function | `configured_export_dir(settings)` | Implementation symbol. |
| 667 | function | `ensure_import_folder_ready(settings)` | Implementation symbol. |
| 677 | function | `save_configured_import_folder(settings, folder_path)` | Implementation symbol. |
| 692 | function | `run_excel_import_from_path(settings, source_path, archive_dir)` | Implementation symbol. |
| 852 | function | `refresh_upload_folder_imports(settings, automatic)` | Implementation symbol. |
| 876 | function | `consume_import_folder(settings, folder, archive_folder, automatic)` | Implementation symbol. |
| 937 | function | `archive_retired_import_folder_files(settings, keep_path)` | Implementation symbol. |
| 959 | function | `build_import_folder_archive_target(archive_folder, source_path)` | Implementation symbol. |
| 970 | function | `normalize_import_row(row, row_number, warnings)` | Implementation symbol. |
| 989 | function | `build_excel_sheets_payload(settings, session)` | Implementation symbol. |
| 1113 | function | `build_import_center_payload(settings, session)` | Implementation symbol. |
| 1185 | function | `build_system_status_payload(settings, session)` | Implementation symbol. |
| 1240 | function | `run_single_diagnostic(key, settings, session)` | Implementation symbol. |
| 1446 | function | `run_diagnostics(settings, session, checks)` | Implementation symbol. |
| 1451 | function | `find_excel_candidates(settings)` | Implementation symbol. |
| 1467 | function | `find_upload_folder_candidates(settings)` | Implementation symbol. |
| 1485 | function | `serialize_file_candidate(path, settings)` | Implementation symbol. |
| 1497 | function | `default_workbook_path(settings)` | Implementation symbol. |
| 1504 | function | `count_excel_files(folder)` | Implementation symbol. |
| 1516 | function | `serialize_import_batch(batch)` | Implementation symbol. |
| 1532 | function | `serialize_import_log(log)` | Implementation symbol. |
| 1543 | function | `serialize_backup_log(backup)` | Implementation symbol. |
| 1553 | function | `serialize_column_registry(column)` | Implementation symbol. |
| 1564 | function | `format_bool(value)` | Implementation symbol. |
| 1572 | function | `format_optional_number(value)` | Implementation symbol. |
| 1578 | function | `format_datetime(value)` | Implementation symbol. |
| 1582 | function | `format_datetime_from_timestamp(timestamp)` | Implementation symbol. |
| 1586 | function | `format_bytes(size)` | Implementation symbol. |
| 1596 | function | `render_html_shell(settings, active_path, student_id)` | Implementation symbol. |
| 2012 | function | `build_filter_request_from_payload(payload, page_size)` | Implementation symbol. |
| 2070 | function | `build_numeric_filters(payload)` | Implementation symbol. |
| 2083 | function | `build_boolean_filter(field_name, value)` | Implementation symbol. |
| 2091 | function | `build_category_filter(field_name, value)` | Implementation symbol. |
| 2099 | function | `build_text_filter(field_name, value)` | Implementation symbol. |
| 2104 | function | `serialize_filter_response(result)` | Implementation symbol. |
| 2116 | function | `load_distinct_text_options(session, field_name, limit)` | Implementation symbol. |
| 2132 | function | `chart_points_to_json(points)` | Implementation symbol. |
| 2136 | function | `text_points_to_json(points, limit)` | Implementation symbol. |
| 2140 | function | `clean_optional_text(value)` | Implementation symbol. |
| 2147 | function | `optional_float(value)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `app/web_app.py` when its app responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
