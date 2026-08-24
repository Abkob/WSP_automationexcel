# `tests/test_preferred_work_grouping_service.py`

[Open source](../../../tests/test_preferred_work_grouping_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for preferred work grouping service, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 130 lines
- **Layer:** `tests`
- **Python module:** `tests.test_preferred_work_grouping_service`

## Dependencies and integration

- `__future__`
- `numpy`
- `services.preferred_work_grouping_service`
- `typing`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 10 | class | `MeaningEmbeddingModel` | Implementation symbol. |
| 46 | function | `test_embedding_grouper_assigns_stable_fields_and_reviews_ambiguous_text()` | Implementation symbol. |
| 61 | function | `test_embedding_grouper_caches_normalized_answers()` | Implementation symbol. |
| 72 | function | `test_embedding_grouper_discovers_repeated_novel_themes_but_not_singletons()` | Implementation symbol. |
| 97 | class | `BrokenEmbeddingModel` | Implementation symbol. |
| 104 | function | `test_embedding_failure_sends_answers_to_review()` | Implementation symbol. |
| 114 | function | `test_explicit_flexibility_is_recognized_without_the_embedding_model()` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_preferred_work_grouping_service.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
