# `services/embedding_service.py`

[Open source](../../../services/embedding_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Loads the local Sentence Transformer model, prepares model-specific query/document text, normalizes vectors, and verifies offline cache availability.

## File facts

- **Type:** `.py`
- **Size:** 159 lines
- **Layer:** `services`
- **Python module:** `services.embedding_service`

## Dependencies and integration

- `__future__`
- `config`
- `functools`
- `huggingface_hub`
- `numpy`
- `os`
- `pathlib`
- `sentence_transformers`
- `typing`

### Referenced by

- `app/web_app.py`
- `scripts/run_bias_testbench.py`
- `scripts/run_preferred_work_edge_case_audit.py`
- `services/preferred_work_grouping_service.py`
- `services/semantic_search_service.py`
- `services/technical_skill_grouping_service.py`
- `services/vector_store_service.py`
- `tests/test_embedding_service.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 12 | class | `EmbeddingModelUnavailable` | Raised when the configured local embedding model cannot be loaded. |
| 16 | class | `EmbeddingModel` | Implementation symbol. |
| 23 | class | `SentenceTransformerEmbeddingModel` | Implementation symbol. |
| 66 | function | `get_cached_sentence_transformer_model(model_name, local_files_only)` | Implementation symbol. |
| 70 | function | `get_default_embedding_model(settings)` | Implementation symbol. |
| 74 | function | `prepare_embedding_text(text, kind, model_name)` | Implementation symbol. |
| 88 | function | `is_e5_model(model_name)` | Implementation symbol. |
| 92 | function | `is_mxbai_model(model_name)` | Implementation symbol. |
| 96 | function | `normalize_embedding_matrix(vectors)` | Implementation symbol. |
| 107 | function | `is_sentence_transformer_model_cached(model_name)` | Implementation symbol. |
| 120 | function | `local_sentence_transformer_path_is_complete(model_path)` | Implementation symbol. |
| 128 | function | `cached_file_exists(model_name, filename)` | Implementation symbol. |
| 144 | function | `_find_in_hf_cache_snapshots(model_name, filename)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `services/embedding_service.py` when its services responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
