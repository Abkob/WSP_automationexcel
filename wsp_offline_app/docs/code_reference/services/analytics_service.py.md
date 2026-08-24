# `services/analytics_service.py`

[Open source](../../../services/analytics_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Calculates dashboard metrics, chart series, latest-import summaries, and text-frequency analytics from current records.

## File facts

- **Type:** `.py`
- **Size:** 391 lines
- **Layer:** `services`
- **Python module:** `services.analytics_service`

## Dependencies and integration

- `__future__`
- `collections`
- `database.models`
- `dataclasses`
- `re`
- `sqlalchemy`
- `sqlalchemy.orm`
- `statistics`
- `typing`

### Referenced by

- `app/components/chart_card.py`
- `app/components/import_status_card.py`
- `app/layout.py`
- `app/pages/dashboard_page.py`
- `app/web_app.py`
- `services/dashboard_intelligence_service.py`
- `services/preferred_work_grouping_service.py`
- `services/technical_skill_grouping_service.py`
- `tests/test_analytics_service.py`
- `tests/test_dashboard_page.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 16 | class | `DashboardMetrics` | Implementation symbol. |
| 30 | class | `ChartPoint` | Implementation symbol. |
| 36 | class | `DashboardCharts` | Implementation symbol. |
| 46 | class | `LatestImportSummary` | Implementation symbol. |
| 60 | class | `TextFrequencyPoint` | Implementation symbol. |
| 67 | class | `TextAndSemanticAnalytics` | Implementation symbol. |
| 114 | function | `get_dashboard_metrics(session, include_missing)` | Implementation symbol. |
| 136 | function | `count_true(base_query, condition)` | Implementation symbol. |
| 140 | function | `get_dashboard_charts(session, include_missing)` | Implementation symbol. |
| 153 | function | `get_chart_students(session, include_missing)` | Implementation symbol. |
| 160 | function | `normalize_chart_label(value)` | Implementation symbol. |
| 167 | function | `sort_chart_points(points)` | Implementation symbol. |
| 174 | function | `count_category(students, field_name)` | Implementation symbol. |
| 179 | function | `build_gpa_distribution(students)` | Implementation symbol. |
| 193 | function | `average_number_by_category(students, category_field, number_field)` | Implementation symbol. |
| 214 | function | `count_boolean_by_category(students, category_field, boolean_field)` | Implementation symbol. |
| 227 | function | `count_boolean_distribution(students, field_name)` | Implementation symbol. |
| 245 | function | `get_latest_import_summary(session)` | Implementation symbol. |
| 264 | function | `get_text_and_semantic_analytics(session, include_missing, term_clusterer)` | Implementation symbol. |
| 299 | function | `collect_raw_source_text(students)` | Implementation symbol. |
| 315 | function | `count_terms_for_students(students, category, field_names, split_on_and, term_clusterer)` | Implementation symbol. |
| 353 | function | `split_subjective_terms(value, split_on_and)` | Implementation symbol. |
| 362 | function | `normalize_subjective_term(value)` | Implementation symbol. |
| 379 | function | `clean_text_value(value)` | Implementation symbol. |
| 385 | function | `title_preserving_acronyms(value)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `services/analytics_service.py` when its services responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
