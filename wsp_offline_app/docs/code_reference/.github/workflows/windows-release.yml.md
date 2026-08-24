# `.github/workflows/windows-release.yml`

[Open source](../../../../../.github/workflows/windows-release.yml) · [Code documentation index](../../../CODE_REFERENCE.md) · [Feature and code flows](../../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Builds and uploads the verified Windows installer package on main/tag pushes and attaches assets to versioned GitHub Releases.

## File facts

- **Type:** `.yml`
- **Size:** 41 lines
- **Layer:** `.github`

## Dependencies and integration

- `actions/checkout@v4`
- `actions/upload-artifact@v4`
- `softprops/action-gh-release@v2`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 1 | workflow job | `push` | GitHub Actions job. |
| 1 | workflow job | `workflow_dispatch` | GitHub Actions job. |
| 1 | workflow job | `package` | GitHub Actions job. |

## Runtime flow

1. The application or development workflow loads `.github/workflows/windows-release.yml` when its .github responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
