# `tests/test_archive_service.py`

[Open source](../../../tests/test_archive_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for archive service, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 121 lines
- **Layer:** `tests`
- **Python module:** `tests.test_archive_service`

## Dependencies and integration

- `__future__`
- `database.db`
- `database.models`
- `datetime`
- `openpyxl`
- `pathlib`
- `pytest`
- `services.archive_service`
- `services.excel_importer`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 21 | function | `create_workbook(path)` | Implementation symbol. |
| 29 | function | `test_safe_filename_part_removes_unsafe_characters()` | Implementation symbol. |
| 34 | function | `test_build_archive_filename_includes_timestamp_stem_and_hash()` | Implementation symbol. |
| 42 | function | `test_archive_original_excel_file_creates_verified_copy(tmp_path)` | Implementation symbol. |
| 56 | function | `test_archive_original_excel_file_avoids_filename_collision(tmp_path)` | Implementation symbol. |
| 70 | function | `test_archive_original_excel_file_rejects_file_archive_path(tmp_path)` | Implementation symbol. |
| 79 | function | `test_archive_and_create_pending_import_batch_records_archive_path(tmp_path)` | Implementation symbol. |
| 106 | function | `test_archive_failure_prevents_import_batch_creation(tmp_path)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_archive_service.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
