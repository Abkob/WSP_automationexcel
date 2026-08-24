# WSP Offline System

WSP Offline System is a private Windows application for importing Work Study Program Excel workbooks, reviewing the current student population, filtering records, running local AI-assisted searches, exporting results, and safely keeping import history and database backups.

After the first installation, the application runs locally at `http://127.0.0.1:8080`. Student data is stored on the same computer and is not sent to a cloud service.

## Quick start

1. Download `WSP_Offline_System_v1.1.5.zip` from the [latest GitHub release](https://github.com/Abkob/WSP_automationexcel/releases/latest) and extract it completely.
2. Double-click **`INSTALL WSP - ONE CLICK.bat`** at the top of a release package. If you are working directly inside the app folder, double-click **`INSTALL_WSP.bat`**.
3. Leave the installer window open until it reports that installation is complete.
4. After setup succeeds, the extracted installer folder can be deleted.
5. Double-click the new **WSP Offline System** desktop icon.
6. Open the new **WSP Import Folder** desktop shortcut and place the newest WSP `.xlsx` or `.xlsm` workbook there.
7. Open **Import Center** and click **Check Now** if the workbook has not already been imported.

The first installation needs internet access and can take 10-30 minutes because it installs the Python packages and downloads the local AI search model. Later launches are offline.

## What must be installed separately?

For a normal Windows 10 or Windows 11 computer, nothing needs to be installed manually:

- The one-click installer detects a compatible Python installation.
- If Python is missing, it asks Windows Package Manager (`winget`) to install 64-bit Python 3.12 for the current user.
- It creates a private `.venv` environment so WSP packages do not affect other applications.
- It installs every package from `requirements.txt`.
- It downloads the local `mixedbread-ai/mxbai-embed-large-v1` AI model into `.models`.
- It installs WSP under `%LOCALAPPDATA%\WSP Offline System` instead of depending on the extracted ZIP folder.
- It creates the Import Folder, Export Folder, application shortcut, Import Folder shortcut, repair shortcut, and uninstaller.

You do **not** need Node.js, Docker, Ollama, a database server, Microsoft Excel, or Microsoft Office to run WSP. Excel or another spreadsheet editor is only needed if you want to create or edit the source workbook.

Before installing, make sure the computer has:

- 64-bit Windows 10 or Windows 11;
- an internet connection for the first installation;
- Windows Package Manager (`winget`), which is normally included with current Windows installations; and
- at least 6 GB of free disk space for Python, scientific/AI packages, the local model, and working data.

If `winget` is unavailable and Python is not installed, install 64-bit Python 3.11 or 3.12 from [python.org](https://www.python.org/downloads/windows/), enable **Add python.exe to PATH**, and run `INSTALL_WSP.bat` again.

## What the installer does

The installer is safe to run again as an update or repair. It performs these steps:

1. Verifies 64-bit Windows, required package files, SHA-256 package checksums, and at least 6 GB of free space.
2. Copies the application to `%LOCALAPPDATA%\WSP Offline System\wsp_offline_app`.
3. Finds Python 3.11 or newer, preferring Python 3.12, or installs Python 3.12 with `winget` when missing.
4. Creates or repairs the private `.venv` without touching other Python applications.
5. Installs `requirements.txt` and runs `pip check`.
6. Downloads the AI embedding model and proves it can create an embedding offline.
7. Initializes the SQLite database and verifies required application routes and write access.
8. Creates the import, export, backup, log, and semantic-index folders.
9. Creates Desktop and Start Menu shortcuts for WSP, the Import Folder, repair, and uninstall.
10. Writes `install_manifest.json` and starts WSP only after every verification passes.

The detailed installation log is written to:

```text
%LOCALAPPDATA%\WSP Offline System\wsp_offline_app\data\install.log
```

## Folder layout and where to put the Excel file

The installer creates this layout automatically:

```text
%LOCALAPPDATA%\WSP Offline System\
|-- Import Folder\
|   |-- newest_wsp_workbook.xlsx      <-- put the newest workbook here
|   `-- archive\                      <-- older accepted workbooks move here
|-- Export Folder\                    <-- filtered exports appear here
`-- wsp_offline_app\
    |-- LAUNCH_WSP.bat
    |-- UPDATE_WSP.bat
    |-- UNINSTALL_WSP.bat
    |-- README.md
    |-- .venv\                        <-- created by the installer
    |-- .models\                      <-- local AI model
    `-- data\
        |-- wsp.db                    <-- live SQLite database
        |-- backups\                  <-- automatic database snapshots
        |-- semantic_index\           <-- local AI search index
        `-- logs\
```

By default, the exact source location is:

```text
%LOCALAPPDATA%\WSP Offline System\Import Folder
```

The exact export location is:

```text
%LOCALAPPDATA%\WSP Offline System\Export Folder
```

Both paths are displayed inside **Import Center**. The Import Folder can also be changed on that page: enter an absolute folder path, click **Save Folder**, and WSP will remember it. The Export Folder will then be created beside the selected Import Folder.

### Daily Excel workflow

1. Close the workbook in Excel so it has finished saving.
2. Copy the newest `.xlsx` or `.xlsm` file into the root of **Import Folder**. Do not put it inside `archive`.
3. Leave WSP running. It checks the folder automatically about every 30 seconds.
4. To import immediately, open **Import Center** and click **Check Now**.
5. Confirm the latest filename, import counts, and validation log on the page.
6. Use **Dashboard**, **Search & Match**, **Data Explorer**, or **Student Profiles** to review the imported data.

WSP identifies exact duplicate workbooks by file hash and skips them instead of importing them twice. After the newest workbook is accepted, older workbooks in the Import Folder are moved to `Import Folder\archive`. The newest accepted workbook remains in the root of Import Folder as the current source file.

Do not manually edit files in `data`, `data\backups`, `data\semantic_index`, or `Import Folder\archive`.

## Excel workbook requirements

The importer accepts:

- `.xlsx` workbooks;
- `.xlsm` workbooks; and
- the **first worksheet** in the workbook as the student data sheet.

It ignores temporary Excel lock files whose names begin with `~$`. Legacy `.xls` files and CSV files are not supported.

Prepare the workbook as follows:

- Row 1 must contain column headers.
- Each later row represents one student.
- `STUD_ID` is the required unique identifier. Rows without a usable `STUD_ID` are rejected and shown in the validation log.
- Keep IDs as text when leading zeroes are important.
- Header matching is case-insensitive and punctuation/spaces are normalized to underscores. For example, `stud id` becomes `STUD_ID`. The normalized name must still match the intended standard header; arbitrary synonyms are not remapped.
- Duplicate normalized headers should be avoided.
- Extra columns are preserved as additional student data and registered in the column schema.
- Missing expected columns are recorded in the import summary; they do not prevent valid rows from importing.
- Blank, invalid boolean, numeric, or date values may be normalized and reported as warnings.
- A workbook with headers but no valid student rows is rejected without replacing the current active population.

### Standard WSP columns

The application recognizes these standard columns:

| Group | Headers |
|---|---|
| Identity and contact | `STUD_ID`, `STUD_NAME`, `STUD_EMAIL`, `MOBILE_NBR` |
| Academic | `MAJR_DESC`, `CLAS_DESC`, `CUM_GPA`, `TOTAL_CREDIT_HOURS`, `LEVL_CODE`, `COLL_CODE`, `ENRL_TERM`, `STST_DESC`, `STYP_CODE`, `STYP_DESC`, `ENROLLED_IND`, `REGISTERED_IND` |
| Academic standing | `DEANS_WARNING`, `DEAN_WARN`, `PROBATION`, `ASTD_TERM`, `ATSD_CODE_END_OF_TERM`, `ASTD_DESC`, `ASTD_DATE_END_OF_TERM` |
| Languages and skills | `WSP_WRITTEN_LANGUAGES`, `WSP_SPOKEN_LANGUAGES`, `WSP_ORGANIZATIONAL_SKILLS`, `WSP_TECHNICAL_SKILLS`, `WSP_INTERPERSONAL_SKILLS`, `WSP_ADDITIONAL_SKILLS` |
| Work preferences/history | `WSP_PREV_WORK`, `WSP_PREVIOUS_TYPE_OF_WORK`, `WSP_PREFERRED_TYPE_OF_WORK`, `APPLICATION_DATE` |
| Programs and support | `USAID`, `MASTER_CARD`, `UPP_MEPI`, `GAS`, `FINANCIAL_AID`, `DORMS` |

When a later workbook changes a student, WSP updates the current record and keeps history. Students who were present before but are absent from the newest valid workbook are marked as missing; they are not deleted. The **Include missing students** option on the Search & Match page can include them in results.

## Pages and features

### Dashboard

The Dashboard is an applicant-review and placement workspace. It helps Work Study Program administrators understand the candidate pool, review talent signals, and open individual records without replacing the original application text.

- Dashboard modes separate **Placement Overview**, **Candidate Pool**, **Skills & Preferences**, **Funding & Logistics**, and **Data Quality** so each page answers a placement-related question.
- The shared filter bar supports faculty, major, class/year, and financial aid. Faculty, major, and class/year use checkbox multi-selects, so administrators can compare any combination instead of choosing only one value or the entire population.
- Faculty and major are cascading: selecting a faculty limits the Major menu to programs belonging to that faculty.
- Active filters become removable chips and are preserved in the page URL. Returning with the browser Back button restores the analytical context.
- KPI cards distinguish read-only indicators from clickable actions. Action cards are labeled **View** and update the relevant dashboard tab or filter.
- The Overview faculty comparison shows candidate volume, prior-experience coverage, financial-aid context, and housing context. Faculties with no records are hidden from interactive controls instead of creating empty dead ends.
- Candidate and support comparisons use percentages rather than raw totals where faculty or class population size would otherwise distort the comparison.
- GPA bands use columns, while category, rate, and score comparisons use sorted bars. When filters leave only one category, the chart switches to a compact animated spotlight instead of stretching one bar across the card. Every chart includes a plain-language text summary and tooltips with the underlying counts.
- The Work-Study view uses a hybrid preferred-work taxonomy. Free-text `WSP_PREFERRED_TYPE_OF_WORK` answers first map to reviewed work fields. Clear open-ended answers such as “anything available,” “any role,” or “wherever needed” map to **Flexible / Open to Any Role**.
- Recurring novel answers can form provisional **Emerging** semantic clusters. A single random answer, typo, or ambiguous response does not create a new field; it remains in **Needs Review** until there is repeated semantically similar evidence.
- Original answers remain unchanged and visible beside their field. Similarity confidence is retained for transparency. Emerging clusters are discovered against the complete active population so dashboard filters do not change their membership.
- Technical skills use the same population-wide approach. Each response is split into individual skill phrases, known tools and spelling variants map to stable topics, and recurring unfamiliar phrases can create dynamic **Emerging** skill topics only when they appear across at least two students. Isolated or uncertain skill text stays in **Unverified / Needs Review** and the source text is never rewritten.
- Preferred-work grouping is calculated locally with the bundled embedding model and cached in memory. New wording is evaluated automatically after an import; no internet service or generative chatbot is involved.
- Each worklist has its own placement purpose: candidate review, talent and preference discovery, funding/housing coordination, or records with missing core fields.
- The latest-import panel shows the source filename, time, row counts, and changes.
- **Print** creates a clean printable dashboard view.
- **Refresh** reloads the latest values from the local database.

The reviewed major-to-faculty map follows AUB's current academic structure instead of trusting `COLL_CODE` alone:

| Faculty / school | Mapped WSP majors |
|---|---|
| FAS | Psychology, Political Science, Computer Science, Chemistry, Biology, English Literature |
| OSB | Business Administration, Accounting, Finance, Marketing |
| MSFEA | Architecture, Electrical Engineering, Graphic Design |
| FHS | Public Health |
| HSON | Nursing |
| FAFS | No majors in the current WSP dataset |
| Faculty of Medicine | No majors in the current WSP dataset |

Unknown future majors appear in an explicit **Unmapped** group rather than being silently assigned to an incorrect faculty.

Dashboard data comes from the current SQLite database, not directly from an Excel file. A workbook must first be accepted by the importer.

### Search & Match

Search & Match builds a query against the `students_current` database table.

- **Global search** looks across student fields such as ID, name, email, major, skills, and preferred work.
- **Ask local AI** performs semantic matching. It is useful for meaning-based requests such as “students suited for social media design” even when those exact words are not in a cell.
- Semantic filtering embeds the original, untouched student responses—including technical skills, preferred work, previous experience, other skill fields, and languages. Dashboard grouping labels are never substituted into the search document, so rare wording, misspellings, and unique experience details remain searchable.
- Each embedding result cites the two closest original student fields and their field-level similarity scores. Administrators can verify that every stored vector still matches current source text with `python scripts/audit_semantic_index.py`; the audit writes `testbench_reports/semantic_index_audit.json` and does not modify student data.
- **Re-embed All** in Import Center now performs a true forced rebuild of every active student vector. Routine startup and imports remain incremental so unchanged profiles are not needlessly encoded.
- **Threshold Match** controls the minimum semantic similarity. A higher threshold is stricter.
- **Top-K Results** limits the number of displayed AI results.
- **Name contains** and **Skills contain** perform direct text filtering.
- **Minimum GPA** and **Maximum GPA** create a GPA range.
- **Major** and **Class / Year** support multiple selections.
- **Probation**, **Aid**, and **Dorms** accept Any, Yes, or No.
- **Sort by** and **Order** control result ordering.
- **Include missing students** includes records absent from the most recent workbook.
- Active filter tags show what is currently applied.
- While a search runs, an AUB-maroon three-dot pulse and progress card describe the current pipeline stage, such as reading filters, searching the local AI index, ranking matches, and preparing results. These are user-facing status messages, not hidden model reasoning.
- Result rows display student details, semantic match score, and a short explanation.
- Click a student's ID or name to open their complete profile. You can also double-click a result row or right-click it and choose **View student profile**.
- Filter preferences are saved automatically in the local browser profile on that computer.
- **Clear saved** removes those stored preferences.
- **Reset** clears the form for the current search.
- **Export** writes every matching record to an Excel workbook in Export Folder.

The AI index badge shows how much of the active population is indexed. If coverage is incomplete, open **Import Center** and use **Re-embed All**.

### Data Explorer

Data Explorer provides spreadsheet-style views generated from the database. It does not display the source workbook directly.

- **Current Students** shows the current directory used by Search & Match.
- **Import Issues** shows rejected rows and normalization warnings.
- **Column Schema** shows detected columns, data types, active/missing state, and first/last batches.
- **Major Analytics** shows student counts grouped by major.
- The global search field searches across every sheet and value.
- The sheet search field filters the currently selected sheet.
- Selecting a cell displays its content in the formula preview bar.
- In **Current Students**, click a student's ID or name to open their profile. You can also double-click or right-click the row and choose **View student profile**. These profile actions are disabled while Edit mode is active.
- **Edit** is available on Current Students for supported fields: name, major, class, GPA, email, financial aid, probation, and dorms.
- Saving edits creates an automatic database backup first.

Manual database edits can be overwritten by the next Excel import. Make long-term corrections in the source workbook as well.

### Student Profiles

Student Profiles is the holistic record view for an individual student. It is available from the **Student Profiles** navigation item and directly from student rows in Search & Match and Data Explorer.

- **Find a student** searches the local database by student name, ID, AUB email, or major. Press Enter to open the first match.
- The identity header keeps the student's name, ID, major, class, email, mobile number, and important status badges visible together.
- Highlight cards summarize cumulative GPA, credit hours, academic standing, and enrollment/registration state.
- **Academic record** presents program, student type, college, level, enrollment term, GPA, and credits.
- **Standing & alerts** presents standing codes and dates, probation, and dean-warning flags without hiding negative or unknown states.
- **Skills & languages** turns the student's technical, organizational, interpersonal, additional-skill, spoken-language, and written-language fields into readable groups.
- **Work-study profile** presents previous experience, previous work type, and preferred work type.
- **Aid, programs & housing** presents Financial Aid, USAID, Mastercard Foundation, UPP/MEPI, GAS, and dorm participation as Yes, No, or Not provided.
- **Additional information** preserves and displays non-standard columns imported from Excel, such as supervisor or office fields.
- **Record details** identifies whether the record is current, when it was added or modified, and the first/latest source workbook.
- **Record timeline** presents the history retained by imports, including updates and occasions when a student was absent from a later workbook.
- **Print profile** produces a clean paper/PDF view without the navigation, search, or admin controls.

The profile does not calculate private model reasoning or invent advising notes. Every displayed fact comes from the current SQLite student record, retained import history, or preserved extra Excel columns.

### Import Center

Import Center is the operations center.

- **Auto Export** uses the saved preferences from Search & Match and creates a filtered workbook immediately.
- **Import Folder path** displays or changes the watched folder.
- **Save Folder** stores a new watched-folder location.
- **Check Now** immediately scans the folder rather than waiting for the automatic interval.
- **Current workbook** shows the accepted source file.
- **Folder archive** shows how many old Excel files are retained.
- **AI Search Index** shows indexed-student coverage and offers **Re-embed All** when needed.
- **Import Pipeline Progress** shows acceptance, backup, schema, database merge, and post-import backup stages.
- **Detected Columns Schema** displays the registered workbook fields.
- **Validation Execution Log** shows completed imports, rejected rows, duplicate files, normalization warnings, and failures.
- **Backup Vault** lists automatic snapshots, integrity status, file size, and reason.
- **Restore** rolls the database back to a selected snapshot after first creating an emergency pre-restore backup.
- The page lists the exact Import Folder, Export Folder, archive, and backup paths.

Import safety behavior:

1. WSP waits for the workbook file size to stabilize.
2. It checks that the exact file has not already been imported.
3. It creates a pre-import database backup.
4. It archives a copy of the original source.
5. It validates and normalizes the workbook.
6. It merges all valid rows in one database transaction.
7. If the transaction fails, the changes are rolled back.
8. It creates a post-import backup.
9. It refreshes the local semantic search index in the background.

Filtered exports are named like:

```text
YYYYMMDD_HHMMSS_filtered_students.xlsx
```

Each export contains:

- **Filtered Results**: the matching student rows; and
- **Filter Metadata**: the filters, sort settings, and source batch information used to create the file.

### System Health

The System Diagnostics page is the first place to check when something appears wrong.

- Health cards show active/total students, database status and size, latest import, backups, and indexed-student count.
- **Refresh** reloads current status.
- **Run All Diagnostics** runs the complete set of checks.
- Individual checks cover database connectivity, database integrity, the embedding model, semantic search, Import Folder, Export Folder, Backup Vault, and vector index.
- System Information displays Python/Windows versions, configured model, port, disk usage, and the exact database/index/import/export/backup paths.

## Launching and closing the application

Launch WSP in any of these ways:

- double-click the **WSP Offline System** desktop shortcut;
- open **WSP Offline System** from the Windows Start Menu; or
- double-click `LAUNCH_WSP.bat` in the app folder.

WSP starts a private local server and opens Chrome or Edge in app-window mode when available. If neither browser is found in its standard location, the default browser is used.

Closing the browser window does not necessarily stop WSP. The tray icon keeps the local server running.

- Double-click the tray icon, or right-click it and choose **Open WSP**, to reopen the window.
- Right-click the tray icon and choose **Exit** to stop WSP completely.
- The app also has an exit action that shuts down the local server.

Only one WSP instance uses port `8080`. Launching the shortcut while WSP is already running reopens the window.

## Updating or repairing

For a new release package, exit WSP and run the new package's **INSTALL WSP - ONE CLICK.bat** again. Setup copies the new application files into the installed location while preserving `data`, `.models`, and the Import/Export folders.

`UPDATE_WSP.bat` reuses the installer in repair mode. It checks Python, repairs the virtual environment, synchronizes all requirements, verifies the local AI model, and recreates shortcuts. It does not erase the database or backups.

Running `INSTALL_WSP.bat` again is also safe.

## Moving WSP to another computer

Download or copy the release ZIP to the new computer, extract it, then run the one-click installer. Do not copy `.venv` between computers; setup creates the correct environment for the destination machine.

To move existing operational data, copy these while WSP is fully stopped:

- `wsp_offline_app\data`;
- `Import Folder`;
- `Export Folder`; and
- optionally `wsp_offline_app\.models` to avoid downloading the AI model again.

The installer does not delete an existing database, model, archive, backup, import, or export file.

## Backups and recovery

Automatic SQLite backups are stored in:

```text
wsp_offline_app\data\backups
```

Backups are created before imports, after successful imports, before restores, and before supported manual edits. Use **Import Center > Backup Vault > Restore** for the safest recovery workflow.

Original or retired Excel workbooks are separate from database backups and are stored under:

```text
Import Folder\archive
```

For an additional disaster-recovery copy, stop WSP and copy `%LOCALAPPDATA%\WSP Offline System` to an encrypted institutional drive.

## Uninstalling

Open **Start > WSP Offline System > Uninstall WSP** or run `UNINSTALL_WSP.bat` from the installed app folder. The uninstaller asks whether local data should be deleted. If you choose No, it moves the database, imported workbooks, exports, and backups into a timestamped folder under Documents before removing the application.

If setup added Python 3.12 and no other application needs it, Python can be removed separately from **Windows Settings > Apps**.

## Troubleshooting

### The installer stops with a Python or winget error

Install 64-bit Python 3.11 or 3.12 from python.org, enable **Add python.exe to PATH**, restart Windows, and run `INSTALL_WSP.bat` again.

### Package or model download fails

Confirm internet access, free disk space, and any institutional proxy/firewall requirements. Run `UPDATE_WSP.bat` to resume. Package and model downloads are cached, so completed parts normally do not need to download again.

### The desktop icon does not work

Run **Update or Repair WSP** from the Start Menu. The installed application no longer depends on the location of the extracted release package.

### A workbook does not import

- Confirm that it is `.xlsx` or `.xlsm`, not `.xls` or `.csv`.
- Close Excel so the file is no longer being written.
- Confirm the first worksheet contains headers in row 1.
- Confirm at least one data row has a usable `STUD_ID`.
- Open **Import Center**, click **Check Now**, and read the Validation Execution Log.

### Search works but AI matching does not

Open **Import Center** and inspect the AI Search Index. Use **Re-embed All** if coverage is incomplete. Then run the embedding-model, semantic-search, and vector-index checks in **System Health**.

### The app does not open

- Look for the WSP tray icon; WSP may already be running.
- Open `http://127.0.0.1:8080` in a browser.
- Make sure another application is not occupying port 8080.
- Review `wsp_offline_app\data\launcher.log`.
- Run `UPDATE_WSP.bat`, then try again.

### Useful logs

```text
%LOCALAPPDATA%\WSP Offline System\wsp_offline_app\data\install.log
%LOCALAPPDATA%\WSP Offline System\wsp_offline_app\data\launcher.log
%LOCALAPPDATA%\WSP Offline System\wsp_offline_app\data\logs\
```

## Creating a distributable release

Developers can double-click `BUILD_RELEASE.bat`, or run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build_release.ps1
```

This creates:

```text
dist\WSP_Offline_System_v<version>.zip
dist\WSP_Offline_System_v<version>.zip.sha256
```

The release excludes the developer virtual environment, cached model, live database, backups, tests, and other machine-specific files. It includes the one-click installer, uninstaller, verification script, internal package checksum manifest, and empty Import/Export folders. Publish both the ZIP and its `.sha256` file. On the destination computer, extract the ZIP completely and run **INSTALL WSP - ONE CLICK.bat**.

## Development

Run the app with a visible console:

```powershell
.\.venv\Scripts\python.exe main.py
```

Run the test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Generate test workbooks:

```powershell
.\.venv\Scripts\python.exe scripts\create_test_workbooks.py
```

Main runtime requirements are declared in both `requirements.txt` and `pyproject.toml`. The installer uses `requirements.txt`.
