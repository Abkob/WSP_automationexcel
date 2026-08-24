# `tests/test_main.py`

[Open source](../../../tests/test_main.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for main, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 20 lines
- **Layer:** `tests`
- **Python module:** `tests.test_main`

## Dependencies and integration

- `__future__`
- `config`
- `main`
- `pathlib`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 9 | function | `test_build_startup_context_creates_data_directories(tmp_path)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_main.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
