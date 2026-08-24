# Complete administrator user manual

[Documentation home](README.md) · [Feature and code flows](FEATURES_AND_CODE_FLOW.md) · [Operations and recovery](OPERATIONS_SECURITY_TESTING.md)

## 1. Install and open WSP

1. Download the latest release ZIP and extract it completely.
2. Double-click **INSTALL WSP - ONE CLICK.bat**.
3. Leave the installer window open while it checks Windows, package integrity, free space, Python, dependencies, the offline model, database, routes, and writable folders.
4. Open **WSP Offline System** from Desktop or Start Menu.
5. Use **WSP Import Folder** to open the daily workbook location.

The first installation requires internet access and may take 10–30 minutes. Later use is local/offline. Opening WSP again while it is running opens another app window instead of starting a second server. Use the system-tray menu to reopen or exit WSP.

## 2. Understand the navigation

| Navigation item | Use it for |
|---|---|
| Dashboard | Understand the candidate pool, skills/preferences, operational support, and data quality. |
| Search & Match | Build precise filters, run local semantic matching, inspect evidence, and export results. |
| Data Explorer | Inspect database-generated worksheet views and perform controlled edits. |
| Student Profiles | Find one student and review their complete holistic record. |
| Import Center | Configure/scan Import Folder, monitor imports/schema/logs, re-embed, auto-export, and restore backups. |
| System Health | Review runtime information and run diagnostics. |

The top banner confirms the offline workspace and port. **Refresh** reloads the active area. The left sidebar stays consistent on every page.

## 3. Dashboard

### Filter the whole dashboard

1. Click **Show filters**.
2. Select one or more faculties, majors, and class/year values.
3. Use the search box inside a multi-select when the list is long.
4. Select Financial Aid context if needed.
5. Remove one active chip or click **Clear filters**.

Faculty selection narrows the available majors. The same selection updates KPIs, charts, faculty comparisons, and candidate rows. Filter state is kept in the local page URL.

### Placement Overview

Use this first to understand candidate volume, optional previous-experience coverage, aid/housing context, top skill areas, preferred work areas, faculty distribution, and representative candidates. Click an actionable KPI or faculty **Add** control to narrow the view. Click any candidate to open their profile.

### Candidate Pool

Use major, class/year, GPA, and faculty charts to understand the applicant mix. Click a chart value to filter the dashboard. A single remaining category becomes a compact spotlight instead of an oversized bar.

### Skills & Preferences

Review the strongest technical-skill topics and preferred-work areas. Labels may be:

- reviewed stable fields;
- **Flexible / Open to Any Role** for explicit open answers;
- **Emerging** when a novel semantic pattern appears across multiple students; or
- **Needs Review / Unverified** for isolated, random, or uncertain text.

Topics summarize the population; the original answer remains unchanged in each profile and search document.

### Funding & Logistics

Use aid and dorm/housing context to coordinate placements and support. Comparisons use percentages where raw counts would unfairly favor larger faculties/classes.

### Data Quality

Start with the weakest completion field, review the issue queue, and open records needing attention. Unmapped future majors remain in an explicit Unmapped group instead of being assigned incorrectly. Inactive records remain available as history and are excluded from active applicant KPIs.

### Print

Use the browser print command when a print control is available. Navigation and interactive controls are hidden by the print stylesheet.

## 4. Search & Match

### Direct/database filters

- **Global search:** searches across the broad student record.
- **Name contains / Skills contain:** targeted text matching.
- **Minimum/Maximum GPA:** numeric range.
- **Major / Class:** multi-select categories.
- **Probation / Aid / Dorms:** Any, Yes, or No.
- **Sort by / Order:** ID, name, GPA, or major; ascending/descending.
- **Include missing students:** adds students absent from the newest valid workbook.

### Local semantic matching

1. Enter a natural-language request in **Ask local AI**.
2. Set **Threshold Match**. Higher values are stricter.
3. Set **Top-K Results**.
4. Click **Apply AI Filter**.
5. Inspect Match and Why columns.

Each explanation cites the closest original student fields and field-level similarities. Dashboard topic names are not substituted into search documents. The progress animation reports stages such as reading filters, searching the local index, ranking, and preparing results; it is not hidden model reasoning.

### Saved preferences

Filter changes are automatically saved in the browser profile on that computer. **Preferences restored** confirms a reload. **Clear saved** removes persistent preferences. **Reset** changes the current form. Import Center Auto Export uses the saved preference set.

### Open a profile

Click the student ID/name, double-click a row, or right-click and choose **View student profile**. The context menu can also copy the student ID.

### Export

Click **Export**. The application exports every match to Export Folder, with:

- **Filtered Results** — matching rows;
- **Filter Metadata** — filters, sort, counts, and source context.

## 5. Data Explorer

