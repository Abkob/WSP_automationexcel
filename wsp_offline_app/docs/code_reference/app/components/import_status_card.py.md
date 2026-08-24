# `app/components/import_status_card.py`

[Open source](../../../../app/components/import_status_card.py) · [Code documentation index](../../../CODE_REFERENCE.md) · [Feature and code flows](../../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Defines reusable UI data structures and rendering helpers for the import status card area.

## File facts

- **Type:** `.py`
- **Size:** 29 lines
- **Layer:** `app`
- **Python module:** `app.components.import_status_card`

## Dependencies and integration

- `__future__`
- `services.analytics_service`

### Referenced by

- `app/pages/dashboard_page.py`
- `tests/test_dashboard_page.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 6 | function | `build_latest_import_rows(summary)` | Implementation symbol. |
| 21 | function | `render_latest_import_card(ui_module, summary)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `app/components/import_status_card.py` when its app responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
