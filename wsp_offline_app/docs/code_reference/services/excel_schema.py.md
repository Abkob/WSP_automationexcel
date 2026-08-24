# `services/excel_schema.py`

[Open source](../../../services/excel_schema.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Defines supported workbook formats and canonical header normalization rules.

## File facts

- **Type:** `.py`
- **Size:** 199 lines
- **Layer:** `services`
- **Python module:** `services.excel_schema`

## Dependencies and integration

- `__future__`
- `dataclasses`
- `openpyxl`
- `pathlib`
- `re`
- `typing`

### Referenced by

- `app/web_app.py`
- `database/schema_manager.py`
- `services/excel_importer.py`
- `tests/conftest.py`
- `tests/test_database.py`
- `tests/test_excel_schema.py`
- `tests/test_web_app.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 58 | class | `WorkbookSchema` | Implementation symbol. |
| 69 | class | `SchemaComparison` | Implementation symbol. |
| 82 | class | `HeaderCleaningResult` | Implementation symbol. |
| 89 | class | `DuplicateHeaderError` | Raised when two or more raw headers normalize to the same database-safe name. |
| 93 | function | `normalize_header(value)` | Implementation symbol. |
| 101 | function | `normalize_headers(values)` | Implementation symbol. |
| 105 | function | `find_duplicates(values)` | Implementation symbol. |
| 117 | function | `clean_headers(raw_headers, reject_duplicates)` | Implementation symbol. |
| 140 | function | `compare_headers(actual_headers, expected_headers)` | Implementation symbol. |
| 157 | function | `read_workbook_schema(path, sheet_name)` | Implementation symbol. |
| 187 | function | `read_header_row_and_row_count(worksheet)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `services/excel_schema.py` when its services responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
