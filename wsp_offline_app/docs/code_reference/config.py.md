# `config.py`

[Open source](../../config.py) · [Code documentation index](../CODE_REFERENCE.md) · [Feature and code flows](../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Defines immutable application settings, runtime modes, filesystem locations, model configuration, and required data directories.

## File facts

- **Type:** `.py`
- **Size:** 118 lines
- **Layer:** `config.py`
- **Python module:** `config`

## Dependencies and integration

- `__future__`
- `dataclasses`
- `logging`
- `pathlib`

### Referenced by

- `app/layout.py`
- `app/pages/dashboard_page.py`
- `app/pages/filter_page.py`
- `app/pages/history_page.py`
- `app/pages/import_page.py`
- `app/pages/settings_page.py`
- `app/pages/student_profile_page.py`
- `app/routes.py`
- `app/web_app.py`
- `main.py`
- `scripts/audit_semantic_index.py`
- `scripts/run_bias_testbench.py`
- `scripts/run_preferred_work_edge_case_audit.py`
- `scripts/verify_install.py`
- `services/embedding_service.py`
- `services/preferred_work_grouping_service.py`
- `services/semantic_search_service.py`
- `services/semantic_service.py`
- `services/technical_skill_grouping_service.py`
- `tests/test_config.py`
- `tests/test_dashboard_page.py`
- `tests/test_main.py`
- `tests/test_semantic_search_service.py`
- `tests/test_semantic_service.py`
- `tests/test_ui_layout.py`
- `tests/test_web_app.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 15 | class | `AppSettings` | Implementation symbol. |
| 101 | function | `get_default_settings()` | Implementation symbol. |
| 105 | function | `get_testing_settings(data_dir)` | Implementation symbol. |
| 109 | function | `ensure_data_directories(settings)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `config.py` when its config.py responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
