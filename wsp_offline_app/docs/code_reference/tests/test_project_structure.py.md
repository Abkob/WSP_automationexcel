# `tests/test_project_structure.py`

[Open source](../../../tests/test_project_structure.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for project structure, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 45 lines
- **Layer:** `tests`
- **Python module:** `tests.test_project_structure`

## Dependencies and integration

- `__future__`
- `pathlib`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 9 | function | `test_required_project_files_exist()` | Implementation symbol. |
| 23 | function | `test_required_source_directories_exist()` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_project_structure.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
