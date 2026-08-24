# `LAUNCH_WSP.bat`

[Open source](../../LAUNCH_WSP.bat) · [Code documentation index](../CODE_REFERENCE.md) · [Feature and code flows](../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides a double-clickable Windows entry point that delegates to the corresponding verified PowerShell or Python workflow.

## File facts

- **Type:** `.bat`
- **Size:** 13 lines
- **Layer:** `LAUNCH_WSP.bat`

## Dependencies and integration

- No direct imports or external action dependencies were detected.

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 1 | command | `setlocal` | Windows batch step. |
| 2 | command | `cd /d "%~dp0"` | Windows batch step. |
| 3 | command | `if not exist "%~dp0.venv\Scripts\pythonw.exe" (` | Windows batch step. |
| 4 | command | `echo WSP is not installed yet. Starting the installer...` | Windows batch step. |
| 5 | command | `call "%~dp0INSTALL_WSP.bat"` | Windows batch step. |
| 6 | command | `exit /b %ERRORLEVEL%` | Windows batch step. |
| 7 | command | `)` | Windows batch step. |
| 8 | command | `start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0wsp_launcher.pyw"` | Windows batch step. |
| 9 | command | `exit /b 0` | Windows batch step. |

## Runtime flow

1. The application or development workflow loads `LAUNCH_WSP.bat` when its LAUNCH_WSP.bat responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
