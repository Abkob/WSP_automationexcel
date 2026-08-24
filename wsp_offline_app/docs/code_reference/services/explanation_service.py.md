# `services/explanation_service.py`

[Open source](../../../services/explanation_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Turns semantic similarities and original student evidence into short administrator-facing match explanations.

## File facts

- **Type:** `.py`
- **Size:** 61 lines
- **Layer:** `services`
- **Python module:** `services.explanation_service`

## Dependencies and integration

- `__future__`
- `dataclasses`
- `services.semantic_document_service`
- `typing`

### Referenced by

- `services/semantic_search_service.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 23 | class | `OriginalTextEvidence` | Implementation symbol. |
| 29 | function | `build_local_semantic_explanation(query, profile, score, evidence)` | Implementation symbol. |
| 56 | function | `truncate_explanation_text(value, max_length)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `services/explanation_service.py` when its services responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
