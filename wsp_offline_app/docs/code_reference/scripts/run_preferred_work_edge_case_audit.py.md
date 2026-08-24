# `scripts/run_preferred_work_edge_case_audit.py`

[Open source](../../../scripts/run_preferred_work_edge_case_audit.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Supports repeatable development testbench execution and produces auditable local test data or reports.

## File facts

- **Type:** `.py`
- **Size:** 142 lines
- **Layer:** `scripts`
- **Python module:** `scripts.run_preferred_work_edge_case_audit`

## Dependencies and integration

- `__future__`
- `argparse`
- `config`
- `database.db`
- `database.models`
- `json`
- `pathlib`
- `services.dashboard_intelligence_service`
- `services.embedding_service`
- `services.preferred_work_grouping_service`
- `services.technical_skill_grouping_service`
- `sys`
- `tempfile`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 51 | function | `build_students()` | Implementation symbol. |
| 72 | function | `run_audit(output_path)` | Implementation symbol. |
| 127 | function | `main()` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `scripts/run_preferred_work_edge_case_audit.py` when its scripts responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
