# `scripts/audit_semantic_index.py`

[Open source](../../../scripts/audit_semantic_index.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Audits every stored semantic vector against the current source text and reports coverage, hash consistency, and stale records without modifying data.

## File facts

- **Type:** `.py`
- **Size:** 103 lines
- **Layer:** `scripts`
- **Python module:** `scripts.audit_semantic_index`

## Dependencies and integration

- `__future__`
- `argparse`
- `config`
- `database.db`
- `database.models`
- `json`
- `pathlib`
- `services.semantic_document_service`
- `services.vector_store_service`
- `sqlalchemy.orm`
- `sys`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 20 | function | `audit_semantic_index()` | Implementation symbol. |
| 85 | function | `main()` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `scripts/audit_semantic_index.py` when its scripts responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
