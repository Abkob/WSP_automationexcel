# `scripts/create_testbench.py`

[Open source](../../../scripts/create_testbench.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Supports repeatable development testbench execution and produces auditable local test data or reports.

## File facts

- **Type:** `.py`
- **Size:** 864 lines
- **Layer:** `scripts`
- **Python module:** `scripts.create_testbench`

## Dependencies and integration

- `__future__`
- `copy`
- `openpyxl`
- `openpyxl.styles`
- `pathlib`
- `random`
- `shutil`
- `sys`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 93 | function | `_make_student(sid, prob, aid, dorms, major_idx, cls, rng)` | Implementation symbol. |
| 162 | function | `_write_wb(rows, path, columns, sheet_name, data_keys)` | data_keys: if supplied, use these keys to read row values (positionally |
| 195 | function | `_students(start, count, **kwargs)` | Implementation symbol. |
| 203 | function | `gen_A(out)` | Implementation symbol. |
| 276 | function | `gen_B(out)` | Implementation symbol. |
| 344 | function | `gen_C(out)` | Implementation symbol. |
| 439 | function | `gen_D(out)` | Implementation symbol. |
| 516 | function | `gen_E(out)` | Implementation symbol. |
| 600 | function | `gen_F(out)` | Implementation symbol. |
| 730 | function | `gen_G(out)` | Implementation symbol. |
| 784 | function | `main()` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `scripts/create_testbench.py` when its scripts responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
