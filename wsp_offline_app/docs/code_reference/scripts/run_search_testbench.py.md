# `scripts/run_search_testbench.py`

[Open source](../../../scripts/run_search_testbench.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Supports repeatable development testbench execution and produces auditable local test data or reports.

## File facts

- **Type:** `.py`
- **Size:** 546 lines
- **Layer:** `scripts`
- **Python module:** `scripts.run_search_testbench`

## Dependencies and integration

- `__future__`
- `dataclasses`
- `json`
- `openpyxl`
- `pathlib`
- `statistics`
- `sys`
- `threading`
- `time`
- `urllib.error`
- `urllib.request`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 40 | function | `_post(path, body, timeout)` | Implementation symbol. |
| 57 | function | `search(query, threshold, top_k, gpa_min, gpa_max, probation, financial_aid, include_missing)` | Implementation symbol. |
| 83 | class | `QueryResult` | Implementation symbol. |
| 106 | class | `CheckResult` | Implementation symbol. |
| 113 | class | `Report` | Implementation symbol. |
| 139 | function | `restore_g6(report)` | Implementation symbol. |
| 165 | function | `_force_reimport_g6(report)` | G6 was already imported; patch one cell to break the hash. |
| 191 | function | `main()` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `scripts/run_search_testbench.py` when its scripts responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
