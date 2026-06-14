# WSP Offline App Master Checklist

Last updated: 2026-06-07

This file is the editable source of truth for the project. We will work task by task, update this checklist after each completed subtask, and only move forward after the related tests pass.

## Working Rules

- [x] Create the project directory.
- [x] Create this editable Markdown checklist.
- [ ] Keep all implementation tasks small enough to test.
- [ ] Add or update unit tests for every service, parser, database rule, and export behavior.
- [ ] Add integration tests when a feature crosses modules, such as Excel import into SQLite.
- [ ] Run the relevant tests before marking any task complete.
- [ ] Update this file after every completed task, failed test, blocked task, or design decision.
- [ ] Never delete student records during import. Mark missing students instead.
- [ ] Archive original Excel files before changing the database.
- [ ] Backup the database before and after every import.
- [ ] Keep UI code separate from business logic.

## Status Legend

Use normal Markdown checkboxes:

```text
[ ] Not started
[x] Completed
```

For temporary notes, write them under the task as:

```text
Note:
Blocked:
Test result:
Decision:
```

## Target Stack

- [x] Python for the application language.
- [x] FastAPI for the local web UI runtime.
- [x] Vanilla HTML, CSS, and JavaScript for the browser interface.
- [x] NiceGUI was used for the first UI pass, then replaced because the generated UI was not acceptable.
- [x] SQLite for the offline database.
- [x] SQLAlchemy for database models and queries.
- [x] pandas for Excel import and tabular cleaning.
- [x] openpyxl for Excel export and workbook inspection.
- [x] Plotly for dashboard charts.
- [ ] watchdog for folder watching.
- [x] Ollama for local semantic model hosting.
- [x] Qwen3 8B (`qwen3:8b`) for optional local query rewriting, hard-filter extraction, and result explanations.
- [x] sentence-transformers for true local embedding-based semantic retrieval.
- [x] `intfloat/multilingual-e5-small` as the first configured embedding model.
- [x] FAISS for offline vector storage and cosine-similarity search.
- [x] ChromaDB was evaluated but blocked on this Windows machine by native C++ build requirements for `chroma-hnswlib`.
- [ ] PyInstaller for Windows `.exe` packaging.
- [x] pytest for unit and integration tests.

## Real Workbook Findings

Workbook inspected: `C:\Users\Salam\Documents\WSP\WSP.xlsx`

- [x] Confirm workbook exists.
- [x] Confirm workbook has one sheet named `Sheet1`.
- [x] Confirm workbook has 39 columns.
- [x] Confirm workbook currently has the header row only and 0 student data rows.
- [x] Add workbook schema helper in `services/excel_schema.py`.
- [x] Add real workbook contract test that checks the current 39-column WSP schema.

Initial columns detected:

```text
STUD_ID
STUD_NAME
MAJR_DESC
CLAS_DESC
STUD_EMAIL
WSP_WRITTEN_LANGUAGES
WSP_SPOKEN_LANGUAGES
WSP_ORGANIZATIONAL_SKILLS
WSP_TECHNICAL_SKILLS
WSP_INTERPERSONAL_SKILLS
WSP_ADDITIONAL_SKILLS
WSP_PREV_WORK
WSP_PREVIOUS_TYPE_OF_WORK
WSP_PREFERRED_TYPE_OF_WORK
DEANS_WARNING
ENRL_TERM
DEAN_WARN
MOBILE_NBR
PROBATION
APPLICATION_DATE
CUM_GPA
STST_DESC
STYP_CODE
STYP_DESC
ENROLLED_IND
REGISTERED_IND
LEVL_CODE
COLL_CODE
TOTAL_CREDIT_HOURS
ASTD_TERM
ATSD_CODE_END_OF_TERM
ASTD_DESC
ASTD_DATE_END_OF_TERM
USAID
MASTER_CARD
UPP_MEPI
GAS
FINANCIAL_AID
DORMS
```

## Target Project Structure

- [ ] Create this structure during project bootstrap:

```text
wsp_offline_app/
  TASK_CHECKLIST.md
  README.md
  requirements.txt
  pyproject.toml
  main.py
  config.py
  app/
    layout.py
    theme.py
    routes.py
    pages/
      dashboard_page.py
      filter_page.py
      import_page.py
      student_profile_page.py
      history_page.py
      settings_page.py
    components/
      sidebar.py
      metric_card.py
      chart_card.py
      student_table.py
      filter_panel.py
      import_status_card.py
      student_profile_dialog.py
  database/
    db.py
    models.py
    schema_manager.py
    queries.py
    migrations.py
  services/
    excel_importer.py
    folder_watcher.py
    archive_service.py
    backup_service.py
    export_service.py
    filter_service.py
    analytics_service.py
    semantic_service.py
    logging_service.py
  data/
    incoming_excel/
    archive/
      original_excels/
    backups/
    exports/
    logs/
    semantic_index/
  tests/
    fixtures/
    test_config.py
    test_database.py
    test_schema_manager.py
    test_excel_importer.py
    test_archive_service.py
    test_backup_service.py
    test_filter_service.py
    test_export_service.py
    test_analytics_service.py
    test_semantic_service.py
    test_folder_watcher.py
```

## Definition Of Done For Any Subtask

- [ ] The implementation exists.
- [ ] The behavior is covered by tests.
- [ ] Edge cases are tested.
- [ ] The relevant tests pass.
- [ ] The checklist is updated.
- [ ] Any new decision is documented in this file.

## Phase 0: Planning And Setup

### 0.1 Project Directory

- [x] Create `wsp_offline_app/`.
- [x] Confirm the directory exists.

Tests:

- [x] Verify with a shell command that `wsp_offline_app/` exists.

### 0.2 Master Checklist

- [x] Create `TASK_CHECKLIST.md`.
- [x] Verify the checklist can be opened and edited.
- [x] Keep this file as the project control file.

Tests:

- [x] Verify the file exists.
- [x] Verify the file is non-empty.
- [x] Verify the file contains all major project phases.

### 0.3 First Implementation Rule

- [x] Do not start coding the app until Phase 1 is selected.
- [x] When we start Phase 1, create tests at the same time as code.
- [x] Update this checklist after each task.

Tests:

- [x] No automated test needed.
- [x] Manual check that this rule is documented.

## Phase 1: Project Bootstrap

Goal: create a clean Python project that can run tests before real features are added.

### 1.1 Python Environment

- [x] Create `.venv`.
- [x] Confirm Python version.
- [x] Decide supported Python version.
- [x] Install base dependencies.
- [x] Freeze dependencies into `requirements.lock.txt`.

Tests:

- [x] Run `python --version`.
- [x] Run `python -m pip --version`.
- [x] Run `python -m pytest --version` after installing pytest.

Test result:

```text
Python 3.12.13
pip 26.1.2
pytest 9.0.3
```

### 1.2 Packaging Files

- [x] Create `pyproject.toml`.
- [x] Add pytest configuration.
- [x] Add project metadata.
- [x] Decide optional formatting/lint settings are not needed yet.

Tests:

- [x] Test that `pyproject.toml` parses.
- [x] Run `pytest --collect-only`.

Test result:

```text
21 tests collected.
```

### 1.3 Initial App Files

- [x] Create `main.py`.
- [x] Create `config.py`.
- [x] Create `README.md`.
- [x] Add minimal app startup function.
- [x] Keep startup free of import-time side effects.

Tests:

- [x] Test `main.py` imports successfully.
- [x] Test `config.py` imports successfully.
- [x] Test app startup function can be called in dry-run mode if implemented.

### 1.4 Initial Folders

- [x] Create `app/`.
- [x] Create `database/`.
- [x] Create `services/`.
- [x] Create `tests/`.
- [x] Create `tests/fixtures/`.
- [x] Create `data/` folder tree.

Tests:

- [x] Test required folders exist.
- [x] Test data folders can be created idempotently.

## Phase 2: Configuration And Paths

Goal: centralize all paths and settings so the app is portable and packageable.

### 2.1 App Settings Model

- [x] Define app name.
- [x] Define database path.
- [x] Define incoming Excel folder path.
- [x] Define archive folder path.
- [x] Define backup folder path.
- [x] Define export folder path.
- [x] Define logs folder path.
- [x] Define semantic index folder path.

Tests:

- [x] Test default settings resolve inside the project.
- [x] Test settings can be overridden.
- [x] Test invalid paths raise clear errors where appropriate.

### 2.2 Data Directory Creation

- [x] Create a function that ensures all data directories exist.
- [x] Make the function safe to run multiple times.
- [x] Log created folders.

Tests:

- [x] Test directories are created in a temporary folder.
- [x] Test running the function twice does not fail.
- [x] Test missing parent folder is handled.

### 2.3 Runtime Mode

- [x] Add browser mode option.
- [x] Add native desktop mode option.
- [x] Add development mode option.
- [x] Add testing mode option.

Tests:

- [x] Test default mode is development or local.
- [x] Test testing mode uses temporary paths.
- [x] Test native mode flag is read without starting the UI.

## Phase 3: Database Foundation

Goal: create a durable offline SQLite database with current rows, history rows, imports, logs, backups, and exports.

### 3.1 SQLite Connection

- [x] Create SQLAlchemy engine factory.
- [x] Create session factory.
- [x] Enable foreign keys.
- [x] Decide whether to enable WAL mode.
- [x] Set busy timeout.
- [x] Add health check query.

Tests:

- [x] Test engine creates a SQLite database.
- [x] Test session can insert and query a record.
- [x] Test foreign keys are enabled.
- [x] Test health check returns success.

Decision:

```text
Use SQLite WAL mode for file databases and set busy_timeout to 5000 ms by default.
```

### 3.2 Core Tables

- [x] Create `students_current`.
- [x] Create `students_history`.
- [x] Create `import_batches`.
- [x] Create `column_registry`.
- [x] Create `file_import_log`.
- [x] Create `filter_presets`.
- [x] Create `filter_runs`.
- [x] Create `export_log`.
- [x] Create `semantic_embeddings`.
- [x] Create `backup_log`.

Tests:

- [x] Test all tables are created.
- [x] Test expected columns exist.
- [x] Test required indexes exist.
- [x] Test required unique constraints exist.

### 3.3 `students_current`

- [x] Add internal primary key.
- [x] Add `STUD_ID` unique key.
- [x] Add known student columns.
- [x] Add `extra_columns_json` for new Excel columns.
- [x] Add `row_hash`.
- [x] Add `first_seen_batch_id`.
- [x] Add `last_seen_batch_id`.
- [x] Add `created_at`.
- [x] Add `updated_at`.
- [x] Add `missing_from_latest_import`.

Tests:

- [x] Test a student can be inserted.
- [x] Test duplicate `STUD_ID` is rejected or upserted by service only.
- [x] Test extra columns JSON round-trips.
- [x] Test missing flag defaults correctly.

