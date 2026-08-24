# `app/components/filter_panel.py`

[Open source](../../../../app/components/filter_panel.py) · [Code documentation index](../../../CODE_REFERENCE.md) · [Feature and code flows](../../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Defines reusable UI data structures and rendering helpers for the filter panel area.

## File facts

- **Type:** `.py`
- **Size:** 173 lines
- **Layer:** `app`
- **Python module:** `app.components.filter_panel`

## Dependencies and integration

- `__future__`
- `dataclasses`
- `services.filter_service`

### Referenced by

- `app/pages/filter_page.py`
- `tests/test_filter_page_components.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 50 | class | `FilterOptionSet` | Implementation symbol. |
| 56 | class | `FilterUiState` | Implementation symbol. |
| 73 | function | `build_filter_request_from_state(state)` | Implementation symbol. |
| 115 | function | `build_gpa_filters(gpa_min, gpa_max)` | Implementation symbol. |
| 126 | function | `build_boolean_filter(field_name, selected_value)` | Implementation symbol. |
| 133 | function | `resolve_boolean_selection(selected_value)` | Implementation symbol. |
| 141 | function | `build_category_filter(field_name, value)` | Implementation symbol. |
| 148 | function | `build_text_filter(field_name, value)` | Implementation symbol. |
| 155 | function | `build_semantic_filter(value)` | Implementation symbol. |
| 162 | function | `clean_text_filter_value(value)` | Implementation symbol. |
| 169 | function | `build_result_summary(total_count, visible_count, applied_filter_count)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `app/components/filter_panel.py` when its app responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
