# `services/export_service.py`

[Open source](../../../services/export_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Writes filtered student results and filter metadata into timestamped multi-sheet Excel workbooks and logs exports.

## File facts

- **Type:** `.py`
- **Size:** 157 lines
- **Layer:** `services`
- **Python module:** `services.export_service`

## Dependencies and integration

- `__future__`
- `dataclasses`
- `datetime`
- `json`
- `openpyxl`
- `openpyxl.styles`
- `pathlib`
- `re`
- `services.filter_service`
- `sqlalchemy.orm`
- `typing`

### Referenced by

- `app/pages/filter_page.py`
- `app/web_app.py`
- `tests/test_export_service.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 35 | class | `ExcelExportResult` | Implementation symbol. |
| 42 | function | `safe_export_filename_part(value)` | Implementation symbol. |
| 48 | function | `build_export_filename(prefix, exported_at)` | Implementation symbol. |
| 53 | function | `export_filtered_results_to_excel(filter_result, export_dir, filename_prefix, exported_at, app_version, session, filter_run_id)` | Implementation symbol. |
| 108 | function | `build_export_rows(filter_result)` | Implementation symbol. |
| 126 | function | `add_filter_metadata_sheet(workbook, filter_result, exported_at, app_version)` | Implementation symbol. |
| 150 | function | `collect_source_batch_ids(filter_result)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `services/export_service.py` when its services responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
