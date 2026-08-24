# `tests/test_embedding_service.py`

[Open source](../../../tests/test_embedding_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for embedding service, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 37 lines
- **Layer:** `tests`
- **Python module:** `tests.test_embedding_service`

## Dependencies and integration

- `__future__`
- `numpy`
- `services.embedding_service`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 8 | function | `test_e5_embedding_text_uses_query_and_passage_prefixes()` | Implementation symbol. |
| 15 | function | `test_non_e5_embedding_text_does_not_add_prefix()` | Implementation symbol. |
| 19 | function | `test_normalize_embedding_matrix_returns_unit_vectors()` | Implementation symbol. |
| 26 | function | `test_sentence_transformer_cache_check_requires_config_weight_and_tokenizer(monkeypatch)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_embedding_service.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
