# Operations, security, privacy, recovery, and testing

[Documentation home](README.md) · [User manual](USER_MANUAL.md) · [Architecture](ARCHITECTURE.md)

## Local-first privacy

- The server listens only on `127.0.0.1`, not the network interface.
- SQLite, student records, histories, exports, backups, model cache, and FAISS index remain local.
- Semantic matching uses the downloaded local model and does not require a cloud API.
- Optional Ollama support is local and skipped in normal embedding search/testing unless explicitly configured.
- Browser-saved filter preferences remain in local browser storage.
- Exports and copied backups become externally shareable files; administrators remain responsible for institutional handling rules.

## Installer verification

The one-click setup:

1. requires 64-bit Windows and at least 6 GB free space;
2. validates the internal `PACKAGE_MANIFEST.sha256`;
3. installs under `%LOCALAPPDATA%\WSP Offline System`;
4. detects Python 3.11–3.13 or installs Python 3.12 through `winget`;
5. creates a private `.venv`;
6. installs requirements and runs `pip check`;
7. downloads and encodes with the offline model;
8. creates operational folders;
9. initializes SQLite and verifies routes/write access;
10. creates Desktop/Start Menu shortcuts and an installation manifest.

The external `.sha256` verifies the ZIP download. SHA-256 detects damage/tampering but is not publisher code signing.

## Operational safeguards

| Risk | Safeguard |
|---|---|
| Duplicate workbook | SHA-256 file hash uniqueness and duplicate rejection |
| Invalid/empty import | Required headers/data/usable `STUD_ID`; transaction aborts before replacing population |
| Partial merge | Single import transaction with rollback |
| Schema drift | Dynamic column registry, extra-column preservation, missing/new column reporting |
| Source loss | Workbook archive and retained current file |
| Database corruption | SQLite pragmas, integrity checks, pre/post backups |
| Incorrect restore | Selected backup verification + emergency pre-restore backup + post-copy verification |
| Accidental manual edit | Editable-field allowlist + pre-edit backup + cancel path |
| Missing later students | Marked missing and retained; not deleted |
| Stale semantic index | Profile hashes, active-ID coverage, incremental sync, forced re-embed, audit tool |
| Multiple app processes | Port check/single-server launcher behavior |
| Unsafe deletion | Installer/uninstaller validate exact Local AppData target names |

## Backup policy

- Automatic pre-import and post-import snapshots.
- Automatic manual-edit snapshot.
- Automatic pre-restore snapshot.
- Snapshot filenames include timestamp/reason.
- `backup_log` records path, reason, status, integrity result, and errors.
- Retention code defaults to preview/no deletion; deletion requires explicit enablement by a caller.
- System Health warns when the newest backup is old even if its integrity is valid.

## Recovery procedure

1. Stop workbook imports and avoid simultaneous edits.
2. Open Import Center → Backup Vault.
3. Select the correct timestamp/reason/size/integrity row.
4. Click Restore and confirm.
5. Run DB Connectivity, DB Integrity, Vector Index, and Semantic Search diagnostics.
6. If the index no longer matches the restored student population, use **Re-embed All**.
7. Preserve the automatically created pre-restore snapshot until the recovered state is accepted.

## Automated verification

The repository currently passes 346 pytest tests. Coverage includes:

- application settings, folder creation, startup, and structure;
- SQLite models, pragmas, migrations, and schema registry;
- workbook reading, duplicate checks, normalization, merge/history/missing behavior;
- analytics, dashboard intelligence, faculty mapping, topic grouping;
- filter validation, SQL composition, sorting, pagination, presets, audit logs;
- semantic documents/hashes, embeddings, vector operations, evidence explanations, index synchronization;
- preferred-work and technical-skill semantic edge cases;
- exports and metadata sheets;
- FastAPI pages/endpoints, student profiles, Import Folder, backups, diagnostics, and UI assets;
- release installer verification.

Run the suite:

```powershell
cd wsp_offline_app
.\.venv\Scripts\python.exe -m pytest -q
```

## Diagnostics and audits

### Live diagnostics

Use System Health for DB Connectivity, DB Integrity, Embedding Model, Semantic Search, Import Folder, Export Folder, Backup Vault, and Vector Index.

### Semantic-index audit

```powershell
.\.venv\Scripts\python.exe scripts\audit_semantic_index.py
```

The audit compares active/current IDs, stored profile hashes, vector metadata, and current original text. It writes a report and does not modify student data.

### Search/grouping testbenches

- `run_search_testbench.py` — query/result quality and timing.
- `run_bias_testbench.py` — ranking/coverage bias checks.
- `run_preferred_work_edge_case_audit.py` — flexible/noisy/emerging work-preference cases.
- `run_testbench.py` — combined audit harness.
- `create_testbench.py` / `create_test_workbooks.py` — repeatable synthetic inputs.

Every script has a dedicated entry in [CODE_REFERENCE.md](CODE_REFERENCE.md).

## Release process

1. Update `version.txt` and `pyproject.toml`.
2. Run all tests.
3. Run `BUILD_RELEASE.bat` or `scripts/build_release.ps1`.
4. Verify internal manifest and external ZIP checksum.
5. Push `main` and tag `v<version>`.
6. GitHub Actions rebuilds the package, uploads a workflow artifact, and attaches the ZIP/checksum to the versioned Release.
7. Download the published ZIP and verify its released `.sha256` before distribution.

## Known operational expectations

- First install is intentionally slower because the scientific stack and approximately 669 MB model are installed.
- CPU-only semantic search is optimized for an 8 GB no-GPU laptop but large forced re-embedding jobs take time.
- A Backup Vault warning may mean “latest backup is old,” not “backup is corrupt.” Read the detail.
- The local port is fixed at 8080 for the desktop launcher.
- The system is designed for Windows 10/11; the one-click installer is not cross-platform.
