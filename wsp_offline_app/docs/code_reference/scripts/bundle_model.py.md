# `scripts/bundle_model.py`

[Open source](../../../scripts/bundle_model.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides the operational or development utility named bundle model.

## File facts

- **Type:** `.py`
- **Size:** 77 lines
- **Layer:** `scripts`
- **Python module:** `scripts.bundle_model`

## Dependencies and integration

- `__future__`
- `os`
- `pathlib`
- `shutil`
- `sys`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 21 | function | `find_hf_cache()` | Implementation symbol. |
| 40 | function | `bundle_model()` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `scripts/bundle_model.py` when its scripts responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
