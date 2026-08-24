# `tests/test_config.py`

[Open source](../../../tests/test_config.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Provides regression coverage for config, including expected success paths, validation rules, and failure behavior.

## File facts

- **Type:** `.py`
- **Size:** 108 lines
- **Layer:** `tests`
- **Python module:** `tests.test_config`

## Dependencies and integration

- `__future__`
- `config`
- `pathlib`
- `pytest`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 10 | function | `test_default_settings_resolve_inside_project()` | Implementation symbol. |
| 23 | function | `test_testing_settings_use_supplied_data_dir(tmp_path)` | Implementation symbol. |
| 31 | function | `test_native_mode_flag_can_be_read_without_starting_ui(tmp_path)` | Implementation symbol. |
| 37 | function | `test_semantic_ollama_settings_have_local_defaults(tmp_path)` | Implementation symbol. |
| 51 | function | `test_semantic_ollama_settings_can_be_overridden(tmp_path)` | Implementation symbol. |
| 67 | function | `test_ensure_data_directories_creates_all_required_directories(tmp_path)` | Implementation symbol. |
| 78 | function | `test_ensure_data_directories_is_idempotent(tmp_path)` | Implementation symbol. |
| 87 | function | `test_ensure_data_directories_logs_new_directories(tmp_path, caplog)` | Implementation symbol. |
| 96 | function | `test_ensure_data_directories_rejects_file_where_directory_is_expected(tmp_path)` | Implementation symbol. |
| 105 | function | `test_invalid_runtime_mode_is_rejected(tmp_path)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `tests/test_config.py` when its tests responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
