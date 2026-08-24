# `tests/test_analytics_service.py`

[Open source](../../../tests/test_analytics_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for analytics service, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 510 lines
- **Layer:** `tests`
- **Python module:** `tests.test_analytics_service`

## Dependencies and integration

- `__future__`
- `database.db`
- `database.models`
- `services.analytics_service`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 17 | function | `test_dashboard_metrics_on_empty_database(tmp_path)` | Implementation symbol. |
| 37 | function | `test_dashboard_metrics_on_fixture_database(tmp_path)` | Implementation symbol. |
| 99 | function | `test_dashboard_metrics_can_include_or_exclude_missing_students(tmp_path)` | Implementation symbol. |
| 125 | function | `test_dashboard_chart_data_on_empty_database(tmp_path)` | Implementation symbol. |
| 147 | function | `test_dashboard_chart_data_shape_and_values(tmp_path)` | Implementation symbol. |
| 194 | function | `test_dashboard_chart_data_handles_null_values(tmp_path)` | Implementation symbol. |
| 227 | function | `test_dashboard_chart_data_ordering_is_deterministic(tmp_path)` | Implementation symbol. |
| 254 | function | `test_dashboard_charts_can_include_or_exclude_missing_students(tmp_path)` | Implementation symbol. |
| 279 | function | `test_latest_import_summary_with_no_imports(tmp_path)` | Implementation symbol. |
| 290 | function | `test_latest_import_summary_with_successful_import(tmp_path)` | Implementation symbol. |
| 330 | function | `test_latest_import_summary_with_failed_import(tmp_path)` | Implementation symbol. |
| 359 | function | `test_preferred_work_normalization_and_distribution(tmp_path)` | Implementation symbol. |
| 384 | function | `test_technical_skills_frequency_splits_and_dedupes_per_student(tmp_path)` | Implementation symbol. |
| 410 | function | `test_languages_frequency_combines_written_and_spoken_with_deduping(tmp_path)` | Implementation symbol. |
| 438 | function | `test_text_analytics_can_cluster_similar_terms_with_mocked_semantic_clusterer(tmp_path)` | Implementation symbol. |
| 465 | function | `test_text_analytics_keeps_raw_source_text_and_does_not_mutate_students(tmp_path)` | Implementation symbol. |
| 483 | function | `test_text_analytics_excludes_missing_students_by_default(tmp_path)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_analytics_service.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
