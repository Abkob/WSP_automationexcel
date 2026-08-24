# `scripts/build_release.ps1`

[Open source](../../../scripts/build_release.ps1) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Builds the distributable Windows ZIP, internal SHA-256 manifest, external checksum, and clean release folder structure.

## File facts

- **Type:** `.ps1`
- **Size:** 134 lines
- **Layer:** `scripts`

## Dependencies and integration

- `Assert-SafeStagePath`
- `Compress-Archive`
- `Copy-Item`
- `Copy-ReleaseItem`
- `ForEach-Object`
- `Get-ChildItem`
- `New-Item`
- `Remove-Item`
- `See`
- `Set-Content`
- `Sort-Object`
- `WSP`
- `Where-Object`
- `Write-Host`
- `call`
- `exit`
- `foreach`
- `function`
- `if`
- `throw`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 18 | function | `Assert-SafeStagePath` | PowerShell workflow helper. |
| 29 | function | `Copy-ReleaseItem` | PowerShell workflow helper. |

## Runtime flow

1. The application or development workflow loads `scripts/build_release.ps1` when its scripts responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
