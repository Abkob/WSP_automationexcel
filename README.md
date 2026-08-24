# WSP Offline System

**A privacy-first Windows application for importing, auditing, searching, and matching Work Study Program records without sending student data to a cloud service.**

WSP Offline System turns recurring Excel-based administration into a reproducible local workflow. It validates new workbooks, preserves import history, builds an auditable student directory, supports structured and semantic search, and exports placement-ready results. The application, SQLite database, local embedding model, indexes, logs, and backups remain on the administrator's computer.

## Why this project exists

Spreadsheet workflows are flexible, but they make schema drift, duplicate imports, historical comparison, privacy, and consistent matching difficult. WSP adds a controlled layer around the source workbook while keeping Excel as the operational handoff format.

## Highlights

- Workbook validation, normalized schemas, duplicate detection, and import lineage
- Placement dashboard with multi-select filters and transparent population summaries
- Student profiles, record timelines, data-quality views, and editable supported fields
- Direct filters plus local semantic search over original, unmodified responses
- Evidence for every semantic match through source fields and similarity scores
- Population-level preferred-work and technical-skill grouping with review buckets
- Excel export, automatic database snapshots, health checks, and recovery tooling
- One-click Windows installation with offline operation after initial setup

## Privacy and research principles

- Student workbooks, databases, exports, logs, embeddings, and backups are excluded from Git.
- The local model ranks text; it does not generate hidden student evaluations.
- Original student responses remain available beside any derived grouping.
- Rare or ambiguous terms remain in explicit review categories instead of being forced into a label.
- Screenshots and presentation assets remain outside the public repository unless they have been independently de-identified.

## Architecture

```text
Excel workbook
      |
      v
validation + normalization + import ledger
      |
      v
SQLite current state + history + backups
      |                         |
      v                         v
structured filters       local embeddings / FAISS
      |                         |
      +-----------+-------------+
                  v
       review, profiles, and Excel export
```

The codebase is a Python desktop-local web application with SQLite, pandas/openpyxl import and export, locally bundled sentence embeddings, FAISS search, a Windows launcher/installer, and pytest coverage.

## Install the packaged application

1. Download `WSP_Offline_System_v1.1.5.zip` from the [latest release](https://github.com/Abkob/WSP_automationexcel/releases/latest).
2. Extract the ZIP completely.
3. Double-click **`INSTALL WSP - ONE CLICK.bat`**.
4. Use the desktop shortcuts created for the application and its import folder.

The first installation downloads Python dependencies and the local embedding model. Later use is offline.

## Run from source

```powershell
cd wsp_offline_app
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe wsp_launcher.pyw
```

Do not use real student workbooks for development or tests. The test suite creates controlled fixtures.

## Documentation

- [Complete operator and installation guide](wsp_offline_app/README.md)
- [Generated code reference](wsp_offline_app/docs/code_reference)
- [Release workflow](.github/workflows/windows-release.yml)

## Repository boundary

The public repository contains source, tests, and text documentation. Local workbooks, university documents, research-paper PDFs, screenshots, presentations, release build artifacts, databases, models, and operational records remain outside version control.

## Status

Version 1.1.5 is the current development line in this working tree. The system is designed for controlled administrative use and should be validated against the intended schema and institutional policies before deployment.

## Attribution

This is an independent software and research-engineering project. Institutional names and marks remain the property of their respective owners and do not imply endorsement of this repository.
