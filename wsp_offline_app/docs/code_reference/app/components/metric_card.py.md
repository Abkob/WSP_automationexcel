# `app/components/metric_card.py`

[Open source](../../../../app/components/metric_card.py) · [Code documentation index](../../../CODE_REFERENCE.md) · [Feature and code flows](../../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Defines reusable UI data structures and rendering helpers for the metric card area.

## File facts

- **Type:** `.py`
- **Size:** 30 lines
- **Layer:** `app`
- **Python module:** `app.components.metric_card`

## Dependencies and integration

- `__future__`
- `dataclasses`

### Referenced by

- `app/pages/dashboard_page.py`
- `tests/test_dashboard_page.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 7 | class | `MetricCardData` | Implementation symbol. |
| 22 | function | `render_metric_card(ui_module, metric)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `app/components/metric_card.py` when its app responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
