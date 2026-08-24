# `requirements.txt`

[Open source](../../requirements.txt) · [Code documentation index](../CODE_REFERENCE.md) · [Feature and code flows](../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Declares the Python packages required to install and reproduce the WSP runtime.

## File facts

- **Type:** `.txt`
- **Size:** 19 lines
- **Layer:** `requirements.txt`

## Dependencies and integration

- No direct imports or external action dependencies were detected.

## Public symbols and executable sections

This file is declarative, a package marker, a dependency lock, or a vendored/static artifact and does not expose first-party callable symbols.

## Runtime flow

1. The application or development workflow loads `requirements.txt` when its requirements.txt responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
