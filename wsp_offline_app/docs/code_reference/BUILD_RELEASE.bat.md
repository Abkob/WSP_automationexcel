# `BUILD_RELEASE.bat`

[Open source](../../BUILD_RELEASE.bat) · [Code documentation index](../CODE_REFERENCE.md) · [Feature and code flows](../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides a double-clickable Windows entry point that delegates to the corresponding verified PowerShell or Python workflow.

## File facts

- **Type:** `.bat`
- **Size:** 18 lines
- **Layer:** `BUILD_RELEASE.bat`

## Dependencies and integration

- No direct imports or external action dependencies were detected.

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 1 | command | `setlocal` | Windows batch step. |
| 2 | command | `title WSP Offline System - Build Release Package` | Windows batch step. |
| 3 | command | `cd /d "%~dp0"` | Windows batch step. |
| 4 | command | `powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\build_release.ps1"` | Windows batch step. |
| 5 | command | `set "BUILD_EXIT=%ERRORLEVEL%"` | Windows batch step. |
| 6 | command | `echo.` | Windows batch step. |
| 7 | command | `if not "%BUILD_EXIT%"=="0" (` | Windows batch step. |
| 8 | command | `echo Release build failed.` | Windows batch step. |
| 9 | command | `) else (` | Windows batch step. |
| 10 | command | `echo Release package is ready in the dist folder.` | Windows batch step. |
| 11 | command | `)` | Windows batch step. |
| 12 | command | `echo.` | Windows batch step. |
| 13 | command | `pause` | Windows batch step. |
| 14 | command | `exit /b %BUILD_EXIT%` | Windows batch step. |

## Runtime flow

1. The application or development workflow loads `BUILD_RELEASE.bat` when its BUILD_RELEASE.bat responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
