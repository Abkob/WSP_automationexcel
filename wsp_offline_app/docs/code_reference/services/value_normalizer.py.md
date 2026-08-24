# `services/value_normalizer.py`

[Open source](../../../services/value_normalizer.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Normalizes booleans, numbers, dates, text, email, and phone values while recording non-fatal validation warnings.

## File facts

- **Type:** `.py`
- **Size:** 178 lines
- **Layer:** `services`
- **Python module:** `services.value_normalizer`

## Dependencies and integration

- `__future__`
- `dataclasses`
- `datetime`
- `math`
- `re`
- `typing`

### Referenced by

- `app/web_app.py`
- `services/excel_importer.py`
- `tests/test_value_normalizer.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 15 | class | `NormalizationWarning` | Implementation symbol. |
| 22 | function | `is_empty_value(value)` | Implementation symbol. |
| 32 | function | `add_warning(warnings, column_name, raw_value, message, row_number)` | Implementation symbol. |
| 51 | function | `normalize_text(value)` | Implementation symbol. |
| 59 | function | `normalize_boolean(value, column_name, row_number, warnings)` | Implementation symbol. |
| 96 | function | `normalize_number(value, column_name, row_number, warnings)` | Implementation symbol. |
| 136 | function | `normalize_date(value, column_name, row_number, warnings)` | Implementation symbol. |
| 166 | function | `normalize_email(value)` | Implementation symbol. |
| 171 | function | `normalize_phone_text(value)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `services/value_normalizer.py` when its services responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
