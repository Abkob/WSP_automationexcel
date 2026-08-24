# `tests/test_semantic_service.py`

[Open source](../../../tests/test_semantic_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for semantic service, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 668 lines
- **Layer:** `tests`
- **Python module:** `tests.test_semantic_service`

## Dependencies and integration

- `__future__`
- `config`
- `database.db`
- `database.models`
- `pytest`
- `services.semantic_service`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 39 | function | `test_text_builder_includes_expected_non_private_fields()` | Implementation symbol. |
| 73 | function | `test_empty_fields_do_not_create_noisy_text()` | Implementation symbol. |
| 88 | function | `test_text_builder_output_is_stable()` | Implementation symbol. |
| 120 | function | `test_source_fields_can_select_private_fields_when_explicitly_needed()` | Implementation symbol. |
| 140 | function | `test_extra_columns_are_included_without_overwriting_raw_values()` | Implementation symbol. |
| 154 | function | `test_source_fields_can_disable_automatic_extra_columns()` | Implementation symbol. |
| 166 | function | `test_clean_semantic_value_handles_common_values()` | Implementation symbol. |
| 174 | function | `test_private_field_detection_and_human_labels()` | Implementation symbol. |
| 183 | function | `test_ollama_api_url_normalizes_base_url()` | Implementation symbol. |
| 187 | function | `test_ollama_availability_detects_installed_model()` | Implementation symbol. |
| 204 | function | `test_ollama_availability_reports_missing_server()` | Implementation symbol. |
| 216 | function | `test_ollama_availability_reports_missing_model()` | Implementation symbol. |
| 228 | function | `test_ensure_ollama_model_available_raises_clear_error()` | Implementation symbol. |
| 238 | function | `test_disabled_semantic_search_does_not_call_ollama(tmp_path)` | Implementation symbol. |
| 250 | function | `test_enabled_semantic_search_uses_settings(tmp_path)` | Implementation symbol. |
| 272 | function | `test_run_ollama_chat_uses_mocked_client()` | Implementation symbol. |
| 298 | function | `test_run_ollama_chat_can_request_json_format_and_options()` | Implementation symbol. |
| 317 | function | `test_run_ollama_chat_rejects_empty_prompt_or_response()` | Implementation symbol. |
| 325 | function | `test_semantic_candidates_return_current_non_blank_students(tmp_path)` | Implementation symbol. |
| 349 | function | `test_semantic_candidates_can_include_missing_students(tmp_path)` | Implementation symbol. |
| 369 | function | `test_semantic_candidates_support_source_fields_and_student_id_subset(tmp_path)` | Implementation symbol. |
| 398 | function | `test_semantic_candidate_map_uses_student_id()` | Implementation symbol. |
| 409 | function | `test_semantic_document_hash_is_stable_and_changes_with_text()` | Implementation symbol. |
| 418 | function | `test_semantic_artifact_directory_can_be_created(tmp_path)` | Implementation symbol. |
| 428 | function | `test_semantic_ranking_prompt_contains_query_candidates_and_json_contract()` | Implementation symbol. |
| 443 | function | `test_semantic_ranking_prompt_truncates_long_candidate_text()` | Implementation symbol. |
| 456 | function | `test_parse_semantic_score_accepts_zero_to_one_and_percent_values()` | Implementation symbol. |
| 465 | function | `test_parse_semantic_match_response_filters_sorts_and_limits_matches()` | Implementation symbol. |
| 497 | function | `test_parse_semantic_match_response_rejects_invalid_json()` | Implementation symbol. |
| 502 | function | `test_rank_semantic_candidates_uses_mocked_chat_runner()` | Implementation symbol. |
| 521 | function | `test_rank_semantic_candidates_defaults_to_functional_offline_ranker()` | Implementation symbol. |
| 543 | function | `test_local_semantic_ranker_scores_synonyms_and_respects_minimum_score()` | Implementation symbol. |
| 571 | function | `test_default_semantic_ranker_does_not_cap_local_results_to_qwen_prompt_limit()` | Implementation symbol. |
| 587 | function | `test_semantic_query_tokens_remove_short_words_and_stop_words()` | Implementation symbol. |
| 596 | function | `test_select_semantic_candidates_prefers_lexically_relevant_profiles()` | Implementation symbol. |
| 613 | function | `test_rank_semantic_candidates_limits_prompt_candidates_before_qwen_call()` | Implementation symbol. |
| 637 | function | `test_rank_student_rows_semantically_builds_candidates_from_rows()` | Implementation symbol. |
| 657 | function | `get_semantic_candidates_from_documents_for_test(document)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_semantic_service.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
