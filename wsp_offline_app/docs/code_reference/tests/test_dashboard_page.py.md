# `tests/test_dashboard_page.py`

[Open source](../../../tests/test_dashboard_page.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for dashboard page, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 155 lines
- **Layer:** `tests`
- **Python module:** `tests.test_dashboard_page`

## Dependencies and integration

- `__future__`
- `app.components.chart_card`
- `app.components.import_status_card`
- `app.components.metric_card`
- `app.pages.dashboard_page`
- `config`
- `database.db`
- `database.models`
- `services.analytics_service`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 20 | function | `test_dashboard_formatters()` | Implementation symbol. |
| 26 | function | `test_dashboard_metric_cards_are_built_from_metrics()` | Implementation symbol. |
| 49 | function | `test_dashboard_chart_specs_are_built_from_chart_data()` | Implementation symbol. |
| 66 | function | `test_plotly_figures_preserve_data_and_title_metadata()` | Implementation symbol. |
| 81 | function | `test_chart_alt_text_summarizes_points_for_accessibility()` | Implementation symbol. |
| 87 | function | `test_text_analytics_chart_specs_limit_subjective_terms()` | Implementation symbol. |
| 103 | function | `test_latest_import_rows_for_empty_and_successful_import()` | Implementation symbol. |
| 126 | function | `test_load_dashboard_page_data_creates_empty_database(tmp_path)` | Implementation symbol. |
| 137 | function | `test_load_dashboard_page_data_reads_seeded_database(tmp_path)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_dashboard_page.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
