# `tests/test_excel_schema.py`

[Open source](../../../tests/test_excel_schema.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for excel schema, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 155 lines
- **Layer:** `tests`
- **Python module:** `tests.test_excel_schema`

## Dependencies and integration

- `__future__`
- `openpyxl`
- `pathlib`
- `pytest`
- `services.excel_schema`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 20 | function | `test_normalize_header_creates_stable_database_safe_name()` | Implementation symbol. |
| 26 | function | `test_clean_headers_trims_normalizes_and_preserves_original_names()` | Implementation symbol. |
| 37 | function | `test_clean_headers_detects_duplicate_headers_after_cleaning()` | Implementation symbol. |
| 43 | function | `test_clean_headers_rejects_duplicate_headers_by_default()` | Implementation symbol. |
| 48 | function | `test_find_duplicates_preserves_first_duplicate_order()` | Implementation symbol. |
| 52 | function | `test_compare_headers_matches_expected_columns()` | Implementation symbol. |
| 61 | function | `test_compare_headers_detects_missing_new_and_duplicate_columns()` | Implementation symbol. |
| 75 | function | `test_read_workbook_schema_reads_fixture(sample_workbook_path)` | Implementation symbol. |
| 86 | function | `test_read_workbook_schema_rejects_missing_file(tmp_path)` | Implementation symbol. |
| 91 | function | `test_read_workbook_schema_rejects_unsupported_extension(tmp_path)` | Implementation symbol. |
| 99 | function | `test_read_workbook_schema_rejects_missing_sheet(sample_workbook_path)` | Implementation symbol. |
| 104 | function | `test_user_added_wsp_workbook_matches_initial_column_contract()` | Implementation symbol. |
| 117 | function | `test_duplicate_headers_can_be_seen_after_normalization(tmp_path)` | Implementation symbol. |
| 130 | class | `WorksheetWithoutDimensionMetadata` | Implementation symbol. |
| 142 | function | `test_schema_reader_header_fallback_handles_missing_dimension_metadata()` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_excel_schema.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
