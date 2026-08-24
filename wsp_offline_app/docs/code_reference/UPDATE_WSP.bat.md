# `UPDATE_WSP.bat`

[Open source](../../UPDATE_WSP.bat) · [Code documentation index](../CODE_REFERENCE.md) · [Feature and code flows](../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides a double-clickable Windows entry point that delegates to the corresponding verified PowerShell or Python workflow.

## File facts

- **Type:** `.bat`
- **Size:** 21 lines
- **Layer:** `UPDATE_WSP.bat`

## Dependencies and integration

- No direct imports or external action dependencies were detected.

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 1 | command | `setlocal` | Windows batch step. |
| 2 | command | `title WSP Offline System - Update or Repair` | Windows batch step. |
| 3 | command | `cd /d "%~dp0"` | Windows batch step. |
| 4 | command | `echo.` | Windows batch step. |
| 5 | command | `echo  Updating/repairing the WSP environment...` | Windows batch step. |
| 6 | command | `echo.` | Windows batch step. |
| 7 | command | `powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install.ps1" -NoLaunch` | Windows batch step. |
| 8 | command | `set "UPDATE_EXIT=%ERRORLEVEL%"` | Windows batch step. |
| 9 | command | `echo.` | Windows batch step. |
| 10 | command | `if not "%UPDATE_EXIT%"=="0" (` | Windows batch step. |
| 11 | command | `echo  Update/repair did not complete. See data\install.log.` | Windows batch step. |
| 12 | command | `) else (` | Windows batch step. |
| 13 | command | `echo  Update/repair completed successfully.` | Windows batch step. |
| 14 | command | `)` | Windows batch step. |
| 15 | command | `echo.` | Windows batch step. |
| 16 | command | `pause` | Windows batch step. |
| 17 | command | `exit /b %UPDATE_EXIT%` | Windows batch step. |

## Runtime flow

1. The application or development workflow loads `UPDATE_WSP.bat` when its UPDATE_WSP.bat responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