### 3.4 `students_history`

- [x] Add history primary key.
- [x] Add `STUD_ID`.
- [x] Add `batch_id`.
- [x] Add snapshot JSON for the full old row.
- [x] Add `row_hash`.
- [x] Add `valid_from`.
- [x] Add `valid_to`.
- [x] Add `change_type`.
- [x] Add `created_at`.

Tests:

- [x] Test history row can be inserted.
- [x] Test history links to import batch.
- [x] Test old row snapshot is preserved.
- [ ] Test valid change types are enforced by service or constraint.

### 3.5 Import And Log Tables

- [x] Add import batch status fields.
- [x] Add file hash.
- [x] Add archived file path.
- [x] Add row counts.
- [x] Add new column counts.
- [x] Add missing column counts.
- [x] Add error message.
- [x] Add import event log rows.

Tests:

- [x] Test import batch can be created.
- [x] Test import batch status updates.
- [x] Test duplicate file hash can be detected.
- [x] Test event log links to batch.

### 3.6 Schema Manager

- [x] Track every detected Excel column.
- [x] Track first seen batch.
- [x] Track last seen batch.
- [x] Track active/inactive columns.
- [x] Track inferred type.
- [x] Store notes for manual review.

Tests:

- [x] Test new columns are registered.
- [x] Test repeated columns update `last_seen_batch_id`.
- [x] Test missing columns are marked inactive when appropriate.
- [x] Test inferred types are stable for common cases.

## Phase 4: Excel Import Pipeline

Goal: import Excel safely, detect changes, preserve history, and never lose data.

### 4.1 File Intake

- [x] Accept manual file path.
- [x] Reject missing files.
- [x] Reject unsupported file extensions.
- [x] Ignore Excel temporary files starting with `~$`.
- [x] Wait for file size to stabilize.

Tests:

- [x] Test valid `.xlsx` is accepted.
- [x] Test missing file raises clear error.
- [x] Test `.txt` file is rejected.
- [x] Test `~$file.xlsx` is ignored.
- [x] Test unstable file waits or errors predictably.

### 4.2 File Hashing And Duplicate Detection

- [x] Calculate file hash.
- [x] Check previous imports for same hash.
- [x] Skip exact duplicates.
- [x] Log duplicate skip.

Tests:

- [x] Test same file produces same hash.
- [x] Test changed file produces different hash.
- [x] Test duplicate import is skipped.
- [x] Test duplicate skip does not modify students.

### 4.3 Archive Before Import

- [x] Copy original Excel to archive folder.
- [x] Add timestamp to archived filename.
- [x] Include file hash in archive metadata or name.
- [x] Store archived path in import batch.

Tests:

- [x] Test archived file exists.
- [x] Test archived file content hash matches original.
- [x] Test archive path is recorded.
- [x] Test archive failure prevents database mutation.

### 4.4 Read Excel

- [x] Read workbook with pandas.
- [x] Select first sheet by default.
- [x] Allow future support for sheet selection.
- [x] Read headers.
- [x] Read rows.
- [x] Preserve empty cells as nulls.

Tests:

- [x] Test fixture workbook loads.
- [x] Test headers are detected.
- [x] Test empty cells become null/empty consistently.
- [x] Test multiple sheets are handled by first sheet default.

### 4.5 Header Cleaning

- [x] Trim whitespace.
- [x] Convert headers to stable database-safe names.
- [x] Preserve original header names in metadata.
- [x] Detect duplicate headers after cleaning.
- [x] Reject or disambiguate duplicate headers.

Tests:

- [x] Test spaces are trimmed.
- [x] Test mixed casing is normalized.
- [x] Test duplicate cleaned headers are detected.
- [x] Test original header names are preserved.

### 4.6 Schema Comparison

- [x] Compare imported headers with `column_registry`.
- [x] Detect new columns.
- [x] Detect missing columns.
- [x] Detect type changes.
- [x] Update schema registry.
- [x] Show changes in import summary.

Tests:

- [x] Test new column detection.
- [x] Test missing column detection.
- [x] Test type change detection.
- [x] Test schema updates happen in the same transaction as import.

### 4.7 Value Normalization

- [x] Normalize booleans such as `Y`, `N`, `Yes`, `No`, `TRUE`, `FALSE`, `1`, `0`.
- [x] Normalize GPA to decimal.
- [x] Normalize credit hours to number.
- [x] Normalize dates.
- [x] Normalize emails.
- [x] Normalize phone numbers as text.
- [x] Normalize empty strings.
- [x] Normalize text whitespace.

Tests:

- [x] Test every supported boolean input.
- [x] Test invalid boolean input is logged.
- [x] Test GPA numeric conversion.
- [x] Test invalid GPA is handled.
- [x] Test date conversion.
- [x] Test empty values become null consistently.
- [x] Test text whitespace cleanup.

### 4.8 Row Identity

- [x] Require `STUD_ID`.
- [x] Trim and normalize `STUD_ID`.
- [x] Reject rows without usable `STUD_ID`.
- [x] Log rejected rows.

Tests:

- [x] Test valid `STUD_ID` passes.
- [x] Test missing `STUD_ID` is rejected.
- [x] Test whitespace around `STUD_ID` is removed.
- [x] Test rejected row appears in import log.

### 4.9 Row Hashing

- [x] Generate stable hash for normalized row data.
- [x] Exclude volatile fields from hash.
- [x] Include extra columns in hash.

Tests:

- [x] Test same row produces same hash.
- [x] Test changed GPA changes hash.
- [x] Test changed extra column changes hash.
- [x] Test changed column order does not change hash.

### 4.10 Upsert Logic

- [x] Insert new student when `STUD_ID` does not exist.
- [x] Detect unchanged student when hash matches.
- [x] Detect updated student when hash differs.
- [x] Before update, copy old current row to history.
- [x] Update current row.
- [x] Set first and last seen batch IDs.
- [x] Clear missing flag for restored students.

Tests:

- [x] Test new student insert.
- [x] Test unchanged student does not create unnecessary history.
- [x] Test changed student updates current row.
- [x] Test changed student creates history row.
- [x] Test restored missing student is unmarked.

### 4.11 Missing Student Detection

- [x] Compare current database students to latest Excel `STUD_ID` list.
- [x] Mark absent students as `missing_from_latest_import`.
- [x] Do not delete absent students.
- [x] Add history event for newly missing students.
- [x] Do not repeatedly add missing history if already missing.

Tests:

- [x] Test absent student is marked missing.
- [x] Test missing student is not deleted.
- [x] Test newly missing student gets history event.
- [x] Test already missing student does not duplicate history event.

### 4.12 Transaction Safety

- [x] Wrap import in a database transaction.
- [x] Roll back if import fails after starting.
- [x] Keep archive and backup logs clear after failure.
- [x] Record failed import status.

Tests:

- [x] Test simulated failure rolls back student changes.
- [x] Test failed batch is recorded.
- [x] Test no partial current rows remain.
- [x] Test archive remains available for debugging.

## Phase 5: Backup And Archive System

Goal: make the system robust against bad imports, user mistakes, and database corruption.

### 5.1 Backup Creation

- [x] Create pre-import database backup.
- [x] Create post-import database backup.
- [x] Use SQLite-safe backup method.
- [x] Store backup timestamp.
- [x] Store backup reason.
- [x] Store backup file path.

Tests:

- [x] Test backup file is created.
- [x] Test backup can be opened as SQLite.
- [x] Test backup contains expected tables.
- [x] Test backup log row is created.

### 5.2 Backup Integrity

- [x] Verify backup after creation.
- [x] Run SQLite integrity check on backup.
- [x] Fail loudly if backup is invalid.

Tests:

- [x] Test valid backup passes integrity check.
- [x] Test invalid backup fails integrity check.
- [x] Test import does not continue if required pre-import backup fails.

### 5.3 Restore Support

- [x] List available backups.
- [x] Restore selected backup only after confirmation.
- [x] Backup current database before restore.
- [x] Log restore event.

Tests:

- [x] Test backup list returns sorted backups.
- [x] Test restore replaces database safely in test temp folder.
- [x] Test pre-restore backup is created.
- [x] Test restore event is logged.

### 5.4 Retention Policy

- [x] Keep all backups during development.
- [x] Add optional retention setting later.
- [x] Never auto-delete original Excel archives without explicit setting.

Tests:

- [x] Test retention function is disabled by default.
- [x] Test retention preview lists files without deleting them.

## Phase 6: Filtering System

Goal: create a reliable filter engine independent from the UI.

### 6.1 Filter Data Model

- [x] Define filter request structure.
- [x] Define numeric filter structure.
- [x] Define boolean filter structure.
- [x] Define category filter structure.
- [x] Define text filter structure.
- [x] Define semantic filter structure.
- [x] Define sorting and pagination structure.

Tests:

- [x] Test valid filter request parses.
- [x] Test invalid field name is rejected.
- [x] Test invalid operator is rejected.
- [x] Test empty filter returns all non-deleted current students.

### 6.2 Numeric Filters

- [x] Support `=`.
- [x] Support `>`.
- [x] Support `>=`.
- [x] Support `<`.
- [x] Support `<=`.
- [x] Support `between`.
- [x] Support `is empty`.
- [x] Support `is not empty`.
- [x] Apply to GPA, credit hours, and term fields.

Tests:

- [x] Test each numeric operator.
- [x] Test boundary values.
- [x] Test null values.
- [x] Test invalid numeric input is rejected.

### 6.3 Boolean Filters

- [x] Support yes.
- [x] Support no.
- [x] Support any.
- [x] Apply to probation.
- [x] Apply to dean warning.
- [x] Apply to financial aid.
- [x] Apply to dorms.
- [x] Apply to registered.
- [x] Apply to enrolled.
- [x] Apply to USAID.
- [x] Apply to MASTER_CARD.
- [x] Apply to UPP_MEPI.
- [x] Apply to GAS.

Tests:

- [x] Test yes filter.
- [x] Test no filter.
- [x] Test any filter.
- [x] Test combinations of boolean filters.

### 6.4 Category Filters

- [x] Support single select.
- [x] Support multi-select.
- [x] Support empty category.
- [x] Apply to major.
- [x] Apply to class.
- [x] Apply to college.
- [x] Apply to status.
- [x] Apply to level.

Tests:

- [x] Test single category filter.
- [x] Test multi-category filter.
- [x] Test category with special characters.
- [x] Test empty category behavior.

### 6.5 Text Filters

- [x] Support contains.
- [x] Support does not contain.
- [x] Support starts with.
- [x] Support ends with.
- [x] Support exact match.
- [x] Support is empty.
- [x] Support is not empty.
- [x] Apply to skills, languages, previous work, preferred work, name, email.

