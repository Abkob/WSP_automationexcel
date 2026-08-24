# `tests/test_web_app.py`

[Open source](../../../tests/test_web_app.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for web app, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 530 lines
- **Layer:** `tests`
- **Python module:** `tests.test_web_app`

## Dependencies and integration

- `__future__`
- `app.web_app`
- `config`
- `database.db`
- `database.models`
- `fastapi.testclient`
- `openpyxl`
- `os`
- `pathlib`
- `services.excel_schema`
- `shutil`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 17 | function | `make_test_client(tmp_path)` | Implementation symbol. |
| 72 | function | `test_filters_page_uses_fastapi_static_ui_not_nicegui(tmp_path)` | Implementation symbol. |
| 91 | function | `test_index_status_uses_active_students_as_coverage_denominator(tmp_path)` | Implementation symbol. |
| 106 | function | `test_admin_workspace_pages_render_from_fastapi_shell(tmp_path)` | Implementation symbol. |
| 142 | function | `test_student_profile_page_and_api_present_complete_record(tmp_path)` | Implementation symbol. |
| 185 | function | `test_student_lookup_and_missing_profile(tmp_path)` | Implementation symbol. |
| 197 | function | `test_filter_and_excel_assets_include_profile_entry_points(tmp_path)` | Implementation symbol. |
| 209 | function | `test_dashboard_api_returns_metrics_and_chart_data(tmp_path)` | Implementation symbol. |
| 229 | function | `test_dashboard_api_supports_faculty_and_class_drilldown(tmp_path)` | Implementation symbol. |
| 242 | function | `test_dashboard_static_assets_include_interactive_chart_system(tmp_path)` | Implementation symbol. |
| 284 | function | `test_new_workspace_apis_return_backend_data(tmp_path)` | Implementation symbol. |
| 319 | function | `test_import_run_api_executes_safe_excel_pipeline(tmp_path, sample_workbook_path)` | Implementation symbol. |
| 338 | function | `test_import_run_rejects_headers_only_workbook_without_marking_students_missing(tmp_path)` | Implementation symbol. |
| 363 | function | `test_import_run_rejects_workbook_with_no_valid_student_ids_without_marking_students_missing(tmp_path)` | Implementation symbol. |
| 391 | function | `test_import_refresh_folder_imports_new_uploads_and_skips_duplicates(tmp_path, sample_workbook_path)` | Implementation symbol. |
| 415 | function | `test_import_folder_can_be_assigned_from_import_center(tmp_path)` | Implementation symbol. |
| 431 | function | `test_import_folder_keeps_newest_workbook_and_archives_old_root_files(tmp_path, sample_workbook_path)` | Implementation symbol. |
| 464 | function | `test_search_api_returns_fast_offline_semantic_results(tmp_path)` | Implementation symbol. |
| 485 | function | `test_export_api_creates_filtered_xlsx(tmp_path)` | Implementation symbol. |
| 504 | function | `test_web_payload_builder_handles_boolean_numeric_and_category_filters()` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_web_app.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
