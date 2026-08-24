# `services/semantic_search_service.py`

[Open source](../../../services/semantic_search_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Synchronizes the FAISS student index, ranks embedding matches, cites original-text evidence, manages index freshness, and provides fallbacks.

## File facts

- **Type:** `.py`
- **Size:** 604 lines
- **Layer:** `services`
- **Python module:** `services.semantic_search_service`

## Dependencies and integration

- `__future__`
- `collections`
- `config`
- `database.models`
- `dataclasses`
- `json`
- `numpy`
- `services.chat_orchestrator`
- `services.embedding_service`
- `services.explanation_service`
- `services.filter_service`
- `services.semantic_document_service`
- `services.semantic_service`
- `services.vector_store_service`
- `sqlalchemy.orm`
- `threading`
- `typing`

### Referenced by

- `app/web_app.py`
- `scripts/run_bias_testbench.py`
- `tests/test_semantic_search_service.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 46 | function | `mark_index_fresh()` | Implementation symbol. |
| 52 | function | `mark_index_stale()` | Implementation symbol. |
| 58 | function | `mark_reindex_started()` | Implementation symbol. |
| 63 | function | `_is_index_fresh()` | True when the background reindex finished and no import has arrived since. |
| 68 | function | `_reindex_in_progress()` | True while the background thread is actively encoding profiles. |
| 85 | function | `_get_query_vector(model, query)` | Implementation symbol. |
| 103 | function | `_get_evidence_vectors(model, evidence_rows)` | Implementation symbol. |
| 135 | function | `rank_original_text_evidence(model, query_vector, profiles, evidence_per_student)` | Implementation symbol. |
| 179 | class | `SemanticIndexSyncResult` | Implementation symbol. |
| 187 | function | `get_default_vector_store(settings)` | Implementation symbol. |
| 191 | function | `rank_student_rows_by_ollama_rag(settings, session, semantic_filter, candidate_rows, chat_runner)` | Implementation symbol. |
| 236 | function | `retrieve_rag_candidate_profiles(query, profiles, candidate_limit)` | Implementation symbol. |
| 263 | function | `build_ollama_rag_prompt(query, profiles, top_k, profile_text_limit)` | Implementation symbol. |
| 291 | function | `run_ollama_rag_chat(settings, prompt, system_prompt)` | Implementation symbol. |
| 304 | function | `normalize_rag_match_scores(matches)` | Implementation symbol. |
| 322 | function | `filter_semantic_matches(matches, minimum_score, top_k)` | Implementation symbol. |
| 332 | function | `compact_rag_profile_text(profile, max_length)` | Implementation symbol. |
| 347 | function | `profile_to_semantic_candidate(profile)` | Implementation symbol. |
| 356 | function | `build_rag_candidate_map(profiles)` | Implementation symbol. |
| 360 | function | `sync_student_semantic_index(session, settings, students, embedding_model, vector_store, prune_stale)` | Implementation symbol. |
| 405 | function | `prune_stale_semantic_records(session, vector_store, active_student_ids)` | Remove vectors and embedding rows for students outside the active dataset. |
| 436 | function | `rank_student_rows_by_vector_search(settings, session, semantic_filter, candidate_rows, embedding_model, vector_store)` | Implementation symbol. |
| 496 | function | `text_match_fallback(semantic_filter, candidate_rows, reason)` | Implementation symbol. |
| 519 | function | `local_retrieval_estimate(semantic_filter, candidate_rows, reason)` | Implementation symbol. |
| 542 | function | `load_existing_semantic_rows(session, model_name)` | Implementation symbol. |
| 554 | function | `profile_needs_embedding(profile, row, indexed_ids)` | Implementation symbol. |
| 570 | function | `upsert_semantic_embedding_rows(session, profiles, model_name, vector_store_name)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `services/semantic_search_service.py` when its services responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
