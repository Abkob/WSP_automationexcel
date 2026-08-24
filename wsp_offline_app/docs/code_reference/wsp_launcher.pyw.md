# `wsp_launcher.pyw`

[Open source](../../wsp_launcher.pyw) · [Code documentation index](../CODE_REFERENCE.md) · [Feature and code flows](../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides the Windows desktop/tray launch experience, single-instance behavior, browser opening, process logging, and graceful shutdown controls.

## File facts

- **Type:** `.pyw`
- **Size:** 220 lines
- **Layer:** `wsp_launcher.pyw`
- **Python module:** `wsp_launcher`

## Dependencies and integration

- `PIL`
- `__future__`
- `app.web_app`
- `ctypes`
- `io`
- `logging`
- `main`
- `numpy`
- `os`
- `pathlib`
- `pystray`
- `socket`
- `subprocess`
- `sys`
- `threading`
- `time`
- `uvicorn`
- `webbrowser`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 52 | function | `_is_port_in_use(port)` | Implementation symbol. |
| 57 | function | `_wait_for_server(port, timeout)` | Implementation symbol. |
| 66 | function | `_fatal(msg)` | Implementation symbol. |
| 76 | function | `_make_tray_icon()` | Return a 64×64 RGBA tray icon using the AUB seal from the static folder. |
| 106 | function | `_open_app_window(url)` | Open the URL in a dedicated app window. |
| 145 | function | `main()` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `wsp_launcher.pyw` when its wsp_launcher.pyw responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
