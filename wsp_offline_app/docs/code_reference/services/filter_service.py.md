# `services/filter_service.py`

[Open source](../../../services/filter_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Validates filter requests, composes SQLAlchemy predicates, applies semantic ranking, sorts/paginates results, and stores filter audit records.

## File facts

- **Type:** `.py`
- **Size:** 613 lines
- **Layer:** `services`
- **Python module:** `services.filter_service`

## Dependencies and integration

- `__future__`
- `database.models`
- `dataclasses`
- `services.semantic_service`
- `sqlalchemy`
- `sqlalchemy.orm`
- `typing`

### Referenced by

- `app/components/filter_panel.py`
- `app/components/student_table.py`
- `app/pages/filter_page.py`
- `app/web_app.py`
- `scripts/run_bias_testbench.py`
- `services/export_service.py`
- `services/semantic_search_service.py`
- `tests/test_export_service.py`
- `tests/test_filter_page_components.py`
- `tests/test_filter_service.py`
- `tests/test_semantic_search_service.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 13 | class | `FilterValidationError` | Raised when a filter request contains an invalid field or operator. |
| 17 | class | `FilterPresetError` | Raised when filter preset operations fail. |
| 98 | class | `NumericFilter` | Implementation symbol. |
| 120 | class | `BooleanFilter` | Implementation symbol. |
| 129 | class | `CategoryFilter` | Implementation symbol. |
| 141 | class | `TextFilter` | Implementation symbol. |
| 154 | class | `SemanticFilter` | Implementation symbol. |
| 173 | class | `SortSpec` | Implementation symbol. |
| 183 | class | `PaginationSpec` | Implementation symbol. |
| 202 | class | `FilterRequest` | Implementation symbol. |
| 226 | class | `FilterResult` | Implementation symbol. |
| 238 | function | `validate_field(field_name, allowed_fields)` | Implementation symbol. |
| 243 | function | `validate_operator(operator, allowed_operators)` | Implementation symbol. |
| 248 | function | `validate_numeric_input(value, label)` | Implementation symbol. |
| 253 | function | `execute_filter_request(session, request, semantic_ranker)` | Implementation symbol. |
| 312 | function | `execute_semantic_filter_request(query, request, semantic_ranker)` | Implementation symbol. |
| 348 | function | `default_semantic_ranker(semantic_filter, candidate_rows)` | Implementation symbol. |
| 358 | function | `apply_global_search(query, text)` | Implementation symbol. |
| 368 | function | `count_applied_filters(request)` | Implementation symbol. |
| 379 | function | `serialize_selected_rows(rows, selected_columns, semantic_scores, semantic_reasons)` | Implementation symbol. |
| 409 | function | `build_filter_metadata(request)` | Implementation symbol. |
| 424 | function | `filter_request_to_json(request)` | Implementation symbol. |
| 428 | function | `filter_request_from_json(data)` | Implementation symbol. |
| 454 | function | `save_filter_preset(session, preset_name, request)` | Implementation symbol. |
| 467 | function | `load_filter_preset(session, preset_name)` | Implementation symbol. |
| 474 | function | `rename_filter_preset(session, preset_id, new_name)` | Implementation symbol. |
| 492 | function | `delete_filter_preset(session, preset_id)` | Implementation symbol. |
| 500 | function | `log_filter_run(session, request, result_count, preset_id)` | Implementation symbol. |
| 517 | function | `log_filter_export(session, filter_run_id, export_path, row_count)` | Implementation symbol. |
| 537 | function | `apply_numeric_filter(query, numeric_filter)` | Implementation symbol. |
| 561 | function | `apply_boolean_filter(query, boolean_filter)` | Implementation symbol. |
| 569 | function | `apply_category_filter(query, category_filter)` | Implementation symbol. |
| 583 | function | `escape_like_text(value, escape_char)` | Implementation symbol. |
| 591 | function | `apply_text_filter(query, text_filter)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `services/filter_service.py` when its services responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
