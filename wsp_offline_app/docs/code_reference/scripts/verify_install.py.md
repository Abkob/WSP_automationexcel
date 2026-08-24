# `scripts/verify_install.py`

[Open source](../../../scripts/verify_install.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Verifies required modules, writable data paths, SQLite initialization, application routes, and offline embedding generation.

## File facts

- **Type:** `.py`
- **Size:** 82 lines
- **Layer:** `scripts`
- **Python module:** `scripts.verify_install`

## Dependencies and integration

- `__future__`
- `app.web_app`
- `argparse`
- `config`
- `importlib`
- `main`
- `os`
- `pathlib`
- `sentence_transformers`
- `sys`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 15 | function | `verify_imports()` | Implementation symbol. |
| 32 | function | `verify_application()` | Implementation symbol. |
| 53 | function | `verify_model()` | Implementation symbol. |
| 64 | function | `main()` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `scripts/verify_install.py` when its scripts responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
