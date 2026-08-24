# `database/queries.py`

[Open source](../../../database/queries.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides reusable database query helpers for current-student and import-history access.

## File facts

- **Type:** `.py`
- **Size:** 3 lines
- **Layer:** `database`
- **Python module:** `database.queries`

## Dependencies and integration

- No direct imports or external action dependencies were detected.

## Public symbols and executable sections

This file is declarative, a package marker, a dependency lock, or a vendored/static artifact and does not expose first-party callable symbols.

## Runtime flow

1. The application or development workflow loads `database/queries.py` when its database responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
