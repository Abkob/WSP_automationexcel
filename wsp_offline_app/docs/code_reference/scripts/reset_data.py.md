# `scripts/reset_data.py`

[Open source](../../../scripts/reset_data.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides the operational or development utility named reset data.

## File facts

- **Type:** `.py`
- **Size:** 124 lines
- **Layer:** `scripts`
- **Python module:** `scripts.reset_data`

## Dependencies and integration

- `__future__`
- `json`
- `pathlib`
- `shutil`
- `sys`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 33 | function | `_read_import_folder_path()` | Implementation symbol. |
| 45 | function | `_count_excel_files(folder)` | Implementation symbol. |
| 49 | function | `_delete_files(folder, label)` | Implementation symbol. |
| 66 | function | `main()` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `scripts/reset_data.py` when its scripts responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
