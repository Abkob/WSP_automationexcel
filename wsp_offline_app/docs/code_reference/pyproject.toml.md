# `pyproject.toml`

[Open source](../../pyproject.toml) · [Code documentation index](../CODE_REFERENCE.md) · [Feature and code flows](../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Defines project metadata, supported Python version, dependencies, and pytest configuration.

## File facts

- **Type:** `.toml`
- **Size:** 29 lines
- **Layer:** `pyproject.toml`

## Dependencies and integration

- No direct imports or external action dependencies were detected.

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 1 | configuration section | `project` | TOML configuration section. |
| 1 | configuration section | `project.optional-dependencies` | TOML configuration section. |
| 1 | configuration section | `tool.pytest.ini_options` | TOML configuration section. |

## Runtime flow

1. The application or development workflow loads `pyproject.toml` when its pyproject.toml responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
