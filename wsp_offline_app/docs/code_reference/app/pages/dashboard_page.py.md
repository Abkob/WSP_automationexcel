# `app/pages/dashboard_page.py`

[Open source](../../../../app/pages/dashboard_page.py) · [Code documentation index](../../../CODE_REFERENCE.md) · [Feature and code flows](../../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Defines the legacy/component-level page adapter for dashboard page; the production browser shell is served by app/web_app.py.

## File facts

- **Type:** `.py`
- **Size:** 128 lines
- **Layer:** `app`
- **Python module:** `app.pages.dashboard_page`

## Dependencies and integration

- `__future__`
- `app.components.chart_card`
- `app.components.import_status_card`
- `app.components.metric_card`
- `config`
- `database.db`
- `dataclasses`
- `nicegui`
- `services.analytics_service`

### Referenced by

- `app/routes.py`
- `tests/test_dashboard_page.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 24 | class | `DashboardPageData` | Implementation symbol. |
| 31 | function | `load_dashboard_page_data(settings)` | Implementation symbol. |
| 44 | function | `build_metric_cards(metrics)` | Implementation symbol. |
| 59 | function | `build_dashboard_chart_specs(charts)` | Implementation symbol. |
| 70 | function | `build_text_analytics_chart_specs(text_analytics, limit)` | Implementation symbol. |
| 90 | function | `text_frequency_to_chart_points(points, limit)` | Implementation symbol. |
| 94 | function | `format_count(value)` | Implementation symbol. |
| 98 | function | `format_optional_number(value)` | Implementation symbol. |
| 102 | function | `render_dashboard_page(settings)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `app/pages/dashboard_page.py` when its app responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
