# `services/archive_service.py`

[Open source](../../../services/archive_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Copies source workbooks into the protected archive and creates pending import-batch records before database changes.

## File facts

- **Type:** `.py`
- **Size:** 110 lines
- **Layer:** `services`
- **Python module:** `services.archive_service`

## Dependencies and integration

- `__future__`
- `database.models`
- `dataclasses`
- `datetime`
- `pathlib`
- `re`
- `services.excel_importer`
- `shutil`
- `sqlalchemy.orm`

### Referenced by

- `app/web_app.py`
- `tests/test_archive_service.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 15 | class | `ArchiveError` | Base error for archive failures. |
| 19 | class | `ArchiveIntegrityError` | Raised when an archived file does not match the original hash. |
| 24 | class | `ArchiveResult` | Implementation symbol. |
| 31 | function | `safe_filename_part(value)` | Implementation symbol. |
| 37 | function | `build_archive_filename(source_path, file_hash, archived_at)` | Implementation symbol. |
| 44 | function | `archive_original_excel_file(source_path, archive_dir, file_hash, archived_at)` | Implementation symbol. |
| 85 | function | `archive_and_create_pending_import_batch(session, source_path, archive_dir, file_hash, archived_at)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `services/archive_service.py` when its services responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
