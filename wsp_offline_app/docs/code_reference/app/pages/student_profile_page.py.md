# `app/pages/student_profile_page.py`

[Open source](../../../../app/pages/student_profile_page.py) · [Code documentation index](../../../CODE_REFERENCE.md) · [Feature and code flows](../../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Defines the legacy/component-level page adapter for student profile page; the production browser shell is served by app/web_app.py.

## File facts

- **Type:** `.py`
- **Size:** 10 lines
- **Layer:** `app`
- **Python module:** `app.pages.student_profile_page`

## Dependencies and integration

- `__future__`
- `config`
- `nicegui`

### Referenced by

- `app/routes.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 6 | function | `render_student_profile_page(_settings)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `app/pages/student_profile_page.py` when its app responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