Tests:

- [x] Test case-insensitive contains.
- [x] Test exact match.
- [x] Test empty values.
- [x] Test special characters do not break query.
- [x] Test SQL injection-like text is treated as text.

### 6.6 Combined Filters

- [x] Combine filters with AND by default.
- [x] Add future support for OR groups only if needed.
- [x] Return total count.
- [x] Return paginated rows.
- [x] Return selected columns.
- [x] Return applied filter metadata.

Tests:

- [x] Test numeric plus boolean.
- [x] Test category plus text.
- [x] Test all filter types together.
- [x] Test pagination.
- [x] Test sorting.
- [x] Test selected columns.

### 6.7 Filter Presets

- [x] Save filter preset.
- [x] Load filter preset.
- [x] Rename filter preset.
- [x] Delete filter preset.
- [x] Validate preset before execution.

Tests:

- [x] Test preset save/load round trip.
- [x] Test duplicate preset name handling.
- [x] Test invalid preset cannot run.
- [x] Test deleting preset does not affect students.

### 6.8 Filter Run Logging

- [x] Log filter execution timestamp.
- [x] Log filter JSON.
- [x] Log result count.
- [x] Log export ID if exported.

Tests:

- [x] Test filter run log is created.
- [x] Test result count is stored.
- [x] Test export link is added when export happens.

## Phase 7: Excel Export

Goal: export filtered results safely and traceably.

### 7.1 Export Filtered Results

- [x] Export current filtered rows to `.xlsx`.
- [x] Create `Filtered Results` sheet.
- [x] Include selected columns.
- [x] Include semantic score if present.
- [x] Format headers.
- [x] Freeze header row.

Tests:

- [x] Test export file is created.
- [x] Test exported workbook opens with openpyxl.
- [x] Test row count matches filter result.
- [x] Test selected columns are respected.

### 7.2 Export Metadata

- [x] Create `Filter Metadata` sheet.
- [x] Include filter JSON.
- [x] Include export timestamp.
- [x] Include source import batch IDs.
- [x] Include number of rows.
- [x] Include app version if available.

Tests:

- [x] Test metadata sheet exists.
- [x] Test filter JSON is stored.
- [x] Test timestamp is stored.
- [x] Test source batches are stored.

### 7.3 Export Logging

- [x] Add export log row.
- [x] Store export path.
- [x] Store filter run ID.
- [x] Store row count.

Tests:

- [x] Test export log row is created.
- [x] Test export log path points to existing file.
- [x] Test export log links to filter run.

## Phase 8: Dashboard Analytics

Goal: provide aggregated analytics from all current student data.

### 8.1 Metric Cards

- [x] Total students.
- [x] New students in latest import.
- [x] Updated students in latest import.
- [x] Average GPA.
- [x] Students on probation.
- [x] Students with dean warning.
- [x] Students with financial aid.
- [x] Students in dorms.
- [x] Registered students.
- [x] Enrolled students.

Tests:

- [x] Test each metric on empty database.
- [x] Test each metric on fixture database.
- [x] Test missing students can be included or excluded by setting.

### 8.2 Charts

- [x] Students by major.
- [x] Students by class.
- [x] GPA distribution.
- [x] Average GPA by major.
- [x] Probation by major.
- [x] Financial aid distribution.

Tests:

- [x] Test chart data shape.
- [x] Test chart data on empty database.
- [x] Test chart data with null values.
- [x] Test chart data ordering.

Decision:

```text
Keep Phase 8.2 limited to structured or reliably categorical fields.
Move subjective/free-text analytics to Phase 9 after semantic/text normalization.
```

### 8.3 Latest Import Summary

- [x] Show latest import filename.
- [x] Show import time.
- [x] Show rows added.
- [x] Show rows updated.
- [x] Show rows unchanged.
- [x] Show rows missing.
- [x] Show new columns.
- [x] Show errors.

Tests:

- [x] Test latest import summary with no imports.
- [x] Test latest import summary with one import.
- [x] Test latest import summary with failed import.

## Phase 9: Semantic Search

Goal: add offline meaning-based filtering after the normal filter system works.

### 9.1 Semantic Text Builder

- [x] Combine relevant student text fields.
- [x] Include skills.
- [x] Include languages.
- [x] Include previous work.
- [x] Include preferred work.
- [x] Include additional skills.
- [x] Exclude private fields unless needed.
- [x] Handle empty text.
- [x] Keep `STUD_ID` in document metadata without adding it to semantic text by default.
- [x] Include non-private extra Excel columns in deterministic order.
- [x] Preserve raw source text without overwriting Excel values.

Tests:

- [x] Test text builder includes expected fields.
- [x] Test empty fields do not create noisy text.
- [x] Test text builder output is stable.
- [x] Test private fields are excluded by default.
- [x] Test private fields can be included only when explicitly requested.
- [x] Test extra columns are included without mutating raw source values.

Test result:

```text
2026-06-04: tests/test_semantic_service.py: 8 passed in 1.71s.
```

### 9.2 Local Ollama Model

- [x] Choose local model backend.
- [x] Choose `qwen3:8b` as requested local model.
- [x] Detect whether Ollama is installed on this machine.
- [x] Detect whether the local Ollama API is reachable.
- [x] Add setting for Ollama base URL.
- [x] Add setting for Ollama model name.
- [x] Add setting for semantic search enable or disable.
- [x] Add model availability check.
- [x] Add clear command guidance for `ollama run qwen3:8b`.
- [x] Pull/cache `qwen3:8b` locally when Ollama is available.
- [x] Add clear error when model is missing.
- [x] Add mocked Ollama chat wrapper for later semantic scoring.

Tests:

- [x] Unit test Ollama availability check with mocked HTTP client.
- [x] Unit test semantic service with mocked Ollama client.
- [x] Test disabled semantic search does not load model.
- [x] Test missing model error is clear.

Test result:

```text
2026-06-04: tests/test_semantic_service.py tests/test_config.py: 27 passed in 0.55s.
2026-06-04: real Ollama check: `qwen3:8b` available locally, size 5.2 GB, digest starts `500a1f067a9f`.
```

Decision:

```text
Use Ollama qwen3:8b as the local semantic model. Do not require the real model in unit tests because it is a large local download.
```

### 9.3 Semantic Candidate Retrieval

- [x] Start with normal filters and text search as candidate narrowing.
- [x] Add persistent vector index for real embedding search.
- [x] Store semantic artifacts in `data/semantic_index/`.
- [x] Map semantic result IDs to `STUD_ID`.
- [x] Rebuild semantic artifacts only when profile hash or vector record is missing.
- [x] Track semantic document hash so changed students can be detected.
- [x] Update only changed students if possible.
- [x] Skip students with no usable semantic text.
- [x] Exclude missing students by default.
- [x] Allow missing students only when requested.

Tests:

- [x] Test candidates can be selected from current students.
- [x] Test semantic artifact directory can be created.
- [x] Test semantic ID to student mapping.
- [x] Test changed student updates semantic artifact mapping.
- [x] Test blank semantic text is skipped.
- [x] Test missing students are excluded by default and included by setting.

Test result:

```text
2026-06-04: tests/test_semantic_service.py after Phase 9.3 candidate retrieval: 23 passed in 0.78s.
```

### 9.3b True Embedding Semantic Retrieval

- [x] Create `semantic_document_service.py`.
- [x] Build one rich work-study profile document per student.
- [x] Include major, class, GPA, eligibility, skills, work preferences, previous work, and languages.
- [x] Exclude `STUD_EMAIL`, `MOBILE_NBR`, names, phone-like, and contact-like fields from embedded text by default.
- [x] Store a stable semantic document hash.
- [x] Create `embedding_service.py`.
- [x] Use `intfloat/multilingual-e5-small` as the default embedding model.
- [x] Add E5 `query:` and `passage:` prompt prefixes for consistent embedding behavior.
- [x] Normalize embedding vectors before storage/search.
- [x] Create `vector_store_service.py`.
- [x] Persist vectors under `data/semantic_index/`.
- [x] Use FAISS `IndexFlatIP` for normalized cosine-similarity search.
- [x] Persist metadata and vectors so the app can restart without losing the index.
- [x] Support candidate-limited vector search after SQLite hard filters.
- [x] Create `semantic_search_service.py`.
- [x] Sync changed student profiles into vector storage.
- [x] Skip re-embedding unchanged profiles.
- [x] Keep SQLite as the source of truth for student rows and semantic metadata.
- [x] Keep the previous keyword/synonym scorer only as text-match fallback.
- [x] Rename UI intent from generic semantic ranker to embedding semantic search.
- [x] Return semantic score and explanation.
- [x] Export semantic score and explanation.
- [x] Add `chat_orchestrator.py` for optional Qwen query rewriting and hard-filter extraction.
- [x] Add `explanation_service.py` for local explanation fallback when Qwen is unavailable.

Tests:

- [x] Test profile generation.
- [x] Test private field exclusion.
- [x] Test semantic hash stability.
- [x] Test embedding text prefixes.
- [x] Test embedding normalization.
- [x] Test FAISS vector upsert and query.
- [x] Test vector search candidate filtering.
- [x] Test changed students are re-embedded and unchanged students are skipped.
- [x] Test structured filters run before vector search.
- [x] Test vague query can retrieve a related profile without exact keyword overlap.
- [x] Test embedding/Qwen unavailable fallback.
- [x] Test export includes semantic explanation.

Test result:

```text
2026-06-07: tests/test_semantic_document_service.py tests/test_embedding_service.py tests/test_vector_store_service.py tests/test_semantic_search_service.py and related filter/export/web tests: 127 passed in 16.58s.
2026-06-07: full pytest suite after embedding/vector refactor: 306 passed in 17.41s.
2026-06-07: live `/api/search` query for `spreadsheet reporting with careful data entry` over `Rerun` students returned 5 rows in 0.104 seconds with explicit text-match fallback explanations because `intfloat/multilingual-e5-small` is not fully cached locally yet.
2026-06-07: live `/api/export` returned an Excel file with `semantic_score` and `semantic_explanation` columns.
2026-06-07: switched live search to local Ollama/Qwen RAG by default. Live `/api/search` for `Find students good for social media posters Canva and design communications` returned 4 Qwen-ranked rows in 28.106 seconds with model-written explanations and no online API usage.
2026-06-07: full pytest suite after local Qwen RAG wiring: 310 passed in 18.95s.
```

Decision:

```text
Use FAISS as the local vector store because ChromaDB could not be installed on this Windows runtime without Microsoft C++ build tools. This still implements true offline embedding semantic search.
```

### 9.4 Semantic Query

