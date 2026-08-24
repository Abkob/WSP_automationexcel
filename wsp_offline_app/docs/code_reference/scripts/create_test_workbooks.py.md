# `scripts/create_test_workbooks.py`

[Open source](../../../scripts/create_test_workbooks.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Supports repeatable development testbench execution and produces auditable local test data or reports.

## File facts

- **Type:** `.py`
- **Size:** 459 lines
- **Layer:** `scripts`
- **Python module:** `scripts.create_test_workbooks`

## Dependencies and integration

- `__future__`
- `collections`
- `copy`
- `openpyxl`
- `pandas`
- `pathlib`
- `random`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 159 | function | `_col_code(major)` | Implementation symbol. |
| 165 | function | `_credits(cls)` | Implementation symbol. |
| 171 | function | `_gpa(probation)` | Implementation symbol. |
| 176 | function | `_astd(gpa)` | Implementation symbol. |
| 183 | function | `_langs(extra_french)` | Implementation symbol. |
| 191 | function | `make_student(stud_id, rng)` | Implementation symbol. |
| 302 | function | `write_single_sheet(rows, path, sheet_name)` | Implementation symbol. |
| 308 | function | `write_multi_sheet(students, path)` | Write the 1 000-student workbook with 3 sheets. |
| 341 | function | `main()` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `scripts/create_test_workbooks.py` when its scripts responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
