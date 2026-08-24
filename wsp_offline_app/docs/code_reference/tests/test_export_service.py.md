# `tests/test_export_service.py`

[Open source](../../../tests/test_export_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for export service, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 327 lines
- **Layer:** `tests`
- **Python module:** `tests.test_export_service`

## Dependencies and integration

- `__future__`
- `database.db`
- `database.models`
- `datetime`
- `openpyxl`
- `pathlib`
- `pytest`
- `services.export_service`
- `services.filter_service`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 20 | function | `test_safe_export_filename_part_removes_unsafe_characters()` | Implementation symbol. |
| 25 | function | `test_build_export_filename_includes_timestamp_and_prefix()` | Implementation symbol. |
| 31 | function | `test_export_filtered_results_file_is_created(tmp_path)` | Implementation symbol. |
| 53 | function | `test_exported_workbook_opens_and_has_filtered_results_sheet(tmp_path)` | Implementation symbol. |
| 73 | function | `test_exported_row_count_matches_filter_result(tmp_path)` | Implementation symbol. |
| 95 | function | `test_export_respects_selected_columns(tmp_path)` | Implementation symbol. |
| 120 | function | `test_export_includes_semantic_score_when_present(tmp_path)` | Implementation symbol. |
| 138 | function | `test_export_includes_semantic_score_for_default_columns_when_present(tmp_path)` | Implementation symbol. |
| 164 | function | `test_export_includes_semantic_explanation_for_default_columns_when_present(tmp_path)` | Implementation symbol. |
| 187 | function | `metadata_rows(path)` | Implementation symbol. |
| 195 | function | `test_export_metadata_sheet_exists_and_stores_filter_json(tmp_path)` | Implementation symbol. |
| 214 | function | `test_export_metadata_stores_timestamp_row_count_and_app_version(tmp_path)` | Implementation symbol. |
| 234 | function | `test_export_metadata_stores_source_batch_ids(tmp_path)` | Implementation symbol. |
| 261 | function | `test_export_log_row_is_created(tmp_path)` | Implementation symbol. |
| 289 | function | `test_export_log_links_to_filter_run(tmp_path)` | Implementation symbol. |
| 314 | function | `test_export_logging_requires_session_and_filter_run_together(tmp_path)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_export_service.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
