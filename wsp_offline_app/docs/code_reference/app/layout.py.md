# `app/layout.py`

[Open source](../../../app/layout.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Supports the WSP Offline System as the repository artifact `app/layout.py`.

## File facts

- **Type:** `.py`
- **Size:** 105 lines
- **Layer:** `app`
- **Python module:** `app.layout`

## Dependencies and integration

- `__future__`
- `app.components.sidebar`
- `app.theme`
- `config`
- `database.db`
- `database.models`
- `dataclasses`
- `pathlib`
- `services.analytics_service`
- `sqlalchemy.exc`
- `typing`

### Referenced by

- `app/routes.py`
- `tests/test_ui_layout.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 18 | class | `LayoutStatus` | Implementation symbol. |
| 30 | function | `build_layout_status(settings)` | Implementation symbol. |
| 70 | function | `render_app_shell(ui_module, settings, active_path, page_title, content_renderer, status)` | Implementation symbol. |
| 94 | function | `render_status_bar(ui_module, status)` | Implementation symbol. |
| 101 | function | `render_status_chip(ui_module, icon_name, label, detail)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `app/layout.py` when its app responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
