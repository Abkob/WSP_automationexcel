# Data model and API reference

[Documentation home](README.md) · [Architecture](ARCHITECTURE.md) · [Complete code reference](CODE_REFERENCE.md)

## SQLite tables

| Table | Purpose | Key relationships |
|---|---|---|
| `students_current` | Latest usable record for every known student, including missing flag and extra columns | Links first/latest seen batches; ID feeds profiles, exports, and embeddings |
| `students_history` | Immutable/import-scoped snapshots and change types | Links to `import_batches` by batch ID |
| `import_batches` | Source filename/path/hash, row/column counts, changes, status, errors | Parent of history and import-log rows |
| `column_registry` | Normalized/original header, inferred type, first/latest seen, active/new state | References import batches |
| `file_import_log` | Import events, rejected rows, warnings, messages, details | References batch and optionally student ID |
| `filter_presets` | Server-side named filter JSON support | Optional parent of filter runs |
| `filter_runs` | Audit of applied filter payload and result count | Parent of export log |
| `export_log` | Export path, row count, timestamp | References filter run |
| `semantic_embeddings` | Student/profile hash, vector ID, model/store, update time | References current student ID |
| `backup_log` | Backup path, reason, status, integrity/error, timestamp | Standalone operational audit |

Full field definitions: [database/models.py](code_reference/database/models.py.md).

## Core student fields

| Group | Fields |
|---|---|
| Identity/contact | `STUD_ID`, `STUD_NAME`, `STUD_EMAIL`, `MOBILE_NBR` |
| Academic | `MAJR_DESC`, `CLAS_DESC`, `CUM_GPA`, `TOTAL_CREDIT_HOURS`, `ENRL_TERM`, `STST_DESC`, `STYP_CODE`, `STYP_DESC`, `LEVL_CODE`, `COLL_CODE`, `ENROLLED_IND`, `REGISTERED_IND` |
| Standing | `DEANS_WARNING`, `DEAN_WARN`, `PROBATION`, `ASTD_TERM`, `ATSD_CODE_END_OF_TERM`, `ASTD_DESC`, `ASTD_DATE_END_OF_TERM` |
| Skills/languages | `WSP_WRITTEN_LANGUAGES`, `WSP_SPOKEN_LANGUAGES`, `WSP_ORGANIZATIONAL_SKILLS`, `WSP_TECHNICAL_SKILLS`, `WSP_INTERPERSONAL_SKILLS`, `WSP_ADDITIONAL_SKILLS` |
| Work study | `WSP_PREV_WORK`, `WSP_PREVIOUS_TYPE_OF_WORK`, `WSP_PREFERRED_TYPE_OF_WORK`, `APPLICATION_DATE` |
| Programs/support | `USAID`, `MASTER_CARD`, `UPP_MEPI`, `GAS`, `FINANCIAL_AID`, `DORMS` |
| Audit/runtime | row hash, first/latest batch, missing flag, added/modified timestamps, extra columns JSON |

## HTTP endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Dashboard shell |
| GET | `/filters` | Search & Match shell |
| GET | `/excel-sheets` | Data Explorer shell |
| GET | `/student-profile` | Profile directory shell |
| GET | `/student-profile/{id}` | Profile shell with requested student ID |
| GET | `/import` | Import Center shell |
| GET | `/system-status` | System Health shell |
| POST | `/api/shutdown` | Graceful local process shutdown requested by the UI |
| POST | `/api/admin/reindex` | Start incremental or forced semantic reindex |
| GET | `/api/admin/index-status` | Return index/active counts, coverage, freshness, and running state |
| GET | `/api/dashboard` | Return filtered dashboard intelligence payload |
| GET | `/api/filter-options` | Return distinct major/class options |
| GET | `/api/students/lookup` | Search student directory suggestions |
| GET | `/api/students/{id}/profile` | Return complete holistic profile payload |
| POST | `/api/search` | Execute validated database and optional semantic filters |
| POST | `/api/export` | Export all matching results to Excel |
| GET | `/api/excel-sheets` | Return worksheet-style database views |
| PATCH | `/api/students/update` | Apply allowed manual edits after automatic backup |
| GET | `/api/backups` | List database snapshots and archived workbooks |
| POST | `/api/backup/restore` | Restore a selected local database backup |
| GET | `/api/import-center` | Return import paths, schema, pipeline, and logs |
| POST | `/api/import/run` | Import a specific workbook path |
| POST | `/api/import/refresh-folder` | Scan/consume Import Folder now |
| POST | `/api/import-folder` | Save configured Import Folder |
| GET | `/api/system-status` | Return overview/system information |
| POST | `/api/system-status/diagnostics` | Run selected/all diagnostics |
| POST | `/api/system-status/diagnostics/single` | Run one diagnostic |
| GET | `/api/system-status/diagnostics/checks` | List diagnostic keys/labels |

Endpoint implementation: [app/web_app.py](code_reference/app/web_app.py.md).

## Filter payload

The browser can send global query, semantic query/threshold/top K, name, skills, GPA range, arrays of majors/classes, probation/aid/dorm state, sort field/direction, page size, selected columns, and missing-student inclusion. [filter_service.py](code_reference/services/filter_service.py.md) validates every field/operator before SQL composition.

## Dashboard faculty map

| Code | Faculty/school | Reviewed current majors |
|---|---|---|
| FAS | Faculty of Arts and Sciences | Psychology, Political Science, Computer Science, Chemistry, Biology, English Literature |
| OSB | Suliman S. Olayan School of Business | Business Administration, Accounting, Finance, Marketing |
| MSFEA | Maroun Semaan Faculty of Engineering and Architecture | Architecture, Electrical Engineering, Graphic Design |
| FHS | Faculty of Health Sciences | Public Health |
| HSON | Rafic Hariri School of Nursing | Nursing |
| FAFS | Faculty of Agricultural and Food Sciences | No current dataset majors |
| FM | Faculty of Medicine | No current dataset majors |
| UNMAPPED | Explicit safe fallback | Any unreviewed future major |

## Filesystem state

| Location | Contents |
|---|---|
| `data/wsp.db` | Live SQLite database |
| `data/backups` | Verified database snapshots |
| `data/semantic_index` | FAISS/vector metadata files |
| `data/logs` | Application operational logs |
| `data/install.log` | Installer transcript |
| `data/launcher.log` | Desktop launcher/tray log |
| `.models` | Offline Hugging Face model cache |
| Import Folder | Current source workbook and `archive` |
| Export Folder | Filtered Excel output workbooks |
