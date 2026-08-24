# `services/chat_orchestrator.py`

[Open source](../../../services/chat_orchestrator.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Implements the chat orchestrator service used by the local WSP application.

## File facts

- **Type:** `.py`
- **Size:** 53 lines
- **Layer:** `services`
- **Python module:** `services.chat_orchestrator`

## Dependencies and integration

- `__future__`
- `dataclasses`
- `json`
- `services.semantic_service`
- `typing`

### Referenced by

- `services/semantic_search_service.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 14 | class | `ChatSearchIntent` | Implementation symbol. |
| 27 | function | `interpret_chat_search_request(query, chat_runner)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `services/chat_orchestrator.py` when its services responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
