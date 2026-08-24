# `scripts/generate_code_documentation.py`

[Open source](../../../scripts/generate_code_documentation.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides the operational or development utility named generate code documentation.

## File facts

- **Type:** `.py`
- **Size:** 375 lines
- **Layer:** `scripts`
- **Python module:** `scripts.generate_code_documentation`

## Dependencies and integration

- `__future__`
- `ast`
- `collections`
- `pathlib`
- `re`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 81 | function | `source_files()` | Implementation symbol. |
| 96 | function | `display_path(path)` | Implementation symbol. |
| 103 | function | `doc_path(path)` | Implementation symbol. |
| 108 | function | `purpose_for(path)` | Implementation symbol. |
| 146 | function | `python_details(text)` | Implementation symbol. |
| 180 | function | `js_details(text)` | Implementation symbol. |
| 193 | function | `powershell_details(text)` | Implementation symbol. |
| 201 | function | `generic_details(path, text)` | Implementation symbol. |
| 227 | function | `analyze(path)` | Implementation symbol. |
| 250 | function | `local_module(path)` | Implementation symbol. |
| 263 | function | `relative_link(from_doc, target)` | Implementation symbol. |
| 267 | function | `write_reference_pages(items)` | Implementation symbol. |
| 340 | function | `write_index(items)` | Implementation symbol. |
| 364 | function | `main()` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `scripts/generate_code_documentation.py` when its scripts responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
