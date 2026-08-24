# `tests/test_filter_service.py`

[Open source](../../../tests/test_filter_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for filter service, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 1,130 lines
- **Layer:** `tests`
- **Python module:** `tests.test_filter_service`

## Dependencies and integration

- `__future__`
- `database.db`
- `database.models`
- `pytest`
- `services.filter_service`
- `services.semantic_service`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 32 | function | `test_valid_filter_request_parses()` | Implementation symbol. |
| 48 | function | `test_invalid_numeric_field_name_is_rejected()` | Implementation symbol. |
| 53 | function | `test_invalid_operator_is_rejected()` | Implementation symbol. |
| 58 | function | `test_invalid_numeric_input_is_rejected()` | Implementation symbol. |
| 66 | function | `test_numeric_between_requires_two_values()` | Implementation symbol. |
| 71 | function | `test_text_filter_requires_value_for_matching_operator()` | Implementation symbol. |
| 76 | function | `test_category_filter_requires_values()` | Implementation symbol. |
| 81 | function | `test_semantic_filter_rejects_empty_query()` | Implementation symbol. |
| 86 | function | `test_sort_and_pagination_validation()` | Implementation symbol. |
| 100 | function | `test_empty_filter_returns_all_non_missing_current_students(tmp_path)` | Implementation symbol. |
| 123 | function | `test_empty_filter_can_include_missing_students_when_requested(tmp_path)` | Implementation symbol. |
| 144 | function | `test_empty_filter_supports_sorting_and_pagination(tmp_path)` | Implementation symbol. |
| 169 | function | `seed_numeric_filter_students(session)` | Implementation symbol. |
| 194 | function | `test_numeric_filter_operators(tmp_path, numeric_filter, expected_ids)` | Implementation symbol. |
| 209 | function | `test_numeric_filter_boundary_values(tmp_path)` | Implementation symbol. |
| 226 | function | `test_numeric_filter_excludes_missing_students_by_default(tmp_path)` | Implementation symbol. |
| 246 | function | `seed_boolean_filter_students(session)` | Implementation symbol. |
| 299 | function | `test_boolean_yes_filter(tmp_path)` | Implementation symbol. |
| 313 | function | `test_boolean_no_filter(tmp_path)` | Implementation symbol. |
| 327 | function | `test_boolean_any_filter_is_skipped(tmp_path)` | Implementation symbol. |
| 341 | function | `test_boolean_filter_combinations(tmp_path)` | Implementation symbol. |
| 381 | function | `test_boolean_filter_accepts_expected_boolean_fields(field_name)` | Implementation symbol. |
| 385 | function | `seed_category_filter_students(session)` | Implementation symbol. |
| 420 | function | `test_category_single_select_filter(tmp_path)` | Implementation symbol. |
| 434 | function | `test_category_multi_select_filter(tmp_path)` | Implementation symbol. |
| 451 | function | `test_category_filter_handles_special_characters(tmp_path)` | Implementation symbol. |
| 468 | function | `test_category_empty_value_filter(tmp_path)` | Implementation symbol. |
| 482 | function | `test_category_filter_applies_to_expected_category_fields(tmp_path)` | Implementation symbol. |
| 502 | function | `seed_text_filter_students(session)` | Implementation symbol. |
| 546 | function | `test_text_contains_is_case_insensitive(tmp_path)` | Implementation symbol. |
| 563 | function | `test_text_exact_match(tmp_path)` | Implementation symbol. |
| 577 | function | `test_text_starts_with_and_ends_with(tmp_path)` | Implementation symbol. |
| 593 | function | `test_text_empty_values(tmp_path)` | Implementation symbol. |
| 609 | function | `test_text_does_not_contain_includes_nulls(tmp_path)` | Implementation symbol. |
| 623 | function | `test_text_special_characters_are_treated_as_literal_text(tmp_path)` | Implementation symbol. |
| 639 | function | `test_sql_injection_like_text_is_treated_as_text(tmp_path)` | Implementation symbol. |
| 656 | function | `seed_combined_filter_students(session)` | Implementation symbol. |
| 708 | function | `test_combined_numeric_plus_boolean_filters(tmp_path)` | Implementation symbol. |
| 728 | function | `test_combined_category_plus_text_filters(tmp_path)` | Implementation symbol. |
| 748 | function | `test_combined_all_supported_filter_types_together(tmp_path)` | Implementation symbol. |
| 771 | function | `test_combined_filters_support_pagination(tmp_path)` | Implementation symbol. |
| 793 | function | `test_combined_filters_support_sorting(tmp_path)` | Implementation symbol. |
| 813 | function | `test_combined_filters_return_selected_columns_and_metadata(tmp_path)` | Implementation symbol. |
| 839 | function | `test_filter_results_can_select_student_audit_timestamps(tmp_path)` | Implementation symbol. |
| 859 | function | `test_filter_request_json_round_trip()` | Implementation symbol. |
| 875 | function | `test_save_and_load_filter_preset_round_trip(tmp_path)` | Implementation symbol. |
| 895 | function | `test_duplicate_filter_preset_name_is_rejected(tmp_path)` | Implementation symbol. |
| 908 | function | `test_invalid_preset_cannot_run(tmp_path)` | Implementation symbol. |
| 927 | function | `test_rename_filter_preset(tmp_path)` | Implementation symbol. |
| 944 | function | `test_delete_filter_preset_does_not_affect_students(tmp_path)` | Implementation symbol. |
| 963 | function | `test_load_or_delete_missing_preset_raises_clear_error(tmp_path)` | Implementation symbol. |
| 976 | function | `test_filter_run_log_is_created(tmp_path)` | Implementation symbol. |
| 995 | function | `test_filter_run_log_stores_result_count_and_preset_id(tmp_path)` | Implementation symbol. |
| 1016 | function | `test_export_link_is_added_when_export_happens(tmp_path)` | Implementation symbol. |
| 1043 | function | `test_export_log_requires_existing_filter_run(tmp_path)` | Implementation symbol. |
| 1053 | function | `test_semantic_filter_combines_with_numeric_filter(tmp_path)` | Implementation symbol. |
| 1097 | function | `test_semantic_filter_combines_with_boolean_filter(tmp_path)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_filter_service.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
