# `app/components/student_table.py`

[Open source](../../../../app/components/student_table.py) · [Code documentation index](../../../CODE_REFERENCE.md) · [Feature and code flows](../../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Defines reusable UI data structures and rendering helpers for the student table area.

## File facts

- **Type:** `.py`
- **Size:** 109 lines
- **Layer:** `app`
- **Python module:** `app.components.student_table`

## Dependencies and integration

- `__future__`
- `database.models`
- `services.filter_service`
- `typing`

### Referenced by

- `app/pages/filter_page.py`
- `app/web_app.py`
- `tests/test_filter_page_components.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 26 | function | `build_student_table_rows(filter_result)` | Implementation symbol. |
| 37 | function | `student_to_table_row(student, semantic_score, semantic_reason)` | Implementation symbol. |
| 62 | function | `display_text(value)` | Implementation symbol. |
| 69 | function | `format_optional_float(value)` | Implementation symbol. |
| 73 | function | `format_boolean(value)` | Implementation symbol. |
| 81 | function | `format_semantic_score(value)` | Implementation symbol. |
| 85 | function | `format_audit_datetime(value)` | Implementation symbol. |
| 93 | function | `truncate_text(value, max_length)` | Implementation symbol. |
| 100 | function | `render_student_results_table(ui_module, rows)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `app/components/student_table.py` when its app responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
