# `services/student_profile_service.py`

[Open source](../../../services/student_profile_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Assembles the holistic student profile payload from current data, retained history, support flags, skills, and extra workbook columns.

## File facts

- **Type:** `.py`
- **Size:** 335 lines
- **Layer:** `services`
- **Python module:** `services.student_profile_service`

## Dependencies and integration

- `__future__`
- `database.models`
- `datetime`
- `re`
- `sqlalchemy`
- `typing`

### Referenced by

- `app/web_app.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 83 | function | `lookup_students(session, query, limit)` | Implementation symbol. |
| 121 | function | `build_student_profile_payload(session, student_id)` | Implementation symbol. |
| 245 | function | `_split_tags(value)` | Implementation symbol. |
| 252 | function | `_initials(name)` | Implementation symbol. |
| 257 | function | `_build_badges(student)` | Implementation symbol. |
| 272 | function | `_build_overview(student)` | Implementation symbol. |
| 288 | function | `_enrollment_label(student)` | Implementation symbol. |
| 300 | function | `_format_metric(value, decimals)` | Implementation symbol. |
| 309 | function | `_history_title(change_type)` | Implementation symbol. |
| 317 | function | `_humanize_key(value)` | Implementation symbol. |
| 321 | function | `_value_kind(value)` | Implementation symbol. |
| 331 | function | `_json_value(value)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `services/student_profile_service.py` when its services responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
