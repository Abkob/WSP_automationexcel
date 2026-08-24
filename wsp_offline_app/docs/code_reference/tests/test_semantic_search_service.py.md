# `tests/test_semantic_search_service.py`

[Open source](../../../tests/test_semantic_search_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for semantic search service, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 352 lines
- **Layer:** `tests`
- **Python module:** `tests.test_semantic_search_service`

## Dependencies and integration

- `__future__`
- `config`
- `database.db`
- `database.models`
- `json`
- `numpy`
- `pathlib`
- `re`
- `services.filter_service`
- `services.semantic_document_service`
- `services.semantic_search_service`
- `services.semantic_service`
- `services.vector_store_service`
- `typing`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 28 | class | `MeaningEmbeddingModel` | Implementation symbol. |
| 43 | class | `BrokenEmbeddingModel` | Implementation symbol. |
| 50 | function | `meaning_vector(text)` | Implementation symbol. |
| 62 | function | `make_settings(tmp_path)` | Implementation symbol. |
| 66 | function | `make_session_factory(tmp_path)` | Implementation symbol. |
| 72 | function | `test_semantic_index_sync_embeds_only_new_or_changed_profiles(tmp_path)` | Implementation symbol. |
| 102 | function | `test_semantic_index_sync_prunes_students_outside_active_dataset(tmp_path)` | Implementation symbol. |
| 135 | function | `test_vector_search_retrieves_vague_related_profile_without_exact_keyword_overlap(tmp_path)` | Implementation symbol. |
| 177 | function | `test_structured_filters_are_applied_before_vector_search(tmp_path)` | Implementation symbol. |
| 210 | function | `test_qwen_or_embedding_unavailable_falls_back_to_text_match(tmp_path)` | Implementation symbol. |
| 238 | function | `test_ollama_rag_ranker_sends_retrieved_profiles_to_local_model(tmp_path)` | Implementation symbol. |
| 301 | function | `test_ollama_rag_retrieval_limits_candidates_before_model_prompt()` | Implementation symbol. |
| 318 | function | `test_compact_rag_profile_prioritizes_matching_fields()` | Implementation symbol. |
| 341 | function | `test_qwen_zero_scores_are_repaired_from_rank_order()` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_semantic_search_service.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
