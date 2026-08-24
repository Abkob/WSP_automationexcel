# `tests/conftest.py`

[Open source](../../../tests/conftest.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Defines shared pytest fixtures and reusable test data used across the automated verification suite.

## File facts

- **Type:** `.py`
- **Size:** 64 lines
- **Layer:** `tests`
- **Python module:** `tests.conftest`

## Dependencies and integration

- `__future__`
- `openpyxl`
- `pathlib`
- `pytest`
- `services.excel_schema`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 12 | function | `sample_workbook_path(tmp_path)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/conftest.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
