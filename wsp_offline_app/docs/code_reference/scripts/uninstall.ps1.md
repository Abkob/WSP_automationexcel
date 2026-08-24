# `scripts/uninstall.ps1`

[Open source](../../../scripts/uninstall.ps1) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Removes WSP shortcuts and application files safely, with an option to preserve operational data in a timestamped Documents folder.

## File facts

- **Type:** `.ps1`
- **Size:** 65 lines
- **Layer:** `scripts`

## Dependencies and integration

- `Assert-SafeUninstallTarget`
- `ForEach-Object`
- `Get-CimInstance`
- `Move-Item`
- `New-Item`
- `Remove-Item`
- `Set-Location`
- `Where-Object`
- `Write-Host`
- `catch`
- `exit`
- `foreach`
- `function`
- `if`
- `throw`
- `try`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 11 | function | `Assert-SafeUninstallTarget` | PowerShell workflow helper. |

## Runtime flow

1. The application or development workflow loads `scripts/uninstall.ps1` when its scripts responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
