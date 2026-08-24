# `tests/test_value_normalizer.py`

[Open source](../../../tests/test_value_normalizer.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for value normalizer, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 101 lines
- **Layer:** `tests`
- **Python module:** `tests.test_value_normalizer`

## Dependencies and integration

- `__future__`
- `datetime`
- `services.value_normalizer`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 17 | function | `test_empty_values_are_detected()` | Implementation symbol. |
| 24 | function | `test_supported_boolean_values_are_normalized()` | Implementation symbol. |
| 34 | function | `test_invalid_boolean_value_is_logged_as_warning()` | Implementation symbol. |
| 50 | function | `test_numeric_values_are_normalized()` | Implementation symbol. |
| 57 | function | `test_invalid_numeric_value_is_logged()` | Implementation symbol. |
| 67 | function | `test_boolean_is_not_accepted_as_number()` | Implementation symbol. |
| 74 | function | `test_dates_are_normalized_to_iso_strings()` | Implementation symbol. |
| 81 | function | `test_invalid_date_is_logged()` | Implementation symbol. |
| 88 | function | `test_text_whitespace_is_normalized()` | Implementation symbol. |
| 93 | function | `test_email_is_lowercased()` | Implementation symbol. |
| 97 | function | `test_phone_number_is_preserved_as_text()` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_value_normalizer.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
