# WSP Offline System

WSP Offline System is a private Windows application for importing Work Study Program Excel workbooks, reviewing the current student population, filtering records, running local AI-assisted searches, exporting results, and safely keeping import history and database backups.

After the first installation, the application runs locally at `http://127.0.0.1:8080`. Student data is stored on the same computer and is not sent to a cloud service.

## Quick start

1. Keep the complete package folder together after extracting it.
2. Double-click **`INSTALL WSP - ONE CLICK.bat`** at the top of a release package. If you are working directly inside the app folder, double-click **`INSTALL_WSP.bat`**.
3. Leave the installer window open until it reports that installation is complete.
4. Put the newest WSP `.xlsx` or `.xlsm` workbook in the **`Import Folder`** beside `wsp_offline_app`.
5. Double-click the new **WSP Offline System** desktop icon.
6. Open **Import / Export** and click **Check Now** if the workbook has not already been imported.

The first installation needs internet access and can take 10-30 minutes because it installs the Python packages and downloads the local AI search model. Later launches are offline.

## What must be installed separately?

For a normal Windows 10 or Windows 11 computer, nothing needs to be installed manually:

- The one-click installer detects a compatible Python installation.
- If Python is missing, it asks Windows Package Manager (`winget`) to install 64-bit Python 3.12 for the current user.
- It creates a private `.venv` environment so WSP packages do not affect other applications.
- It installs every package from `requirements.txt`.
- It downloads the local `mixedbread-ai/mxbai-embed-large-v1` AI model into `.models`.
- It creates the Import Folder, Export Folder, Desktop shortcut, and Start Menu shortcut.

You do **not** need Node.js, Docker, Ollama, a database server, Microsoft Excel, or Microsoft Office to run WSP. Excel or another spreadsheet editor is only needed if you want to create or edit the source workbook.

Before installing, make sure the computer has:

- 64-bit Windows 10 or Windows 11;
- an internet connection for the first installation;
- Windows Package Manager (`winget`), which is normally included with current Windows installations; and
- approximately 5 GB of free disk space for Python, scientific/AI packages, the local model, and working data.