### Worksheet views

- **Current Students:** current and retained student records shown from SQLite.
- **Import Issues:** rejected rows and normalization warnings.
- **Column Schema:** registered workbook fields and mappings.
- **Major Analytics:** database-generated major distribution.

Use global search across sheets or the active-sheet search. Click a cell to populate the formula/value preview. Student ID/name links open profiles.

### Controlled editing

1. Click **Edit**.
2. Change supported fields in the visible cells.
3. Review the pending edit count.
4. Click **Save** or **Cancel**.

Saving creates a database backup first, applies allowed fields only, and records modified timestamps. Cancel exits without writing changes. Unsupported/free-form columns remain read-only.

## 6. Student Profiles

### Find a student

Search by student name, ID, AUB email, or major. Press Enter to open the first match. Recent/suggested profiles appear on the empty directory page.

### Profile sections

- Identity header: name, ID, major, class, email, mobile, current/enrollment badges.
- Highlights: GPA, credit hours, academic standing, enrollment/registration.
- Academic record: program, codes, type, level, term, status, GPA, credits.
- Standing & alerts: standing, probation, dean-warning flags.
- Skills & languages: technical, organizational, interpersonal, additional, spoken, and written fields.
- Work-study profile: prior experience, prior work type, preferred work.
- Aid, programs & housing: Financial Aid, USAID, Mastercard, UPP/MEPI, GAS, Dorms.
- Contact & application: email, mobile, application date.
- Additional information: non-standard workbook columns preserved in `extra_columns_json`.
- Record details: current/missing state, added/modified dates, first/latest source workbook.
- Record timeline: added, updated, and missing-from-import history.

Use **Find another student** to return to lookup and **Print profile** for a clean print/PDF view.

## 7. Import Center

### Daily workflow

1. Close the workbook in Excel.
2. Place the newest `.xlsx` or `.xlsm` file in Import Folder (not in `archive`).
3. Wait for the automatic 30-second scan or click **Check Now**.
4. Confirm the accepted filename and pipeline stages.
5. Review schema changes and validation logs.
6. Confirm AI Search Index returns to 100%.

### Change Import Folder

Enter an absolute path and click **Save Folder**. The path is stored locally. The archive path is created inside it; Export Folder is created beside it.

### Import safety behavior

- Only `.xlsx` and `.xlsm` are accepted; temporary `~$` files are ignored.
- The first worksheet is used.
- Row 1 must contain headers and at least one later row must have a usable `STUD_ID`.
- Exact duplicate files are detected by SHA-256 and skipped.
- Headers are normalized; unexpected columns are preserved/registered.
- Invalid/blank values may be normalized with warnings.
- Pre-import backup occurs before database changes.
- Rows merge in one transaction; failure rolls back.
- Changed rows retain history; absent students are marked missing, not deleted.
- Post-import backup occurs after success.
- Older accepted workbook files move into `archive`.

### Pipeline, schema, and log

The pipeline shows workbook acceptance, pre-backup, schema validation, database merge, and post-backup. Detected Columns Schema shows type, status, and first/latest batch. Validation Execution Log shows imports, warnings, rejected rows, duplicates, and failures.

### AI Search Index

Coverage compares active students with indexed IDs. **Re-embed All** force-rebuilds every active vector. Normal startup/import behavior is incremental. Searches may lazily repair missing candidate vectors.

### Auto Export

Auto Export summarizes the saved Search & Match preferences. Click **Export Now** to generate a current workbook without rebuilding the filter form, or **Edit Filters** to change preferences.

## 8. Backup Vault

The vault lists timestamp, reason, size, integrity, and Restore. Reasons include pre-import, post-import, manual edit, and pre-restore.

Before restore, WSP:

1. verifies the selected backup;
2. creates an emergency snapshot of the current database;
3. replaces the database safely;
4. rechecks integrity; and
5. logs the restore.

Restore is a material data change. Confirm the chosen timestamp/reason and ensure no other WSP instance is editing data.

## 9. System Health

The overview shows active/total students, database size/health, import-batch count/latest import, and backup count/latest backup. System Information shows Python, Windows, model, port, database/index/folder paths, and disk usage.

Select any diagnostic toggles or click **All**, then run diagnostics. Read pass/warn/fail status, timing, headline value, and detailed measurements. A warning can indicate an aging backup even when integrity is valid.

## 10. Repair, move, and uninstall

- Run **Update or Repair WSP** to recheck files, dependencies, model, and shortcuts while preserving data.
- On another computer, download/extract the release and run the one-click installer; never copy `.venv`.
- To migrate operational data, stop WSP and copy `data`, Import Folder, Export Folder, and `.models` if avoiding another model download.
- Run **Uninstall WSP**. Choosing not to delete data moves operational folders into a timestamped Documents folder.
