# `main.py`

[Open source](../../main.py) · [Code documentation index](../CODE_REFERENCE.md) · [Feature and code flows](../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Creates the startup context, prepares runtime folders/database state, and launches the local FastAPI application through Uvicorn.

## File facts

- **Type:** `.py`
- **Size:** 50 lines
- **Layer:** `main.py`
- **Python module:** `main`

## Dependencies and integration

- `__future__`
- `app.web_app`
- `config`
- `database.db`
- `dataclasses`
- `uvicorn`

### Referenced by

- `scripts/verify_install.py`
- `tests/test_main.py`
- `wsp_launcher.pyw`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 10 | class | `StartupContext` | Implementation symbol. |
| 15 | function | `build_startup_context(settings)` | Implementation symbol. |
| 25 | function | `initialize_runtime_database(settings)` | Implementation symbol. |
| 30 | function | `run(settings)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `main.py` when its main.py responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
