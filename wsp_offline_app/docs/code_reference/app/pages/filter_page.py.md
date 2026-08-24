# `app/pages/filter_page.py`

[Open source](../../../../app/pages/filter_page.py) · [Code documentation index](../../../CODE_REFERENCE.md) · [Feature and code flows](../../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Defines the legacy/component-level page adapter for filter page; the production browser shell is served by app/web_app.py.

## File facts

- **Type:** `.py`
- **Size:** 243 lines
- **Layer:** `app`
- **Python module:** `app.pages.filter_page`

## Dependencies and integration

- `__future__`
- `app.components.filter_panel`
- `app.components.student_table`
- `config`
- `database.db`
- `database.models`
- `dataclasses`
- `nicegui`
- `services.export_service`
- `services.filter_service`

### Referenced by

- `app/routes.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 24 | class | `FilterPageData` | Implementation symbol. |
| 30 | function | `load_filter_page_data(settings)` | Implementation symbol. |
| 37 | function | `execute_filter_for_settings(settings, request, log_run)` | Implementation symbol. |
| 49 | function | `load_filter_options(settings)` | Implementation symbol. |
| 60 | function | `load_distinct_text_options(session, field_name, limit)` | Implementation symbol. |
| 73 | function | `export_filter_result(settings, request)` | Implementation symbol. |
| 92 | function | `render_filter_page(settings)` | Implementation symbol. |
| 239 | function | `optional_float(value)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `app/pages/filter_page.py` when its app responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
