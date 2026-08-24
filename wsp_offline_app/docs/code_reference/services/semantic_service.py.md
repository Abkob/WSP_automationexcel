# `services/semantic_service.py`

[Open source](../../../services/semantic_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides lexical semantic fallbacks, optional local Ollama integration, prompt parsing, and model-availability reporting.

## File facts

- **Type:** `.py`
- **Size:** 888 lines
- **Layer:** `services`
- **Python module:** `services.semantic_service`

## Dependencies and integration

- `__future__`
- `config`
- `database.models`
- `dataclasses`
- `hashlib`
- `json`
- `pathlib`
- `re`
- `sqlalchemy`
- `sqlalchemy.orm`
- `typing`
- `urllib`

### Referenced by

- `app/web_app.py`
- `services/chat_orchestrator.py`
- `services/filter_service.py`
- `services/semantic_search_service.py`
- `tests/test_filter_service.py`
- `tests/test_semantic_search_service.py`
- `tests/test_semantic_service.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 132 | class | `OllamaModelError` | Raised when the local Ollama semantic model cannot be used. |
| 137 | class | `SemanticTextField` | Implementation symbol. |
| 144 | class | `SemanticTextDocument` | Implementation symbol. |
| 151 | class | `SemanticCandidate` | Implementation symbol. |
| 159 | class | `SemanticMatch` | Implementation symbol. |
| 167 | class | `OllamaModelStatus` | Implementation symbol. |
| 181 | function | `build_student_semantic_document(student, include_private_fields, source_fields, include_extra_columns)` | Implementation symbol. |
| 214 | function | `build_student_semantic_text(student, include_private_fields, source_fields, include_extra_columns)` | Implementation symbol. |
| 229 | function | `get_semantic_candidates(session, include_missing, source_fields, include_private_fields, include_extra_columns, student_ids)` | Implementation symbol. |
| 266 | function | `build_semantic_candidates_from_students(students, source_fields, include_private_fields, include_extra_columns)` | Implementation symbol. |
| 294 | function | `build_semantic_candidate_map(candidates)` | Implementation symbol. |
| 298 | function | `hash_semantic_document(document)` | Implementation symbol. |
| 315 | function | `ensure_semantic_artifact_directory(settings)` | Implementation symbol. |
| 320 | function | `build_semantic_ranking_prompt(query, candidates, top_k, minimum_score)` | Implementation symbol. |
| 351 | function | `rank_semantic_candidates(query, candidates, top_k, minimum_score, max_candidates, chat_runner)` | Implementation symbol. |
| 389 | function | `rank_student_rows_semantically(query, students, source_fields, top_k, minimum_score, max_candidates, chat_runner)` | Implementation symbol. |
| 410 | function | `rank_semantic_candidates_locally(query, candidates, top_k, minimum_score)` | Implementation symbol. |
| 445 | function | `select_semantic_candidates_for_query(query, candidates, max_candidates)` | Implementation symbol. |
| 475 | function | `truncate_semantic_prompt_text(value, max_length)` | Implementation symbol. |
| 482 | function | `semantic_query_tokens(query)` | Implementation symbol. |
| 493 | function | `semantic_candidate_lexical_score(query_tokens, candidate)` | Implementation symbol. |
| 503 | function | `expand_semantic_query_terms(query)` | Implementation symbol. |
| 514 | function | `semantic_query_phrases(query)` | Implementation symbol. |
| 524 | function | `score_semantic_candidate(candidate, expanded_terms, query_phrases)` | Implementation symbol. |
| 561 | function | `build_local_semantic_reason(field_scores, matched_terms_by_field)` | Implementation symbol. |
| 576 | function | `normalize_semantic_text(value)` | Implementation symbol. |
| 580 | function | `normalize_semantic_token(value)` | Implementation symbol. |
| 594 | function | `parse_semantic_match_response(response_text, candidate_map, top_k, minimum_score)` | Implementation symbol. |
| 643 | function | `extract_json_payload(response_text)` | Implementation symbol. |
| 659 | function | `parse_semantic_score(value)` | Implementation symbol. |
| 674 | function | `validate_minimum_score(minimum_score)` | Implementation symbol. |
| 681 | function | `default_semantic_field_names(student, include_extra_columns)` | Implementation symbol. |
| 688 | function | `extra_text_column_names(student)` | Implementation symbol. |
| 697 | function | `read_student_value(student, field_name)` | Implementation symbol. |
| 703 | function | `clean_semantic_value(value)` | Implementation symbol. |
| 711 | function | `format_semantic_fields(fields)` | Implementation symbol. |
| 715 | function | `semantic_field_label(field_name)` | Implementation symbol. |
| 719 | function | `humanize_field_name(field_name)` | Implementation symbol. |
| 726 | function | `is_private_semantic_field(field_name)` | Implementation symbol. |
| 731 | function | `normalize_ollama_base_url(base_url)` | Implementation symbol. |
| 738 | function | `ollama_api_url(base_url, path)` | Implementation symbol. |
| 743 | function | `http_get_json(url, timeout_seconds)` | Implementation symbol. |
| 751 | function | `http_post_json(url, payload, timeout_seconds)` | Implementation symbol. |
| 766 | function | `check_semantic_model_status(settings, http_get)` | Implementation symbol. |
| 789 | function | `check_ollama_model_availability(base_url, model_name, timeout_seconds, http_get)` | Implementation symbol. |
| 836 | function | `ensure_ollama_model_available(status)` | Implementation symbol. |
| 844 | function | `run_ollama_chat(prompt, base_url, model_name, system_prompt, timeout_seconds, response_format, think, options, http_post)` | Implementation symbol. |
| 880 | function | `run_local_semantic_chat(prompt, system_prompt)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `services/semantic_service.py` when its services responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
