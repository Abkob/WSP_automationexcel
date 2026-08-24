# `services/vector_store_service.py`

[Open source](../../../services/vector_store_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Persists normalized vectors and metadata, maintains an in-process cache, and performs candidate-restricted cosine-similarity search.

## File facts

- **Type:** `.py`
- **Size:** 234 lines
- **Layer:** `services`
- **Python module:** `services.vector_store_service`

## Dependencies and integration

- `__future__`
- `dataclasses`
- `faiss`
- `json`
- `numpy`
- `pathlib`
- `re`
- `services.embedding_service`
- `threading`
- `typing`

### Referenced by

- `app/web_app.py`
- `scripts/audit_semantic_index.py`
- `services/semantic_search_service.py`
- `tests/test_semantic_search_service.py`
- `tests/test_vector_store_service.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 26 | class | `VectorRecord` | Implementation symbol. |
| 34 | class | `VectorSearchResult` | Implementation symbol. |
| 41 | class | `FaissVectorStore` | Implementation symbol. |
| 219 | function | `write_faiss_index(index_path, matrix)` | Implementation symbol. |
| 231 | function | `safe_collection_name(value)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `services/vector_store_service.py` when its services responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