If `winget` is unavailable and Python is not installed, install 64-bit Python 3.11 or 3.12 from [python.org](https://www.python.org/downloads/windows/), enable **Add python.exe to PATH**, and run `INSTALL_WSP.bat` again.

## What the installer does

The installer is safe to run again as an update or repair. It performs these steps:

1. Finds Python 3.11 or newer, preferring Python 3.12.
2. Installs Python 3.12 for the current Windows user when Python is missing.
3. Creates or reuses `wsp_offline_app\.venv`.
4. Upgrades the package installer and installs `requirements.txt`.
5. runs `pip check` to verify that installed packages are compatible.
6. Downloads and verifies the AI embedding model in `wsp_offline_app\.models`.
7. Creates the import, export, backup, log, and semantic-index folders.
8. Creates **WSP Offline System** shortcuts on the Desktop and Start Menu.
9. Starts WSP after a successful installation.

The detailed installation log is written to:

```text
wsp_offline_app\data\install.log
```

## Folder layout and where to put the Excel file

Keep this layout:

```text
WSP Offline System\
|-- INSTALL WSP - ONE CLICK.bat
|-- Import Folder\
|   |-- newest_wsp_workbook.xlsx      <-- put the newest workbook here
|   `-- archive\                      <-- older accepted workbooks move here
|-- Export Folder\                    <-- filtered exports appear here
`-- wsp_offline_app\
    |-- INSTALL_WSP.bat
    |-- LAUNCH_WSP.bat
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
<folder containing wsp_offline_app>\Import Folder
```

The exact export location is:

```text
<folder containing wsp_offline_app>\Export Folder
```

Both paths are displayed inside the **Import / Export** page. The Import Folder can also be changed on that page: enter an absolute folder path, click **Save Folder**, and WSP will remember it. The Export Folder will then be created beside the selected Import Folder.

### Daily Excel workflow

1. Close the workbook in Excel so it has finished saving.
2. Copy the newest `.xlsx` or `.xlsm` file into the root of **Import Folder**. Do not put it inside `archive`.
3. Leave WSP running. It checks the folder automatically about every 30 seconds.
4. To import immediately, open **Import / Export** and click **Check Now**.
5. Confirm the latest filename, import counts, and validation log on the page.
6. Use **Dashboard**, **Filtering**, or **Excel Sheets** to review the imported data.

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

When a later workbook changes a student, WSP updates the current record and keeps history. Students who were present before but are absent from the newest valid workbook are marked as missing; they are not deleted. The **Include missing students** option on the Filtering page can include them in results.

## Pages and features

### Dashboard

The Dashboard is the high-level overview of the current imported population.

- Metric cards summarize active records, population state, and key totals.
- The latest-import panel shows the source filename, time, row counts, and changes.
- **Students by major** ranks the largest majors.
- **GPA distribution** groups students into GPA ranges.
- **Average GPA by major** compares academic averages.
- **Probation by major** highlights probation counts.
- **Refresh** reloads the latest values from the local database.

Dashboard data comes from the current SQLite database, not directly from an Excel file. A workbook must first be accepted by the importer.

### Filtering

The Filtering page builds a query against the `students_current` database table.

- **Global search** looks across student fields such as ID, name, email, major, skills, and preferred work.
- **Ask local AI** performs semantic matching. It is useful for meaning-based requests such as “students suited for social media design” even when those exact words are not in a cell.
- **Threshold Match** controls the minimum semantic similarity. A higher threshold is stricter.
- **Top-K Results** limits the number of displayed AI results.
- **Name contains** and **Skills contain** perform direct text filtering.
- **Minimum GPA** and **Maximum GPA** create a GPA range.
- **Major** and **Class / Year** support multiple selections.
- **Probation**, **Aid**, and **Dorms** accept Any, Yes, or No.
- **Sort by** and **Order** control result ordering.
- **Include missing students** includes records absent from the most recent workbook.
- Active filter tags show what is currently applied.
- Result rows display student details, semantic match score, and a short explanation.
- Filter preferences are saved automatically in the local browser profile on that computer.
- **Clear saved** removes those stored preferences.
- **Reset** clears the form for the current search.
- **Export** writes every matching record to an Excel workbook in Export Folder.

The AI index badge shows how much of the active population is indexed. If coverage is incomplete, open **Import / Export** and use **Rebuild Index**.

### Excel Sheets

Excel Sheets provides spreadsheet-style views generated from the database. It does not display the source workbook directly.

- **Current Students** shows the current directory used by Filtering.
- **Import Issues** shows rejected rows and normalization warnings.
- **Column Schema** shows detected columns, data types, active/missing state, and first/last batches.
- **Major Analytics** shows student counts grouped by major.
- The global search field searches across every sheet and value.
- The sheet search field filters the currently selected sheet.
- Selecting a cell displays its content in the formula preview bar.
- **Edit** is available on Current Students for supported fields: name, major, class, GPA, email, financial aid, probation, and dorms.
- Saving edits creates an automatic database backup first.

Manual database edits can be overwritten by the next Excel import. Make long-term corrections in the source workbook as well.

### Import / Export

Import / Export is the operations center.

- **Auto Export** uses the saved preferences from the Filtering page and creates a filtered workbook immediately.
- **Import Folder path** displays or changes the watched folder.
- **Save Folder** stores a new watched-folder location.
- **Check Now** immediately scans the folder rather than waiting for the automatic interval.
- **Current workbook** shows the accepted source file.
- **Folder archive** shows how many old Excel files are retained.
- **AI Search Index** shows indexed-student coverage and offers **Rebuild Index** when needed.
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

### Test/System Status

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

For a copied code update or a package change:

1. Exit WSP from the tray icon.
2. Replace the updated application files while preserving `data`, `.models`, and the Import/Export folders.
3. Double-click `UPDATE_WSP.bat`.
4. Launch WSP normally.

`UPDATE_WSP.bat` reuses the installer in repair mode. It checks Python, repairs the virtual environment, synchronizes all requirements, verifies the local AI model, and recreates shortcuts. It does not erase the database or backups.

Running `INSTALL_WSP.bat` again is also safe.

## Moving WSP to another computer

Copy or extract the complete package to the new computer, then run the one-click installer there. Do not copy `.venv` between computers; the installer creates the correct environment for the destination machine.

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

Backups are created before imports, after successful imports, before restores, and before supported manual edits. Use **Import / Export > Backup Vault > Restore** for the safest recovery workflow.

Original or retired Excel workbooks are separate from database backups and are stored under:

```text
Import Folder\archive
```

For an additional disaster-recovery copy, stop WSP and copy the whole package folder to an encrypted institutional drive.

## Uninstalling

1. Exit WSP from the tray icon.
2. Back up `data`, Import Folder, and Export Folder if the records must be retained.
3. Delete the **WSP Offline System** Desktop and Start Menu shortcuts.
4. Delete the complete WSP package folder.

The WSP-specific Python environment and AI model are inside the package folder. If the installer added Python 3.12 and no other application needs it, it can be removed separately from **Windows Settings > Apps**.

## Troubleshooting

### The installer stops with a Python or winget error

Install 64-bit Python 3.11 or 3.12 from python.org, enable **Add python.exe to PATH**, restart Windows, and run `INSTALL_WSP.bat` again.

### Package or model download fails

Confirm internet access, free disk space, and any institutional proxy/firewall requirements. Run `UPDATE_WSP.bat` to resume. Package and model downloads are cached, so completed parts normally do not need to download again.

### The desktop icon does not work after moving the folder

Shortcuts contain the full installation path. Run `UPDATE_WSP.bat` from the new location to recreate them.

### A workbook does not import

- Confirm that it is `.xlsx` or `.xlsm`, not `.xls` or `.csv`.
- Close Excel so the file is no longer being written.
- Confirm the first worksheet contains headers in row 1.
- Confirm at least one data row has a usable `STUD_ID`.
- Open **Import / Export**, click **Check Now**, and read the Validation Execution Log.

### Search works but AI matching does not

Open **Import / Export** and inspect the AI Search Index. Use **Rebuild Index** if coverage is incomplete. Then run the embedding-model, semantic-search, and vector-index checks on **Test/System Status**.

### The app does not open

- Look for the WSP tray icon; WSP may already be running.
- Open `http://127.0.0.1:8080` in a browser.
- Make sure another application is not occupying port 8080.
- Review `wsp_offline_app\data\launcher.log`.
- Run `UPDATE_WSP.bat`, then try again.

### Useful logs

```text
wsp_offline_app\data\install.log
wsp_offline_app\data\launcher.log
wsp_offline_app\data\logs\
```

## Creating a distributable release

Developers can double-click `BUILD_RELEASE.bat`, or run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build_release.ps1
```

This creates:

```text
dist\WSP_Offline_System_v<version>.zip
```

The release excludes the developer virtual environment, cached model, live database, backups, tests, and other machine-specific files. It includes the one-click installer and empty Import/Export folders. Send the ZIP to the destination computer, extract it completely, and run **INSTALL WSP - ONE CLICK.bat**.

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
