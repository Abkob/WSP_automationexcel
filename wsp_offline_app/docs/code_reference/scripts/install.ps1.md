# `scripts/install.ps1`

[Open source](../../../scripts/install.ps1) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Runs verified one-click Windows installation, including package checksums, Python/venv setup, dependencies, model verification, folders, shortcuts, and final health checks.

## File facts

- **Type:** `.ps1`
- **Size:** 369 lines
- **Layer:** `scripts`

## Dependencies and integration

- `Assert-SafeInstallPath`
- `Assert-SourcePayload`
- `Copy-ApplicationPayload`
- `Copy-Item`
- `Get-ChildItem`
- `Install-Python`
- `Invoke-Checked`
- `New-Item`
- `New-Shortcut`
- `Remove-BrokenVirtualEnvironment`
- `Remove-Item`
- `Start-Process`
- `Start-Transcript`
- `Test-FreeSpace`
- `Test-PackageIntegrity`
- `Write-Check`
- `Write-Host`
- `Write-InstallManifest`
- `Write-Step`
- `catch`
- `continue`
- `else`
- `exit`
- `finally`
- `foreach`
- `function`
- `if`
- `product`
- `python`
- `return`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 33 | function | `Write-Step` | PowerShell workflow helper. |
| 39 | function | `Write-Check` | PowerShell workflow helper. |
| 44 | function | `Assert-SafeInstallPath` | PowerShell workflow helper. |
| 58 | function | `Assert-SourcePayload` | PowerShell workflow helper. |
| 71 | function | `Test-PackageIntegrity` | PowerShell workflow helper. |
| 96 | function | `Test-FreeSpace` | PowerShell workflow helper. |
| 107 | function | `Copy-ApplicationPayload` | PowerShell workflow helper. |
| 141 | function | `Test-PythonCandidate` | PowerShell workflow helper. |
| 153 | function | `Find-CompatiblePython` | PowerShell workflow helper. |
| 185 | function | `Install-Python` | PowerShell workflow helper. |
| 197 | function | `Invoke-Checked` | PowerShell workflow helper. |
| 203 | function | `Remove-BrokenVirtualEnvironment` | PowerShell workflow helper. |
| 215 | function | `New-Shortcut` | PowerShell workflow helper. |
| 234 | function | `Write-InstallManifest` | PowerShell workflow helper. |

## Runtime flow

1. The application or development workflow loads `scripts/install.ps1` when its scripts responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
