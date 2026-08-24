# `services/backup_service.py`

[Open source](../../../services/backup_service.py) · [Code documentation index](../../CODE_REFERENCE.md) · [Feature and code flows](../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Creates timestamped SQLite backups, verifies integrity, records backup metadata, and applies retention policy.

## File facts

- **Type:** `.py`
- **Size:** 239 lines
- **Layer:** `services`
- **Python module:** `services.backup_service`

## Dependencies and integration

- `__future__`
- `database.models`
- `dataclasses`
- `datetime`
- `pathlib`
- `re`
- `shutil`
- `sqlalchemy.orm`
- `sqlite3`

### Referenced by

- `app/web_app.py`
- `tests/test_backup_service.py`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 15 | class | `BackupError` | Base error for backup failures. |
| 19 | class | `BackupIntegrityError` | Raised when a SQLite backup fails integrity verification. |
| 23 | class | `RestoreNotConfirmedError` | Raised when restore is requested without explicit confirmation. |
| 28 | class | `BackupResult` | Implementation symbol. |
| 36 | class | `RestoreResult` | Implementation symbol. |
| 44 | class | `BackupRetentionPreview` | Implementation symbol. |
| 51 | function | `safe_backup_reason(value)` | Implementation symbol. |
| 57 | function | `build_backup_filename(reason, created_at)` | Implementation symbol. |
| 62 | function | `verify_database_integrity(database_path)` | Implementation symbol. |
| 77 | function | `create_database_backup(database_path, backup_dir, reason, session, created_at)` | Implementation symbol. |
| 134 | function | `list_database_backups(backup_dir)` | Implementation symbol. |
| 144 | function | `_remove_sqlite_sidecars(database_path)` | Implementation symbol. |
| 151 | function | `_log_restore_event(database_path, restored_from, pre_restore_backup, restored_at)` | Implementation symbol. |
| 172 | function | `restore_database_from_backup(database_path, backup_path, backup_dir, confirmed, restored_at)` | Implementation symbol. |
| 214 | function | `preview_backup_retention(backup_dir, enabled, keep_latest)` | Implementation symbol. |

## Runtime flow

1. The application or development workflow loads `services/backup_service.py` when its services responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