- [x] Encode user query into a local Qwen ranking prompt.
- [x] Use Ollama JSON mode for semantic ranking responses.
- [x] Search top K candidate students.
- [x] Return semantic score.
- [x] Return matched student IDs.
- [x] Return short semantic match reason.
- [x] Combine semantic result with normal filters.
- [x] Add semantic scores to filter results.
- [x] Include semantic score in Excel export rows when present.

Tests:

- [x] Test semantic search with mocked Qwen/Ollama response.
- [x] Test top K behavior.
- [x] Test semantic scores are sorted.
- [x] Test invalid semantic model JSON fails clearly.
- [x] Test semantic plus GPA filter.
- [x] Test semantic plus boolean filter.
- [x] Test semantic score export behavior.

Test result:

```text
2026-06-04: tests/test_semantic_service.py tests/test_filter_service.py tests/test_export_service.py: 111 passed in 8.24s.
2026-06-04: tests/test_semantic_service.py tests/test_filter_service.py tests/test_export_service.py tests/test_config.py after timeout/JSON-mode tuning: 122 passed in 6.18s.
2026-06-04: real Qwen smoke test ranked two candidates and selected `STUD_ID=1002` with score 0.95.
2026-06-04: Qwen runtime fix added `think: false`, semantic candidate prefiltering, and prompt text compaction after dummy-data semantic smoke initially timed out.
2026-06-04: real Qwen dummy-data smoke test ranked five imported students for `spreadsheet reporting with careful data entry`; top match `STUD_ID=260072` scored 0.80.
```

### 9.5 Text And Semantic Analytics

- [x] Normalize preferred work text before aggregation.
- [x] Build preferred work type distribution from normalized or clustered values.
- [x] Normalize technical skills text before aggregation.
- [x] Build technical skills frequency after splitting, deduping, and cleaning terms.
- [x] Normalize written and spoken languages before aggregation.
- [x] Build languages frequency after splitting, deduping, and cleaning terms.
- [x] Optionally cluster semantically similar labels such as `Excel`, `spreadsheets`, and `data sheets`.
- [x] Keep raw source text available for auditability.
- [x] Exclude missing students by default.
- [x] Include missing students only when requested.

Tests:

- [x] Test preferred work normalization.
- [x] Test technical skills splitting and deduping.
- [x] Test language splitting and deduping.
- [x] Test semantically similar labels can be grouped when semantic mode is enabled.
- [x] Test raw source text is not overwritten by normalized analytics.
- [x] Test missing students are excluded by default and included by setting.

Test result:

```text
2026-06-04: tests/test_analytics_service.py after Phase 9.5 text analytics: 17 passed in 1.53s.
```

## Phase 10: Local Web User Interface

Goal: build a usable local app after services are tested.

### 10.1 Layout

- [x] Create sidebar.
- [x] Create top status bar.
- [x] Create page container.
- [x] Add app title.
- [x] Add database status.
- [x] Add latest import status.
- [x] Add backup status.
- [x] Add explicit UI host and port settings.
- [x] Register base routes for dashboard, filters, import, students, history, and settings.

Tests:

- [x] Smoke test UI app imports.
- [x] Smoke test page functions can be registered.
- [x] Local server smoke check after server runs.

Test result:

```text
2026-06-04: tests/test_ui_layout.py tests/test_main.py tests/test_config.py after Phase 10.1 layout: 17 passed in 0.89s.
2026-06-04: pytest full suite after Phase 10.1 layout: 261 passed in 24.67s.
2026-06-04: NiceGUI server started at http://127.0.0.1:8080.
2026-06-04: HTTP smoke check passed for `/` and `/filters` with status 200 and no NiceGUI server-error page.
Note: in-app Browser tool was not callable in this thread, so the smoke check used local HTTP requests.
```

### 10.2 Dashboard Page

- [x] Add metric cards.
- [x] Add Plotly charts.
- [x] Make bar charts horizontal and easier to read with long labels.
- [x] Add text and semantic analytics charts for preferred work, technical skills, and languages.
- [x] Add chart summaries for accessibility.
- [x] Add latest import table.
- [x] Add refresh action.
- [x] Load dashboard data from the tested analytics service.
- [x] Initialize the database during app startup.

Tests:

- [x] Unit test dashboard data service.
- [x] UI smoke test dashboard route.
- [x] Local server smoke check dashboard route.
- [ ] Manual screenshot check later.

Test result:

```text
2026-06-04: tests/test_dashboard_page.py tests/test_ui_layout.py tests/test_main.py tests/test_analytics_service.py after Phase 10.2 dashboard: 31 passed in 3.05s.
2026-06-04: pytest full suite after Phase 10.2 dashboard: 268 passed in 20.66s.
2026-06-04: NiceGUI server restarted at http://127.0.0.1:8080.
2026-06-04: HTTP smoke check passed for `/` with dashboard, metric cards, latest import content, and no NiceGUI server-error page.
2026-06-04: dashboard readability update added horizontal Plotly bars and text/semantic analytics charts.
Note: in-app Browser tool was not callable in this thread, so the smoke check used local HTTP requests.
```

### 10.3 Filtering Page

- [x] Add numeric filter controls.
- [x] Add boolean filter controls.
- [x] Add category filter controls.
- [x] Add text filter controls.
- [x] Add semantic search box.
- [x] Add apply filters button.
- [x] Add clear filters button.
- [ ] Add save preset button.
- [x] Add results table.
- [x] Add export button.
- [ ] Add student detail preview.
- [x] Add refresh results action.
- [x] Add accessible labels and tooltips for primary actions.
- [x] Add table formatting for GPA, booleans, semantic match score, skills, and preferred work.
- [x] Replace Qwen-dependent semantic ranking with a functional offline semantic ranker.
- [x] Add semantic synonym expansion, phrase matching, field weights, scores, and match reasons.
- [x] Verify real DB semantic query returns ranked results without calling Qwen.

Tests:

- [x] Unit test filter service.
- [x] Unit test filter UI request builders and table formatting.
- [x] Unit test offline semantic ranking behavior.
- [x] UI smoke test filter route.
- [ ] Manual test applying filters.
- [ ] Manual test exporting results.

Test result:

```text
2026-06-04: tests/test_filter_page_components.py tests/test_dashboard_page.py tests/test_excel_schema.py: 29 passed in 1.43s.
2026-06-04: pytest full suite after filter UI/dashboard readability/dummy schema fixes: 277 passed in 23.41s.
2026-06-04: pytest full suite after Qwen `think: false` and semantic prompt compaction: 281 passed in 19.82s.
2026-06-04: HTTP smoke check passed for `/filters` with status 200 and no NiceGUI server-error page.
2026-06-07: direct real DB semantic query `spreadsheet reporting with careful data entry` over rerun students returned 5 ranked results in 0.0242 seconds using the offline ranker.
Note: in-app Browser tool was not callable in this thread, so manual visual click-through remains open.
```

### 10.8 FastAPI UI Migration

- [x] Add FastAPI app factory.
- [x] Add `/`, `/filters`, `/api/dashboard`, `/api/filter-options`, `/api/search`, and `/api/export`.
- [x] Add static CSS and JavaScript assets.
- [x] Switch `main.py` from NiceGUI runtime to Uvicorn/FastAPI runtime.
- [x] Update runtime dependency list to use FastAPI and Uvicorn.
- [x] Verify `/filters` page does not include `_nicegui` assets.
- [x] Verify live search API returns ranked semantic rows.

Tests:

- [x] Unit test FastAPI HTML route.
- [x] Unit test dashboard API.
- [x] Unit test search API.
- [x] Unit test export API.
- [x] Run full suite after migration.

Test result:

```text
2026-06-07: tests/test_semantic_service.py tests/test_filter_service.py tests/test_web_app.py tests/test_main.py: 111 passed in 17.50s.
2026-06-07: pytest full suite after FastAPI UI migration and offline semantic ranker: 289 passed in 20.74s.
2026-06-07: live `/filters` page contains FastAPI static UI assets and does not contain `_nicegui`.
2026-06-07: live `/api/search` returned 5 ranked rerun students for `spreadsheet reporting with careful data entry`.
```

### 10.9 AUB Administration Portal Restyle

- [x] Inspect `aub-student-administration-portal.zip` as the visual reference.
- [x] Replace the dark generic sidebar with the light AUB administration sidebar.
- [x] Add an institutional seal-style SVG mark.
- [x] Add admin workspace navigation labels and status rows.
- [x] Add sticky topbar with offline workspace status and admin account badge.
- [x] Restyle dashboard metric cards, chart cards, and latest import panel.
- [x] Restyle filter builder using the reference semantic query card pattern.
- [x] Add active filter chips.
- [x] Add Qwen threshold slider.
- [x] Add Top-K result control.
- [x] Restyle results table with dense AUB admin table styling.
- [x] Wire dashboard report button to print.
- [x] Keep FastAPI endpoints and local Qwen RAG behavior unchanged.

Tests:

- [x] Unit test FastAPI HTML route includes AUB portal shell.
- [x] Unit test semantic threshold and Top-K payload conversion.
- [x] Run UI-focused tests.
- [x] Run full test suite.
- [x] Live HTTP check `/filters` includes AUB shell and no `_nicegui`.
- [x] Live Qwen RAG `/api/search` still returns model-ranked rows.

Test result:

```text
2026-06-07: tests/test_web_app.py tests/test_semantic_search_service.py tests/test_filter_page_components.py tests/test_ui_layout.py: 25 passed in 3.72s.
2026-06-07: full pytest suite after AUB portal restyle: 310 passed in 16.45s.
2026-06-07: live `/filters` HTML includes `American University of Beirut`, `Offline Qwen RAG search`, `Ask local Qwen`, `Threshold Match`, and `Top-K Results`; `_nicegui` is absent.
2026-06-07: live `/api/search` for `Find students good for social media posters Canva and design communications` returned 4 Qwen-ranked rows; top result `260020` scored `0.92`.
```

### 10.10 Interactive Dashboard Chart Upgrade

- [x] Replace static dashboard bar rows with reusable interactive chart cards.
- [x] Add chart summaries that identify the top category or largest band.
- [x] Add click and keyboard-selectable chart items.
- [x] Add live detail text for selected bars, bins, and donut segments.
- [x] Add ranked bar charts for major, class, probation, and semantic text frequencies.
- [x] Add vertical histogram layout for GPA distribution.
- [x] Add 0.0-to-4.0 score bars for average GPA by major.
- [x] Add donut chart with legend for financial aid distribution.
- [x] Add responsive and focus-visible styling for all chart controls.
- [x] Add static asset regression test for the interactive chart system.

Tests:

- [x] Run JavaScript syntax check with bundled Node.
- [x] Run focused FastAPI/static asset tests.
- [x] Run full test suite.

Test result:

