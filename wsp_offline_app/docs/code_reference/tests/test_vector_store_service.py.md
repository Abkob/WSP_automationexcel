# `tests/test_vector_store_service.py`

[Open source](../../../tests/test_vector_store_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for vector store service, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 72 lines
- **Layer:** `tests`
- **Python module:** `tests.test_vector_store_service`

## Dependencies and integration

- `__future__`
- `numpy`
- `services.vector_store_service`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 8 | function | `test_faiss_vector_store_upserts_and_queries_by_similarity(tmp_path)` | Implementation symbol. |
| 27 | function | `test_vector_store_query_respects_candidate_ids_and_minimum_score(tmp_path)` | Implementation symbol. |
| 47 | function | `test_vector_store_upsert_replaces_existing_record(tmp_path)` | Implementation symbol. |
| 59 | function | `test_vector_store_delete_removes_only_requested_records(tmp_path)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_vector_store_service.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
