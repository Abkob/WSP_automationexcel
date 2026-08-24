# `INSTALL_WSP.bat`

[Open source](../../INSTALL_WSP.bat) · [Code documentation index](../CODE_REFERENCE.md) · [Feature and code flows](../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides a double-clickable Windows entry point that delegates to the corresponding verified PowerShell or Python workflow.

## File facts

- **Type:** `.bat`
- **Size:** 34 lines
- **Layer:** `INSTALL_WSP.bat`

## Dependencies and integration

- No direct imports or external action dependencies were detected.

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 1 | command | `setlocal` | Windows batch step. |
| 2 | command | `title WSP Offline System - One-Click Installer` | Windows batch step. |
| 3 | command | `cd /d "%~dp0"` | Windows batch step. |
| 4 | command | `echo.` | Windows batch step. |
| 5 | command | `echo  ============================================================` | Windows batch step. |
| 6 | command | `echo   WSP Offline System - One-Click Installer` | Windows batch step. |
| 7 | command | `echo  ============================================================` | Windows batch step. |
| 8 | command | `echo.` | Windows batch step. |
| 9 | command | `echo  This installs Python when needed, creates the private app` | Windows batch step. |
| 10 | command | `echo  environment, installs all packages and the local AI model,` | Windows batch step. |
| 11 | command | `echo  verifies the complete installation, and creates shortcuts.` | Windows batch step. |
| 12 | command | `echo.` | Windows batch step. |
| 13 | command | `echo  Install location:` | Windows batch step. |
| 14 | command | `echo  %LOCALAPPDATA%\WSP Offline System` | Windows batch step. |
| 15 | command | `echo.` | Windows batch step. |
| 16 | command | `powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install.ps1"` | Windows batch step. |
| 17 | command | `set "INSTALL_EXIT=%ERRORLEVEL%"` | Windows batch step. |
| 18 | command | `echo.` | Windows batch step. |
| 19 | command | `if not "%INSTALL_EXIT%"=="0" (` | Windows batch step. |
| 20 | command | `echo  Installation did not complete.` | Windows batch step. |
| 21 | command | `echo  Review the error above and the install log, then run this file again.` | Windows batch step. |
| 22 | command | `echo  Log: %LOCALAPPDATA%\WSP Offline System\wsp_offline_app\data\install.log` | Windows batch step. |
| 23 | command | `) else (` | Windows batch step. |
| 24 | command | `echo  Installation completed successfully.` | Windows batch step. |
| 25 | command | `)` | Windows batch step. |
| 26 | command | `echo.` | Windows batch step. |
| 27 | command | `pause` | Windows batch step. |
| 28 | command | `exit /b %INSTALL_EXIT%` | Windows batch step. |

## Runtime flow

1. The application or development workflow loads `INSTALL_WSP.bat` when its INSTALL_WSP.bat responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