```text
2026-06-07: bundled Node `--check app/static/wsp.js`: passed.
2026-06-07: tests/test_web_app.py after final interactive dashboard chart upgrade: 6 passed in 3.83s.
2026-06-07: full pytest suite after final interactive dashboard chart upgrade: 311 passed in 37.02s.
2026-06-07: live browser dashboard check at `http://127.0.0.1:8080/`: 9 interactive chart cards, 50 selectable chart items, 5 GPA histogram columns, and 1 financial aid donut chart.
```

### 10.11 Dashboard Chart Design-System Cleanup

- [x] Remove loud mixed chart colors that did not match the AUB admin design.
- [x] Use AUB maroon for standard distribution bars, GPA bars, and histogram fills.
- [x] Use institutional gold only for probation/risk-oriented chart bars.
- [x] Use slate as the secondary donut color so Yes/No segments are readable without looking gimmicky.
- [x] Replace flashy chart gradients with restrained solid fills.
- [x] Reduce hover effects so chart cards feel like admin analytics widgets instead of demo tiles.
- [x] Tighten chart geometry with smaller radii, quieter selection states, and lighter tracks.
- [x] Verify live dashboard color values in the browser.

Tests:

- [x] Run JavaScript syntax check with bundled Node.
- [x] Run focused FastAPI/static asset tests.
- [x] Run full test suite.

Test result:

```text
2026-06-07: bundled Node `--check app/static/wsp.js`: passed.
2026-06-07: tests/test_web_app.py after dashboard chart design-system cleanup: 6 passed in 2.91s.
2026-06-07: full pytest suite after dashboard chart design-system cleanup: 311 passed in 26.02s.
2026-06-07: live browser dashboard color check: standard chart fill `rgb(109, 0, 38)`, score fill `rgb(142, 27, 59)`, probation fill `rgb(176, 138, 47)`, donut swatches maroon/slate.
```

### 10.12 FastAPI Admin Workspace Pages

- [x] Inspect `aub-student-administration-portal.zip` components for Import Center, Excel Sheets, and System Diagnostics.
- [x] Convert disabled sidebar buttons into real FastAPI routes.
- [x] Add `/excel-sheets` page.
- [x] Add `/import` page.
- [x] Add `/system-status` page.
- [x] Add `/api/excel-sheets` backend data endpoint.
- [x] Add `/api/import-center` backend data endpoint.
- [x] Add `/api/import/run` backend action for path-based Excel imports.
- [x] Add `/api/system-status` backend data endpoint.
- [x] Render spreadsheet-style views from live database rows, import warnings, schema registry, and major counts.
- [x] Render Import Center pipeline with watched folder, backup folder, archive folder, candidate files, schema table, and importer logs.
- [x] Render Test/System Status with FastAPI route status, SQLite integrity, backup status, Qwen/Ollama runtime status, and test command summary.
- [x] Wire backend import action to intake validation, duplicate hash check, pre-import backup, archive copy, transaction import, missing-student marking, post-import backup, and import logs.
- [x] Normalize boolean, numeric, date, email, phone, and text values before upserting imported rows.
- [x] Keep the implementation in the existing FastAPI/static UI instead of reintroducing NiceGUI.

Tests:

- [x] Add route tests for `/excel-sheets`, `/import`, and `/system-status`.
- [x] Add API tests for `/api/excel-sheets`, `/api/import-center`, and `/api/system-status`.
- [x] Add import-run API test using a real sample `.xlsx` workbook fixture.
- [x] Run Python syntax check.
- [x] Run JavaScript syntax check.
- [x] Run focused web tests.
- [x] Run full test suite.

Test result:

```text
2026-06-07: `python -m py_compile app/web_app.py`: passed.
2026-06-07: bundled Node `--check app/static/wsp.js`: passed.
2026-06-07: tests/test_web_app.py after admin workspace pages: 9 passed in 3.76s.
2026-06-07: full pytest suite after admin workspace pages: 314 passed in 22.43s.
2026-06-07: live HTTP check: `/excel-sheets`, `/import`, `/system-status`, `/api/excel-sheets`, `/api/import-center`, and `/api/system-status` all returned 200.
2026-06-07: live browser check: Excel Sheets rendered 4 sheet tabs and 75 rows; Import Center rendered 3 candidate files, 5 pipeline steps, 16 schema rows, and console logs; System Status rendered 4 status cards, 5 phase rows, and `311 passed`.
```

### 10.13 Upload Folder Refresh And Source Clarity

- [x] Add upload-folder refresh endpoint for `data/incoming_excel`.
- [x] Process upload-folder workbooks oldest-to-newest so the newest workbook becomes the final database state.
- [x] Import new or changed workbook files using the existing protected import pipeline.
- [x] Skip duplicate workbook hashes during folder refresh.
- [x] Report checked, imported, duplicate-skipped, and failed files.
- [x] Add Import Center button for `Refresh Upload Folder`.
- [x] Start automatic upload-folder refresh while Import Center is open.
- [x] Keep selected-workbook import available but label it clearly.
- [x] Add Import Center backup-policy cards explaining pre-import backup, archive copy, transaction rollback, and post-import backup.
- [x] Add source-map cards to Excel Sheets.
- [x] Rename generated worksheet tabs so they no longer look like raw `.xlsx` files.
- [x] Clarify that Filtering reads SQLite `students_current`, not raw Excel workbooks.
- [x] Keep Excel Sheets as read-only database worksheet views.

Recommended Future Subtasks:

- [ ] Add persistent background watcher service so refresh happens even when Import Center is not open.
- [ ] Add a configurable refresh interval setting.
- [ ] Add a visible last-auto-refresh timestamp.
- [ ] Add manual folder picker support for changing the upload folder.
- [ ] Add per-file refresh history table with imported/skipped/failed status.
- [ ] Add a setting to choose whether folder refresh imports all files or only the newest workbook.

Tests:

- [x] Test `/api/import/refresh-folder` imports a new upload-folder workbook.
- [x] Test `/api/import/refresh-folder` skips the same workbook on the second refresh.
- [x] Test Import Center exposes backup policy and auto-refresh metadata.
- [x] Test Excel Sheets exposes source-map metadata.
- [x] Test Filtering page includes SQLite source clarification.
- [x] Run Python syntax check.
- [x] Run JavaScript syntax check.
- [x] Run focused web tests.
- [x] Run full test suite.

Test result:

```text
2026-06-08: `python -m py_compile app/web_app.py`: passed.
2026-06-08: bundled Node `--check app/static/wsp.js`: passed.
2026-06-08: tests/test_web_app.py after upload-folder refresh and source clarity: 10 passed in 14.29s.
2026-06-08: full pytest suite after upload-folder refresh and source clarity: 315 passed in 28.40s.
2026-06-08: live HTTP check: `/filters`, `/excel-sheets`, `/import`, `/api/excel-sheets`, and `/api/import-center` returned 200.
2026-06-08: live browser check: Import Center rendered refresh/selected-workbook controls, 4 backup policy cards, and auto-refresh status `2 checked, 0 imported, 2 duplicate, 0 failed`; Excel Sheets rendered 4 source cards and `Current Students`; Filtering rendered the SQLite `students_current` source note.
```

### 10.14 Empty Workbook Import Guard And Active Data Repair

- [x] Investigate blank dashboard and blank filter results from the live database.
- [x] Confirm `/api/dashboard` returned `0` active students because every row was marked `missing_from_latest_import`.
- [x] Inspect the latest imported workbook `C:\Users\Salam\Documents\WSP\WSP.xlsx`.
- [x] Confirm the workbook had valid headers but zero student data rows.
- [x] Identify the unsafe behavior: a headers-only workbook imported as `0` rows and marked the previous active students missing.
- [x] Add importer guard that rejects headers-only workbooks before missing-student detection runs.
- [x] Add importer guard that rejects workbooks where every row has an unusable or missing `STUD_ID`.
- [x] Preserve the import audit by recording the rejected workbook as a failed import batch.
- [x] Create a pre-repair database backup before fixing the live data.
- [x] Restore only the students incorrectly marked missing by the bad headers-only batch.
- [x] Keep the 3 genuinely missing students from the previous valid rerun marked as missing.
- [x] Mark the bad `WSP.xlsx` batch as failed with a clear error message.
- [x] Create a post-repair database backup after fixing the live data.
- [x] Restart the FastAPI server so the new import guard is active.

Recommended Future Subtasks:

- [ ] Add an Import Center warning badge when the latest batch is failed.
- [ ] Add a dashboard empty-state card that explains when zero rows are caused by all records being missing.
- [ ] Add a one-click restore action for the latest failed import if it changed active/missing flags.
- [ ] Add pre-import preview showing sheet name, row count, column count, and first 5 student IDs before import.
- [ ] Add a strict minimum active-row safety threshold, for example "do not mark more than 90 percent missing without confirmation."
- [ ] Add automated notification in Import Center when `WSP.xlsx` is headers-only.

Tests:

- [x] Test headers-only workbook import returns a clear failure.
- [x] Test headers-only workbook import does not mark existing active students missing.
- [x] Test workbook with rows but no valid `STUD_ID` returns a clear failure.
- [x] Test no-valid-ID workbook import does not mark existing active students missing.
- [x] Run Python syntax check for changed importer files.
- [x] Run focused web tests.
- [x] Run full test suite.
- [x] Verify live dashboard API returns active students and chart data.
- [x] Verify live search API returns active filter rows.
- [x] Verify browser dashboard renders metric and chart cards.
- [x] Verify browser filter page renders result rows.

Test result:

```text
2026-06-08: live diagnosis: latest `WSP.xlsx` import had 0 rows, 39 columns, and incorrectly marked 122 students missing.
2026-06-08: live repair backup before fix: `data/backups/20260608_110423_pre_empty_import_repair_wsp.db`.
2026-06-08: live repair restored 122 students, kept 3 students missing, and marked batch 3 `WSP.xlsx` as failed.
2026-06-08: live repair backup after fix: `data/backups/20260608_110424_post_empty_import_repair_wsp.db`.
2026-06-08: `python -m py_compile app/web_app.py services/excel_importer.py`: passed.
2026-06-08: tests/test_web_app.py after empty workbook guard: 12 passed in 5.48s.
2026-06-08: full pytest suite after empty workbook guard and live repair: 317 passed in 26.05s.
2026-06-08: live HTTP check: dashboard students `122`, major chart groups `12`, filter search total `122`, and `/`, `/filters`, `/import`, `/excel-sheets` returned 200.
2026-06-08: live browser check: dashboard rendered 8 metric cards, 9 chart cards, first metric `122`, and no console errors.
2026-06-08: live browser check: `/filters` rendered `122 results`, 25 first-page rows, first result `260004 Jad Barakat`, and no console errors.
```

### 10.15 Seamless Import Folder And Student Added/Modified Fields

- [x] Create a visible default Import Folder for daily workbook drops.
- [x] Create an `archive` folder inside the Import Folder.
- [x] Add Import Center control for assigning a custom Import Folder path.
- [x] Persist the assigned Import Folder path in local config.
- [x] Add backend endpoint for saving the Import Folder.
- [x] Add server-side background refresher that checks the Import Folder while the app is running.
- [x] Keep browser-side Import Center refresh as an immediate visible check.
- [x] Import root workbook files from the Import Folder oldest-to-newest.
- [x] Treat the newest accepted workbook as the current workbook source.
- [x] Move retired root workbook files into the Import Folder `archive`.
- [x] Leave failed newest files in place so the user can fix or replace them.
- [x] Use the Import Folder archive for folder-consumed workbook archive copies.
- [x] Close Excel workbook file handles after reading so Windows can move retired files.
- [x] Add `added_to_db_at` to `students_current`.
- [x] Add `modified_in_db_at` to `students_current`.
- [x] Add lightweight migration for existing databases.
- [x] Set `added_to_db_at` only when a student is first inserted.
- [x] Set `modified_in_db_at` only when imported student data actually changes.
- [x] Keep `modified_in_db_at` empty for newly inserted or unchanged repeated students.
- [x] Show Added and Modified columns in filter results.
- [x] Show Added and Modified columns in the Excel Sheets Current Students view.
- [x] Include Added and Modified fields in filtered Excel exports.
- [x] Update Import Center text to explain the daily drop-folder workflow.

Recommended Future Subtasks:

- [ ] Add a real folder-picker dialog for choosing the Import Folder instead of pasting a path.
- [ ] Add a failed-files subfolder for rejected workbooks after the user confirms they should be moved.
- [ ] Add a current-workbook lock file or status marker so non-technical users can see which file is active in the folder.
- [ ] Add a notification toast when the background refresher consumes a new workbook.
- [ ] Add a safety threshold that requires confirmation before a new workbook marks a very large number of students missing.
- [ ] Add an Import Folder cleanup policy for very old archived workbooks.

Tests:

- [x] Test Import Folder assignment creates the folder and inner archive.
- [x] Test Import Folder refresh imports new files.
- [x] Test duplicate root workbook refresh is skipped safely.
- [x] Test newest workbook remains in the root folder as current.
- [x] Test older root workbook moves into Import Folder archive.
- [x] Test database migration adds Added and Modified columns.
- [x] Test inserted students get Added and no Modified timestamp.
- [x] Test unchanged repeated students do not get Modified timestamp.
- [x] Test changed duplicate students get Modified timestamp.
- [x] Test filter selected columns can include Added and Modified timestamps.
- [x] Test table row formatting exposes Added and Modified values.
- [x] Run Python syntax checks.
- [x] Run JavaScript syntax check.
- [x] Run focused tests.
- [x] Run full test suite.

Test result:

```text
2026-06-08: `python -m py_compile` for config, DB models/migrations, importer, filter/export services, web app, and student table: passed.
2026-06-08: bundled Node `--check app/static/wsp.js`: passed.
2026-06-08: focused tests after Import Folder and Added/Modified implementation: 149 passed in 37.56s.
2026-06-08: regression test for Windows Excel file-handle closure and Import Folder archiving: 2 passed in 2.18s.
2026-06-08: full pytest suite after Import Folder and Added/Modified implementation: 321 passed in 41.45s.
2026-06-08: live server restart after Import Folder implementation: port 8080 listening with startup complete.
2026-06-08: live API check: Import Folder `C:\Users\Salam\Documents\WSP\Import Folder`, archive folder inside it, dashboard students `122`, search total `122`, and `added_to_db_at` populated for 125 rows.
2026-06-08: live browser check: Import Center showed Save Folder, Check Import Folder, 3 folder summary cards, 4 backup policy cards, and no console errors.
2026-06-08: live browser check: Filtering showed `122 results` plus Added and Modified columns; first visible Added value was `2026-06-04 13:48`.
```

### 10.4 Import Page

- [ ] Add manual Excel upload.
- [ ] Add selected watched folder display.
- [ ] Add start watcher button.
- [ ] Add stop watcher button.
- [ ] Add latest import summary.
- [ ] Add detected columns table.
- [ ] Add error log table.

Tests:

- [ ] Unit test import service.
- [ ] UI smoke test import route.
- [ ] Manual test file upload.

### 10.5 Student Profile Page Or Dialog

- [ ] Show student identity.
- [ ] Show contact fields.
- [ ] Show academic fields.
- [ ] Show aid/program fields.
- [ ] Show skills and work preferences.
- [ ] Show import history.
- [ ] Show field changes over time.

Tests:

- [ ] Unit test student profile query.
- [ ] Test history ordering.
- [ ] UI smoke test profile dialog/page.

### 10.6 History Page

- [ ] Show import batches.
- [ ] Show files imported.
- [ ] Show row counts.
- [ ] Show schema changes.
- [ ] Show backup events.
- [ ] Show archive paths.
- [ ] Show failed imports.

Tests:

- [ ] Unit test history queries.
- [ ] UI smoke test history route.

### 10.7 Settings Page

- [ ] Select watched folder.
- [ ] Select backup folder.
- [ ] Select export folder.
- [ ] Toggle semantic search.
- [ ] Choose default export columns.
- [ ] Choose backup frequency if added.
- [ ] Choose missing student behavior.

Tests:

- [ ] Unit test settings save/load.
- [ ] Unit test invalid path validation.
- [ ] UI smoke test settings route.

## Phase 11: Folder Watcher

Goal: automatically import new or updated Excel files from a folder.

### 11.1 Watcher Service

- [ ] Start watcher.
- [ ] Stop watcher.
- [ ] Monitor configured folder.
- [ ] Detect created files.
- [ ] Detect modified files.
- [ ] Ignore directories.
- [ ] Ignore temporary Excel files.

Tests:

- [ ] Test watcher starts in temp folder.
- [ ] Test watcher stops cleanly.
- [ ] Test temp Excel files are ignored.
- [ ] Test non-Excel files are ignored.

### 11.2 Stable File Detection

- [ ] Wait until file size stops changing.
- [ ] Add timeout.
- [ ] Log timeout.
- [ ] Avoid importing half-saved Excel files.

Tests:

- [ ] Test stable file passes.
- [ ] Test changing file waits.
- [ ] Test timeout is handled.

### 11.3 Import Queue

- [ ] Queue detected files.
- [ ] Process one import at a time.
- [ ] Avoid duplicate queue entries.
- [ ] Show watcher status in UI.

Tests:

- [ ] Test file is queued once.
- [ ] Test two files process in order.
- [ ] Test duplicate events do not duplicate imports.

## Phase 12: Logging And Audit Trail

Goal: make the app explain what happened and when.

### 12.1 Application Logs

- [ ] Create structured logs folder.
- [ ] Log app startup.
- [ ] Log imports.
- [ ] Log exports.
- [ ] Log backups.
- [ ] Log watcher events.
- [ ] Log errors.

Tests:

- [ ] Test log file is created.
- [ ] Test expected log messages appear.
- [ ] Test errors are logged without crashing unrelated services.

### 12.2 Audit Tables

- [ ] Track import actions.
- [ ] Track export actions.
- [ ] Track filter runs.
- [ ] Track backup actions.
- [ ] Track restore actions.
- [ ] Track schema changes.

Tests:

- [ ] Test audit records are created.
- [ ] Test audit records can be queried by date.
- [ ] Test audit records link to relevant batch/export/backup IDs.

## Phase 13: Rigorous Test Fixtures

Goal: make testing realistic using small Excel files that cover real edge cases.

### 13.1 Excel Fixtures

- [x] Create fixture with one student.
- [x] Create fixture with multiple students.
- [ ] Create fixture with updated student.
- [ ] Create fixture with missing student.
- [ ] Create fixture with new columns.
- [ ] Create fixture with missing columns.
- [ ] Create fixture with bad GPA.
- [x] Create fixture with boolean variations.
- [ ] Create fixture with duplicate `STUD_ID`.
- [ ] Create fixture with blank `STUD_ID`.
- [x] Create realistic randomized dummy workbook with humanized semantic fields.
- [x] Validate dummy workbook headers against the 39-column WSP schema.
- [x] Import dummy workbook into the local database through archive, backup, and transaction flow.

Tests:

- [x] Test fixtures load successfully.
- [x] Test fixture meanings are documented.

Test result:

```text
2026-06-04: created `data/incoming_excel/WSP_dummy_semantic_20260604.xlsx` with 120 realistic dummy students and a `Semantic Test Queries` sheet.
2026-06-04: validated dummy workbook schema: 39 expected columns, 120 data rows, no missing/new/duplicate headers.
2026-06-04: imported dummy workbook into `data/wsp.db`: batch 1, 120 new rows, 0 warnings, 0 missing rows.
2026-06-04: created pre-import and post-import backups for the dummy import.
2026-06-07: created `data/incoming_excel/WSP_dummy_semantic_rerun_20260607.xlsx` from the dummy workbook to simulate a second Excel update.
2026-06-07: rerun workbook intentionally removed 3 students, updated 7 students, kept 110 unchanged students, and added 5 new students.
2026-06-07: validated rerun workbook schema: 39 expected columns, 122 data rows, no missing/new/duplicate headers.
2026-06-07: imported rerun workbook into `data/wsp.db`: batch 2, 5 new rows, 7 updated rows, 110 unchanged rows, 3 missing rows, 0 warnings.
2026-06-07: created pre-import and post-import backups for the rerun dummy import.
```

### 13.2 Database Fixtures

- [ ] Create empty database fixture.
- [ ] Create seeded student database fixture.
- [ ] Create seeded import history fixture.
- [ ] Create temporary database path fixture.

Tests:

- [ ] Test database fixture isolation.
- [ ] Test each test gets clean data.
- [ ] Test no test writes to production data folder.

### 13.3 Service Test Coverage

- [ ] Test importer service.
- [ ] Test schema manager.
- [ ] Test archive service.
- [ ] Test backup service.
- [ ] Test filter service.
- [ ] Test export service.
- [ ] Test analytics service.
- [ ] Test semantic service with mocks.
- [ ] Test folder watcher service.

Tests:

- [ ] Run full unit suite.
- [ ] Measure coverage if coverage tool is added.
- [ ] Add regression tests for every bug found.

## Phase 14: Packaging

Goal: turn the app into a local Windows application after core features work.

### 14.1 PyInstaller Setup

- [ ] Create PyInstaller command or spec file.
- [ ] Include NiceGUI assets.
- [ ] Include required data folders.
- [ ] Include semantic model only if enabled.
- [ ] Set app icon if available.

Tests:

- [ ] Build package in test mode.
- [ ] Launch packaged app.
- [ ] Confirm database path is writable.
- [ ] Confirm import/export works in packaged app.

### 14.2 Windows Validation

- [ ] Test app on current Windows machine.
- [ ] Test app from a folder with spaces in path.
- [ ] Test app after restart.
- [ ] Test app without internet.

Tests:

- [ ] Manual packaged-app smoke test.
- [ ] Manual offline mode test.
- [ ] Manual import/export test.

## Phase 15: Final QA And Release Checklist

Goal: verify the app is trustworthy before real use.

### 15.1 Data Safety

- [ ] Confirm no import deletes students.
- [ ] Confirm old rows go to history.
- [ ] Confirm original Excel files are archived.
- [ ] Confirm pre-import backups are created.
- [ ] Confirm post-import backups are created.
- [ ] Confirm restore procedure works.

Tests:

- [ ] Run import safety integration tests.
- [ ] Run backup restore integration tests.
- [ ] Run missing student tests.

### 15.2 Performance

- [ ] Test with small file.
- [ ] Test with medium file.
- [ ] Test with large realistic file if available.
- [ ] Measure import time.
- [ ] Measure filter time.
- [ ] Measure dashboard load time.
- [ ] Measure semantic search time if enabled.

Tests:

- [ ] Add performance smoke tests if useful.
- [ ] Document timing results.

### 15.3 Usability

- [ ] Dashboard is readable.
- [ ] Filtering page is the main work area.
- [ ] Import errors are understandable.
- [ ] Export button is easy to find.
- [ ] Student profile is clear.
- [ ] Settings are understandable.

Tests:

- [ ] Manual UI walkthrough.
- [ ] Manual test with realistic workflow.

### 15.4 Release Notes

- [ ] Write what the app does.
- [ ] Write how to import Excel files.
- [ ] Write how folder watching works.
- [ ] Write how backups work.
- [ ] Write how to restore from backup.
- [ ] Write how to export filtered results.
- [ ] Write known limitations.

Tests:

- [ ] Documentation review.
- [ ] Run through docs using the packaged app.

## Phase 16: Testbench Infrastructure

Goal: generate realistic multi-wave test data and run automated import + search verification against the live server.

### 16.1 Import Testbench

- [x] Create `scripts/create_testbench.py` generating 34 XLSX workbooks in `data/testbench/`.
- [x] Group A — core pipeline waves: baseline, update, restore, missing, duplicate (409), empty (400).
- [x] Group B — ID edge cases: leading zeros, long IDs, duplicates within file.
- [x] Group C — field edge cases: GPA boundary, long text, special chars, missing optional fields.
- [x] Group D — schema variants: extra columns, missing columns, lowercase/mixed-case headers.
- [x] Group E — workbook structure: wrong sheet name, empty file, multi-sheet workbook.
- [x] Group F — filter/search targets: one file per major with targeted skill keywords.
- [x] Group G — cumulative waves G1→G6 building to 3 000 active students.
- [x] Fix `_write_wb` to use `data_keys=COLS` parameter so lowercase-header files still write correct cell values.
- [x] G-series students generated with realistic distributions: ~15 % probation, ~25 % financial aid, ~20 % dorms.
- [x] Create `scripts/run_testbench.py` that auto-imports each file via `POST /api/import/run`.
- [x] Expected-error files assert correct HTTP codes (409 duplicate, 400 empty/wrong-sheet).
- [x] Non-expected 409s on re-runs treated as SKIP, not FAIL.
- [x] End-to-end sanity checks: `/api/search {}` and `/api/export {}` after all imports.

Result: 33/33 pass, 1 skip, 0 failures.

### 16.2 AI Semantic Search Testbench

- [x] Create `scripts/run_search_testbench.py` with 47 queries across 7 categories.
- [x] Category A — domain matching: 10 major-specific queries, accuracy check against expected top major.
- [x] Category B — skill keyword queries: 10 skill-phrase queries.
- [x] Category C — cache consistency: same query run twice, scores must match exactly.
- [x] Category D — threshold edge cases: 0.0, 0.10, 0.30, 0.50, 0.75, 0.95, 1.00.
- [x] Category E — combined filter + semantic: GPA range, probation flag, financial aid, dorms.
- [x] Category F — adversarial inputs: empty, whitespace, SQL injection, Arabic text, emoji, XSS — all must return HTTP 200.
- [x] Category G — concurrent load: 5 parallel searches via threads.
- [x] Record p50, p95, p99, max timing and flag slow queries.
- [x] Restore 3 000-student population automatically if active count < 2 900.
- [x] Poll for background reindex completion instead of fixed sleep.

Final result: **27/27 checks passed**. p50 = 421 ms, p95 = 625 ms.

---

## Phase 17: Semantic Search Performance Optimizations

### 17.1 In-Memory Vector Cache

- [x] Add module-level `_VECTOR_CACHE` dict in `services/vector_store_service.py` keyed by vectors file path.
- [x] Cache entry stores `(matrix, metadata, v_mtime, m_mtime)`; invalidated automatically when either file's mtime changes.
- [x] `_load_cached()` reads from disk only when mtime differs from cached value.
- [x] `_invalidate_cache()` called at start of `replace_all()` and on empty-path early return.
- [x] `query()` uses `_load_cached()` instead of separate `load_metadata()` + `load_vectors()` calls.

Improvement: eliminated 1–2 s disk read per search.

### 17.2 Background Reindex After Import

- [x] Add daemon thread in `app/web_app.py` after every successful import.
- [x] Thread calls `sync_student_semantic_index` on all active students, then `mark_index_fresh()`.
- [x] Import API response returns immediately; index update happens in background.

### 17.3 Index Freshness And Reindex-In-Progress Flags

- [x] Add `_index_fresh`, `_reindex_running`, and `_index_lock` to `services/semantic_search_service.py`.
- [x] `mark_index_stale()` — called at start of every import.
- [x] `mark_reindex_started()` — called in `web_app.py` just before background thread launches.
- [x] `mark_index_fresh()` — called when background thread finishes; also clears `_reindex_running`.
- [x] `rank_student_rows_by_vector_search` skips inline sync when `_is_index_fresh()` OR `_reindex_in_progress()`.
- [x] Prevents double-encoding when background thread and a search request compete for CPU.

### 17.4 Startup Freshness Pre-Warm

- [x] In `_prewarm_embedding_model()`, check if FAISS `vectors_path` exists and `store.count() > 0`.
- [x] If so, call `mark_index_fresh()` on startup.
- [x] Prevents first search after a server restart from triggering a full inline sync of all students.

### 17.5 LRU Query Vector Cache

- [x] Add `_QUERY_VECTOR_CACHE` (`collections.OrderedDict`) in `semantic_search_service.py`, max 64 entries.
- [x] `_get_query_vector(model, query)` — checks cache before calling `model.encode()`.
- [x] Cache keyed by `(model_name, query_text)` so different models don't collide.
- [x] Thread-safe via `_QUERY_VECTOR_CACHE_LOCK`.
- [x] `rank_student_rows_by_vector_search` uses `_get_query_vector` instead of inline `model.encode`.

Improvement: repeat queries return in < 150 ms instead of 400–600 ms.

Performance summary after all optimizations (3 000 students, CPU-only):
- Import response: immediate (background reindex decoupled)
- First search (cold): ~450 ms
- Repeat search (LRU hit): ~80–200 ms
- p50: 421 ms · p95: 625 ms · p99: 1 250 ms

---

## Phase 18: Excel Sheets UI Fixes

### 18.1 Remove 75-Row Limit

- [x] `build_excel_sheets_payload` in `app/web_app.py` had `.limit(75)` on the `StudentCurrent` query.
- [x] Removed limit — Current Students sheet now loads all active students.

### 18.2 Global Search Inline On Sheets

- [x] Previous behavior: global search hid the sheet workspace and showed a separate flat panel.
- [x] New behavior: sheet stays visible; rows are filtered and highlighted directly in the table.
- [x] Tab bar shows match-count badges (`em.sheet-tab-badge` — red pill) per sheet.
- [x] If the active sheet has 0 matches, auto-switch to the first sheet that has results.
- [x] Blue info banner above the table shows matched-row count on current sheet and total across all sheets.
- [x] Clicking a tab while search is active re-filters on the new tab without clearing the query.
- [x] Clearing the search input restores normal sheet view with full tab click handlers.
- [x] Added `renderActiveSheetWithQuery(query)` helper that renders the active sheet filtered by a given query string.
- [x] Added CSS: `.global-results-banner` (blue info bar), `.sheet-tab-badge` (red count pill on tabs).

---

## Phase 19: Dashboard Chart.js Fix

- [x] Dashboard bar/line/histogram charts were not rendering — Chart.js bundle was missing from static assets.
- [x] Downloaded `chart.umd.min.js` (v4.4.4, 201 KB) to `app/static/`.
- [x] HTML references it with `<script src="/static/chart.umd.min.js" defer>` before `wsp.js`.

---

## Current Next Task

- [ ] Continue Phase 10: manual visual/accessibility click-through on the FastAPI UI, then add save presets and student detail preview.

## Decisions Log

### 2026-06-03

- [x] Use NiceGUI instead of Streamlit for a more app-like offline UI.
- [x] Use SQLite as the offline database.
- [x] Use append-only history instead of creating a new table for every import.
- [x] Use soft missing markers instead of deleting students.
- [x] Use this Markdown file as the living checklist.
- [x] Real workbook `WSP.xlsx` currently has 39 headers and 0 student rows.
- [x] Keep heavy semantic dependencies out of the first install; add them during Phase 9.
- [x] Use SQLite WAL mode by default for local file databases.
- [x] Move subjective/free-text dashboard analytics from Phase 8.2 to Phase 9.5.

### 2026-06-04

- [x] Use local Ollama `qwen3:8b` for semantic model behavior instead of making sentence-transformers the first semantic backend.
- [x] Keep semantic unit tests mocked/pure so tests do not require downloading or running a 5.2 GB model.
- [x] Before installation, Ollama was not installed as `Ollama.Ollama` according to `winget list --id Ollama.Ollama -e`.
- [x] Before installation, local Ollama API at `http://localhost:11434/api/tags` was not responding.
- [x] Installed Ollama 0.30.4 with `winget install --id Ollama.Ollama -e --accept-package-agreements --accept-source-agreements --silent`.
- [x] Pulled local model `qwen3:8b` with Ollama; model size reported as 5.2 GB.
- [x] Verified `check_semantic_model_status(AppSettings(semantic_search_enabled=True))` returns `model_available=True`.
- [x] Keep subjective dashboard analytics in the text/semantic dashboard section instead of treating them like rigid structured fields.
- [x] Use randomized humanized dummy student prose to test semantic matching against realistic messy Excel text.
- [x] Send `think: false` to Ollama chat calls for Qwen so JSON responses appear in `message.content` instead of only `message.thinking`.
- [x] Cap and compact semantic candidate prompts before local Qwen ranking to keep offline search responsive.

