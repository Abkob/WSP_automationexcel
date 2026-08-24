# `app/components/chart_card.py`

[Open source](../../../../app/components/chart_card.py) · [Code documentation index](../../../CODE_REFERENCE.md) · [Feature and code flows](../../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Defines reusable UI data structures and rendering helpers for the chart card area.

## File facts

- **Type:** `.py`
- **Size:** 89 lines
- **Layer:** `app`
- **Python module:** `app.components.chart_card`

## Dependencies and integration

- `__future__`
- `dataclasses`
- `plotly.graph_objects`
- `services.analytics_service`

### Referenced by

- `app/pages/dashboard_page.py`
- `tests/test_dashboard_page.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 14 | class | `ChartSpec` | Implementation symbol. |
| 20 | function | `build_bar_figure(points, title)` | Implementation symbol. |
| 34 | function | `build_pie_figure(points, title)` | Implementation symbol. |
| 48 | function | `style_figure(figure, title, height)` | Implementation symbol. |
| 66 | function | `calculate_bar_height(points)` | Implementation symbol. |
| 70 | function | `build_chart_alt_text(spec, max_points)` | Implementation symbol. |
| 80 | function | `render_chart_card(ui_module, spec)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `app/components/chart_card.py` when its app responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
