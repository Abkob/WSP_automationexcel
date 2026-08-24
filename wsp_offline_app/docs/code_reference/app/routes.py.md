# `app/routes.py`

[Open source](../../../app/routes.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Supports the WSP Offline System as the repository artifact `app/routes.py`.

## File facts

- **Type:** `.py`
- **Size:** 55 lines
- **Layer:** `app`
- **Python module:** `app.routes`

## Dependencies and integration

- `__future__`
- `app.layout`
- `app.pages.dashboard_page`
- `app.pages.filter_page`
- `app.pages.history_page`
- `app.pages.import_page`
- `app.pages.settings_page`
- `app.pages.student_profile_page`
- `app.theme`
- `config`
- `dataclasses`
- `nicegui`
- `typing`

### Referenced by

- `tests/test_ui_layout.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 18 | class | `PageRoute` | Implementation symbol. |
| 34 | function | `register_routes(settings, ui_module)` | Implementation symbol. |
| 44 | function | `make_page_handler(ui_module, settings, route)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `app/routes.py` when its app responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