### 2026-06-07

- [x] Use a changed dummy Excel file for reruns because exact duplicate workbooks are correctly skipped by file hash.
- [x] Keep rerun dummy imports realistic by testing new, updated, unchanged, and missing students in one workbook.
- [x] Further compact Qwen semantic prompts to 4 candidates and 220 characters per candidate after narrowed rerun semantic smoke still timed out.
- [x] Note that local `qwen3:8b` semantic ranking works but can still be slow on CPU-class local runtime.
- [x] Make offline deterministic semantic ranking the default because UI searches must not block on Qwen.
- [x] Keep Qwen support as optional model reranking only, not the default search path.
- [x] Replace NiceGUI runtime with FastAPI plus plain static HTML/CSS/JS.

## Test Command Log

Record test runs here as the project progresses.

```text
2026-06-03:
- Python version check: Python 3.12.13.
- pip version check: pip 26.1.2.
- pytest version check: pytest 9.0.3.
- pyproject parse check: passed.
- pytest --collect-only: 21 tests collected.
- pytest: 21 passed in 0.27s.
- pytest after Phase 3.1 SQLite connection: 28 passed in 1.05s.
- pytest after Phase 3.2 core tables: 39 passed in 1.54s.
- pytest after Phase 3.6 schema manager: 44 passed in 1.63s.
- pytest after Phase 4.1 file intake: 52 passed in 1.57s.
- pytest after Phase 4.2 hashing and duplicate detection: 59 passed in 2.57s.
- pytest after Phase 4.3 archive before import: 66 passed in 2.18s.
- pytest after Phase 4.4 pandas Excel reader: 72 passed in 5.35s.
- pytest after Phase 4.5 header cleaning: 75 passed in 3.16s.
- pytest after Phase 4.6 schema comparison: 76 passed in 3.84s.
- pytest after Phase 4.7 value normalization: 87 passed in 2.71s.
- pytest after Phase 4.8 row identity: 91 passed in 3.49s.
- pytest after Phase 4.9 row hashing: 96 passed in 5.43s.
- pytest after Phase 4.10 upsert logic: 100 passed in 3.61s.
- pytest after Phase 4.11 missing student detection: 103 passed in 5.70s.
- pytest after Phase 4.12 transaction safety: 106 passed in 5.95s.
- pytest after Phase 5.1 backup creation: 114 passed in 5.03s.
- pytest after Phase 5.2 backup integrity: 117 passed in 6.26s.
- pytest after Phase 5.3 restore support: 121 passed in 5.91s.
- pytest after Phase 5.4 retention policy preview: 124 passed in 5.73s.
- pytest after Phase 6.1 filter data model: 135 passed in 8.68s.
- pytest after Phase 6.2 numeric filters: 146 passed in 6.42s.
- pytest after Phase 6.3 boolean filters: 161 passed in 9.07s.
- pytest after Phase 6.4 category filters: 166 passed in 11.37s.
- pytest after Phase 6.5 text filters: 173 passed in 11.31s.
- pytest after Phase 6.6 combined filters: 179 passed in 9.93s.
- pytest after Phase 6.7 filter presets: 186 passed in 9.88s.
- pytest after Phase 6.8 filter run logging: 190 passed in 11.66s.
- pytest after Phase 7.1 export filtered results: 197 passed in 9.89s.
- pytest after Phase 7.2 export metadata: 200 passed in 11.40s.
- pytest after Phase 7.3 export logging: 203 passed in 9.62s.
- pytest after Phase 8.1 metric cards: 206 passed in 9.80s.
- pytest after Phase 8.2 structured charts: 211 passed in 13.99s.
- pytest after Phase 8.3 latest import summary: 214 passed in 14.23s.
2026-06-04:
- pytest tests/test_semantic_service.py after Phase 9.1 semantic text builder: 8 passed in 1.71s.
- pytest tests/test_semantic_service.py tests/test_config.py after Ollama settings/status layer: 27 passed in 0.55s.
- pytest full suite after Phase 9.1 and Ollama status layer: 233 passed in 17.24s.
- pytest tests/test_semantic_service.py after Phase 9.3 candidate retrieval: 23 passed in 0.78s.
- pytest full suite after Phase 9.3 candidate retrieval: 239 passed in 18.60s.
- pytest tests/test_semantic_service.py tests/test_filter_service.py tests/test_export_service.py after Phase 9.4 semantic query: 111 passed in 8.24s.
- pytest tests/test_semantic_service.py tests/test_filter_service.py tests/test_export_service.py tests/test_config.py after Qwen timeout/JSON-mode tuning: 122 passed in 6.18s.
- real Qwen smoke test after Phase 9.4: selected `STUD_ID=1002` with semantic score 0.95 for query `spreadsheet reporting work`.
- pytest full suite after Phase 9.4 semantic query: 249 passed in 30.01s.
- pytest tests/test_analytics_service.py after Phase 9.5 text analytics: 17 passed in 1.53s.
- pytest full suite after Phase 9.5 text analytics: 255 passed in 17.89s.
- pytest tests/test_ui_layout.py tests/test_main.py tests/test_config.py after Phase 10.1 layout: 17 passed in 0.89s.
- pytest full suite after Phase 10.1 layout: 261 passed in 24.67s.
- NiceGUI local server smoke check: `/` and `/filters` returned HTTP 200 with no server-error page at http://127.0.0.1:8080.
- pytest tests/test_dashboard_page.py tests/test_ui_layout.py tests/test_main.py tests/test_analytics_service.py after Phase 10.2 dashboard: 31 passed in 3.05s.
- pytest full suite after Phase 10.2 dashboard: 268 passed in 20.66s.
- NiceGUI dashboard smoke check: `/` returned HTTP 200 with dashboard, metric cards, latest import content, and no server-error page at http://127.0.0.1:8080.
- pytest tests/test_excel_schema.py after workbook dimension fallback: 14 passed in 0.29s.
- dummy workbook validation: `WSP_dummy_semantic_20260604.xlsx` matched all 39 expected WSP headers with 120 data rows.
- dummy workbook import: batch 1 completed with 120 new rows, 0 warnings, 0 missing rows, plus pre/post DB backups.
- pytest tests/test_filter_page_components.py tests/test_dashboard_page.py tests/test_excel_schema.py after filter UI/dashboard updates: 29 passed in 1.43s.
- pytest full suite after filter UI/dashboard readability/dummy schema fixes: 277 passed in 23.41s.
- NiceGUI smoke check after filter UI/dashboard updates: `/filters` and `/` returned HTTP 200 at http://127.0.0.1:8080, with clean server error log.
- pytest tests/test_semantic_service.py after Qwen `think: false`, candidate prefiltering, and prompt compaction: 34 passed in 0.72s.
- real Qwen dummy-data smoke after semantic runtime fix: query `spreadsheet reporting with careful data entry` returned 5 ranked students; top result `260072` score 0.80.
- pytest full suite after semantic runtime fix: 281 passed in 19.82s.
- NiceGUI final smoke check: `/filters` and `/` returned HTTP 200 at http://127.0.0.1:8080, with clean server error log.
2026-06-07:
- generated rerun dummy workbook: `WSP_dummy_semantic_rerun_20260607.xlsx`, 122 rows, 39 columns, 3 removed, 7 updated, 5 added.
- rerun import: batch 2 completed with 5 new rows, 7 updated rows, 110 unchanged rows, 3 missing rows, 0 warnings.
- DB state after rerun import: 125 current records, 122 active records, 3 missing records, 10 history rows.
- pytest full suite after rerun import: 281 passed in 49.58s.
- real Qwen rerun semantic smoke after prompt compaction: query `spreadsheet reporting with careful data entry` over `Rerun` students returned 3 ranked students; top result `260201` score 0.20.
- pytest tests/test_semantic_service.py after tighter prompt compaction: 34 passed in 3.41s.
- pytest full suite after semantic prompt tuning: 281 passed in 19.87s.
- NiceGUI smoke check after rerun import: `/` and `/filters` returned HTTP 200 at http://127.0.0.1:8080, with clean server error log.
- direct real DB offline semantic query after ranker replacement: 5 results in 0.0242 seconds; top result `260201` score 0.761921.
- pytest tests/test_semantic_service.py tests/test_filter_service.py after offline semantic ranker replacement: 105 passed in 5.37s.
- pytest tests/test_semantic_service.py tests/test_filter_service.py tests/test_web_app.py tests/test_main.py after FastAPI UI migration: 111 passed in 17.50s.
- pytest full suite after FastAPI UI migration and offline semantic ranker: 289 passed in 20.74s.
- live FastAPI UI check: `/filters`, `/static/wsp.css`, `/static/wsp.js`, `/api/dashboard`, and `/api/search` returned HTTP 200.
- live `/filters` HTML check: contains `Find students by fit`, includes `/static/wsp.css` and `/static/wsp.js`, and does not contain `_nicegui`.
2026-06-08:
- pytest tests/test_web_app.py after upload-folder refresh and source clarity: 10 passed in 14.29s.
- pytest full suite after upload-folder refresh and source clarity: 315 passed in 28.40s.
- live diagnosis after blank dashboard/filter issue: latest `WSP.xlsx` had 39 headers and 0 student data rows, causing 122 active students to be marked missing.
- live repair: restored 122 students, kept 3 legitimately missing students, marked batch 3 `WSP.xlsx` failed, and wrote pre/post repair backups.
- py_compile app/web_app.py services/excel_importer.py after empty workbook guard: passed.
- pytest tests/test_web_app.py after empty workbook guard: 12 passed in 5.48s.
- pytest full suite after empty workbook guard and live repair: 317 passed in 26.05s.
- live API check after repair: dashboard students `122`, major chart groups `12`, filter search total `122`, and `/`, `/filters`, `/import`, `/excel-sheets` returned HTTP 200.
- live browser check after repair: dashboard rendered 8 metric cards and 9 chart cards; `/filters` rendered `122 results` with 25 first-page rows; browser console had no errors.
- py_compile for Import Folder and Added/Modified implementation: passed.
- bundled Node `--check app/static/wsp.js` after Import Folder UI changes: passed.
- pytest focused suite after Import Folder and Added/Modified implementation: 149 passed in 37.56s.
- pytest regression after Windows Excel file-handle closure fix: 2 passed in 2.18s.
- pytest full suite after Import Folder and Added/Modified implementation: 321 passed in 41.45s.
- live restart after Import Folder implementation: port 8080 listening, Import Folder at `C:\Users\Salam\Documents\WSP\Import Folder`, dashboard/search totals `122`, and filter table showed Added/Modified columns.
```
