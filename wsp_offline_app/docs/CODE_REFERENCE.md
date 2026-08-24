# Complete code reference

This is the generated source-level index for WSP Offline System. Every first-party source, test, installer, workflow, configuration, and dependency declaration has a dedicated Markdown page.

**Documented files:** 108

[Documentation home](README.md) · [Feature and code flows](FEATURES_AND_CODE_FLOW.md) · [Architecture](ARCHITECTURE.md) · [User manual](USER_MANUAL.md)

## `.github`

| Source file | Responsibility | Lines |
|---|---|---:|
| [`.github/workflows/windows-release.yml`](code_reference/.github/workflows/windows-release.yml.md) | Builds and uploads the verified Windows installer package on main/tag pushes and attaches assets to versioned GitHub Releases. | 41 |

## `.gitignore`

| Source file | Responsibility | Lines |
|---|---|---:|
| [`.gitignore`](code_reference/.gitignore.md) | Prevents machine-specific environments, models, databases, reports, and release outputs from entering source control. | 27 |

## `BUILD_RELEASE.bat`

| Source file | Responsibility | Lines |
|---|---|---:|
| [`BUILD_RELEASE.bat`](code_reference/BUILD_RELEASE.bat.md) | Provides a double-clickable Windows entry point that delegates to the corresponding verified PowerShell or Python workflow. | 18 |

## `INSTALL_WSP.bat`

| Source file | Responsibility | Lines |
|---|---|---:|
| [`INSTALL_WSP.bat`](code_reference/INSTALL_WSP.bat.md) | Provides a double-clickable Windows entry point that delegates to the corresponding verified PowerShell or Python workflow. | 34 |

## `LAUNCH_WSP.bat`

| Source file | Responsibility | Lines |
|---|---|---:|
| [`LAUNCH_WSP.bat`](code_reference/LAUNCH_WSP.bat.md) | Provides a double-clickable Windows entry point that delegates to the corresponding verified PowerShell or Python workflow. | 13 |

## `UNINSTALL_WSP.bat`

| Source file | Responsibility | Lines |
|---|---|---:|
| [`UNINSTALL_WSP.bat`](code_reference/UNINSTALL_WSP.bat.md) | Provides a double-clickable Windows entry point that delegates to the corresponding verified PowerShell or Python workflow. | 19 |

## `UPDATE_WSP.bat`

| Source file | Responsibility | Lines |
|---|---|---:|
| [`UPDATE_WSP.bat`](code_reference/UPDATE_WSP.bat.md) | Provides a double-clickable Windows entry point that delegates to the corresponding verified PowerShell or Python workflow. | 21 |

## `app`

| Source file | Responsibility | Lines |
|---|---|---:|
| [`app/__init__.py`](code_reference/app/__init__.py.md) | Supports the WSP Offline System as the repository artifact `app/__init__.py`. | 3 |
| [`app/components/__init__.py`](code_reference/app/components/__init__.py.md) | Defines reusable UI data structures and rendering helpers for the   init   area. | 3 |
| [`app/components/chart_card.py`](code_reference/app/components/chart_card.py.md) | Defines reusable UI data structures and rendering helpers for the chart card area. | 89 |
| [`app/components/filter_panel.py`](code_reference/app/components/filter_panel.py.md) | Defines reusable UI data structures and rendering helpers for the filter panel area. | 173 |
| [`app/components/import_status_card.py`](code_reference/app/components/import_status_card.py.md) | Defines reusable UI data structures and rendering helpers for the import status card area. | 29 |
| [`app/components/metric_card.py`](code_reference/app/components/metric_card.py.md) | Defines reusable UI data structures and rendering helpers for the metric card area. | 30 |
| [`app/components/sidebar.py`](code_reference/app/components/sidebar.py.md) | Defines reusable UI data structures and rendering helpers for the sidebar area. | 45 |
| [`app/components/student_profile_dialog.py`](code_reference/app/components/student_profile_dialog.py.md) | Defines reusable UI data structures and rendering helpers for the student profile dialog area. | 3 |
| [`app/components/student_table.py`](code_reference/app/components/student_table.py.md) | Defines reusable UI data structures and rendering helpers for the student table area. | 109 |
| [`app/layout.py`](code_reference/app/layout.py.md) | Supports the WSP Offline System as the repository artifact `app/layout.py`. | 105 |
| [`app/pages/__init__.py`](code_reference/app/pages/__init__.py.md) | Defines the legacy/component-level page adapter for   init  ; the production browser shell is served by app/web_app.py. | 3 |
| [`app/pages/dashboard_page.py`](code_reference/app/pages/dashboard_page.py.md) | Defines the legacy/component-level page adapter for dashboard page; the production browser shell is served by app/web_app.py. | 128 |
| [`app/pages/filter_page.py`](code_reference/app/pages/filter_page.py.md) | Defines the legacy/component-level page adapter for filter page; the production browser shell is served by app/web_app.py. | 243 |
| [`app/pages/history_page.py`](code_reference/app/pages/history_page.py.md) | Defines the legacy/component-level page adapter for history page; the production browser shell is served by app/web_app.py. | 10 |
| [`app/pages/import_page.py`](code_reference/app/pages/import_page.py.md) | Defines the legacy/component-level page adapter for import page; the production browser shell is served by app/web_app.py. | 10 |
| [`app/pages/settings_page.py`](code_reference/app/pages/settings_page.py.md) | Defines the legacy/component-level page adapter for settings page; the production browser shell is served by app/web_app.py. | 10 |
| [`app/pages/student_profile_page.py`](code_reference/app/pages/student_profile_page.py.md) | Defines the legacy/component-level page adapter for student profile page; the production browser shell is served by app/web_app.py. | 10 |
| [`app/routes.py`](code_reference/app/routes.py.md) | Supports the WSP Offline System as the repository artifact `app/routes.py`. | 55 |
| [`app/static/chart.umd.min.js`](code_reference/app/static/chart.umd.min.js.md) | Supports the WSP Offline System as the repository artifact `app/static/chart.umd.min.js`. | 21 |
| [`app/static/wsp.css`](code_reference/app/static/wsp.css.md) | Defines the complete AUB-branded responsive visual system for navigation, dashboards, tables, profiles, forms, diagnostics, printing, and loading states. | 3,618 |
| [`app/static/wsp.js`](code_reference/app/static/wsp.js.md) | Implements all browser-side interaction: dashboard navigation, filtering, saved preferences, semantic-search progress, data editing, profile navigation, import operations, backup restore, and diagnostics. | 3,140 |
| [`app/theme.py`](code_reference/app/theme.py.md) | Supports the WSP Offline System as the repository artifact `app/theme.py`. | 52 |
| [`app/web_app.py`](code_reference/app/web_app.py.md) | Defines the production FastAPI routes, HTML shell, import orchestration, dashboard APIs, diagnostics, backup endpoints, and request/response adapters. | 2,151 |

## `config.py`

| Source file | Responsibility | Lines |
|---|---|---:|
| [`config.py`](code_reference/config.py.md) | Defines immutable application settings, runtime modes, filesystem locations, model configuration, and required data directories. | 118 |

## `database`

| Source file | Responsibility | Lines |
|---|---|---:|
| [`database/__init__.py`](code_reference/database/__init__.py.md) | Implements part of the local SQLite persistence layer:   init  . | 3 |
| [`database/db.py`](code_reference/database/db.py.md) | Creates and configures SQLite engines/sessions, enables safety pragmas, initializes tables, and exposes database health helpers. | 65 |
| [`database/migrations.py`](code_reference/database/migrations.py.md) | Applies lightweight backwards-compatible schema migrations when older local databases are opened. | 53 |
| [`database/models.py`](code_reference/database/models.py.md) | Declares the SQLite/SQLAlchemy data model for current students, retained history, imports, schemas, filters, exports, embeddings, and backups. | 206 |
| [`database/queries.py`](code_reference/database/queries.py.md) | Provides reusable database query helpers for current-student and import-history access. | 3 |
| [`database/schema_manager.py`](code_reference/database/schema_manager.py.md) | Tracks workbook columns, infers data types, and synchronizes the dynamic column registry. | 129 |

## `main.py`

| Source file | Responsibility | Lines |
|---|---|---:|
| [`main.py`](code_reference/main.py.md) | Creates the startup context, prepares runtime folders/database state, and launches the local FastAPI application through Uvicorn. | 50 |

## `package-lock.json`

| Source file | Responsibility | Lines |
|---|---|---:|
| [`package-lock.json`](code_reference/package-lock.json.md) | Records the JavaScript dependency lock state retained for repository reproducibility. | 7 |

## `pyproject.toml`

| Source file | Responsibility | Lines |
|---|---|---:|
| [`pyproject.toml`](code_reference/pyproject.toml.md) | Defines project metadata, supported Python version, dependencies, and pytest configuration. | 29 |

## `requirements.lock.txt`

| Source file | Responsibility | Lines |
|---|---|---:|
| [`requirements.lock.txt`](code_reference/requirements.lock.txt.md) | Declares the Python packages required to install and reproduce the WSP runtime. | 87 |

## `requirements.txt`

| Source file | Responsibility | Lines |
|---|---|---:|
| [`requirements.txt`](code_reference/requirements.txt.md) | Declares the Python packages required to install and reproduce the WSP runtime. | 19 |

## `scripts`

| Source file | Responsibility | Lines |
|---|---|---:|
| [`scripts/audit_semantic_index.py`](code_reference/scripts/audit_semantic_index.py.md) | Audits every stored semantic vector against the current source text and reports coverage, hash consistency, and stale records without modifying data. | 103 |
| [`scripts/build_release.ps1`](code_reference/scripts/build_release.ps1.md) | Builds the distributable Windows ZIP, internal SHA-256 manifest, external checksum, and clean release folder structure. | 134 |
| [`scripts/bundle_model.py`](code_reference/scripts/bundle_model.py.md) | Provides the operational or development utility named bundle model. | 77 |
| [`scripts/create_shortcut_icon.py`](code_reference/scripts/create_shortcut_icon.py.md) | Provides the operational or development utility named create shortcut icon. | 41 |
| [`scripts/create_test_workbooks.py`](code_reference/scripts/create_test_workbooks.py.md) | Supports repeatable development testbench execution and produces auditable local test data or reports. | 459 |
| [`scripts/create_testbench.py`](code_reference/scripts/create_testbench.py.md) | Supports repeatable development testbench execution and produces auditable local test data or reports. | 864 |
| [`scripts/download_mxbai.py`](code_reference/scripts/download_mxbai.py.md) | Provides the operational or development utility named download mxbai. | 9 |
| [`scripts/generate_code_documentation.py`](code_reference/scripts/generate_code_documentation.py.md) | Provides the operational or development utility named generate code documentation. | 375 |
| [`scripts/install.ps1`](code_reference/scripts/install.ps1.md) | Runs verified one-click Windows installation, including package checksums, Python/venv setup, dependencies, model verification, folders, shortcuts, and final health checks. | 369 |
| [`scripts/reset_data.py`](code_reference/scripts/reset_data.py.md) | Provides the operational or development utility named reset data. | 124 |
| [`scripts/run_bias_testbench.py`](code_reference/scripts/run_bias_testbench.py.md) | Supports repeatable development testbench execution and produces auditable local test data or reports. | 266 |
| [`scripts/run_preferred_work_edge_case_audit.py`](code_reference/scripts/run_preferred_work_edge_case_audit.py.md) | Supports repeatable development testbench execution and produces auditable local test data or reports. | 142 |
| [`scripts/run_search_testbench.py`](code_reference/scripts/run_search_testbench.py.md) | Supports repeatable development testbench execution and produces auditable local test data or reports. | 546 |
| [`scripts/run_testbench.py`](code_reference/scripts/run_testbench.py.md) | Supports repeatable development testbench execution and produces auditable local test data or reports. | 244 |
| [`scripts/uninstall.ps1`](code_reference/scripts/uninstall.ps1.md) | Removes WSP shortcuts and application files safely, with an option to preserve operational data in a timestamped Documents folder. | 65 |
| [`scripts/verify_install.py`](code_reference/scripts/verify_install.py.md) | Verifies required modules, writable data paths, SQLite initialization, application routes, and offline embedding generation. | 82 |

## `services`

| Source file | Responsibility | Lines |
|---|---|---:|
| [`services/__init__.py`](code_reference/services/__init__.py.md) | Implements the   init   service used by the local WSP application. | 3 |
| [`services/analytics_service.py`](code_reference/services/analytics_service.py.md) | Calculates dashboard metrics, chart series, latest-import summaries, and text-frequency analytics from current records. | 391 |
| [`services/archive_service.py`](code_reference/services/archive_service.py.md) | Copies source workbooks into the protected archive and creates pending import-batch records before database changes. | 110 |
| [`services/backup_service.py`](code_reference/services/backup_service.py.md) | Creates timestamped SQLite backups, verifies integrity, records backup metadata, and applies retention policy. | 239 |
| [`services/chat_orchestrator.py`](code_reference/services/chat_orchestrator.py.md) | Implements the chat orchestrator service used by the local WSP application. | 53 |
| [`services/dashboard_intelligence_service.py`](code_reference/services/dashboard_intelligence_service.py.md) | Builds the placement-focused dashboard model, faculty mappings, worklists, comparison signals, data-quality views, and chart-ready summaries. | 758 |
| [`services/embedding_service.py`](code_reference/services/embedding_service.py.md) | Loads the local Sentence Transformer model, prepares model-specific query/document text, normalizes vectors, and verifies offline cache availability. | 159 |
| [`services/excel_importer.py`](code_reference/services/excel_importer.py.md) | Reads Excel workbooks, rejects unsafe inputs, detects duplicates, merges current students, retains history, and logs transactional import results. | 533 |
| [`services/excel_schema.py`](code_reference/services/excel_schema.py.md) | Defines supported workbook formats and canonical header normalization rules. | 199 |
| [`services/explanation_service.py`](code_reference/services/explanation_service.py.md) | Turns semantic similarities and original student evidence into short administrator-facing match explanations. | 61 |
| [`services/export_service.py`](code_reference/services/export_service.py.md) | Writes filtered student results and filter metadata into timestamped multi-sheet Excel workbooks and logs exports. | 157 |
| [`services/filter_service.py`](code_reference/services/filter_service.py.md) | Validates filter requests, composes SQLAlchemy predicates, applies semantic ranking, sorts/paginates results, and stores filter audit records. | 613 |
| [`services/folder_watcher.py`](code_reference/services/folder_watcher.py.md) | Monitors the configured Import Folder and invokes the import callback for stable supported workbook files. | 3 |
| [`services/logging_service.py`](code_reference/services/logging_service.py.md) | Configures local rotating application logs and structured operational logging. | 3 |
| [`services/preferred_work_grouping_service.py`](code_reference/services/preferred_work_grouping_service.py.md) | Groups free-text work preferences into reviewed, flexible, emerging, or needs-review topics while preserving original responses. | 431 |
| [`services/semantic_document_service.py`](code_reference/services/semantic_document_service.py.md) | Builds deterministic original-text semantic profiles and hashes from student fields used by local matching. | 201 |
| [`services/semantic_search_service.py`](code_reference/services/semantic_search_service.py.md) | Synchronizes the FAISS student index, ranks embedding matches, cites original-text evidence, manages index freshness, and provides fallbacks. | 604 |
| [`services/semantic_service.py`](code_reference/services/semantic_service.py.md) | Provides lexical semantic fallbacks, optional local Ollama integration, prompt parsing, and model-availability reporting. | 888 |
| [`services/student_profile_service.py`](code_reference/services/student_profile_service.py.md) | Assembles the holistic student profile payload from current data, retained history, support flags, skills, and extra workbook columns. | 335 |
| [`services/technical_skill_grouping_service.py`](code_reference/services/technical_skill_grouping_service.py.md) | Splits and semantically groups rough technical-skill text into stable, emerging, or unverified topics without rewriting source data. | 307 |
| [`services/value_normalizer.py`](code_reference/services/value_normalizer.py.md) | Normalizes booleans, numbers, dates, text, email, and phone values while recording non-fatal validation warnings. | 178 |
| [`services/vector_store_service.py`](code_reference/services/vector_store_service.py.md) | Persists normalized vectors and metadata, maintains an in-process cache, and performs candidate-restricted cosine-similarity search. | 234 |

## `tests`

| Source file | Responsibility | Lines |
|---|---|---:|
| [`tests/conftest.py`](code_reference/tests/conftest.py.md) | Defines shared pytest fixtures and reusable test data used across the automated verification suite. | 64 |
| [`tests/test_analytics_service.py`](code_reference/tests/test_analytics_service.py.md) | Provides regression coverage for analytics service, including expected success paths, validation rules, and failure behavior. | 510 |
| [`tests/test_archive_service.py`](code_reference/tests/test_archive_service.py.md) | Provides regression coverage for archive service, including expected success paths, validation rules, and failure behavior. | 121 |
| [`tests/test_backup_service.py`](code_reference/tests/test_backup_service.py.md) | Provides regression coverage for backup service, including expected success paths, validation rules, and failure behavior. | 275 |
| [`tests/test_config.py`](code_reference/tests/test_config.py.md) | Provides regression coverage for config, including expected success paths, validation rules, and failure behavior. | 108 |
| [`tests/test_dashboard_intelligence_service.py`](code_reference/tests/test_dashboard_intelligence_service.py.md) | Provides regression coverage for dashboard intelligence service, including expected success paths, validation rules, and failure behavior. | 266 |
| [`tests/test_dashboard_page.py`](code_reference/tests/test_dashboard_page.py.md) | Provides regression coverage for dashboard page, including expected success paths, validation rules, and failure behavior. | 155 |
| [`tests/test_database.py`](code_reference/tests/test_database.py.md) | Provides regression coverage for database, including expected success paths, validation rules, and failure behavior. | 353 |
| [`tests/test_embedding_service.py`](code_reference/tests/test_embedding_service.py.md) | Provides regression coverage for embedding service, including expected success paths, validation rules, and failure behavior. | 37 |
| [`tests/test_excel_importer.py`](code_reference/tests/test_excel_importer.py.md) | Provides regression coverage for excel importer, including expected success paths, validation rules, and failure behavior. | 640 |
| [`tests/test_excel_schema.py`](code_reference/tests/test_excel_schema.py.md) | Provides regression coverage for excel schema, including expected success paths, validation rules, and failure behavior. | 155 |
| [`tests/test_export_service.py`](code_reference/tests/test_export_service.py.md) | Provides regression coverage for export service, including expected success paths, validation rules, and failure behavior. | 327 |
| [`tests/test_filter_page_components.py`](code_reference/tests/test_filter_page_components.py.md) | Provides regression coverage for filter page components, including expected success paths, validation rules, and failure behavior. | 136 |
| [`tests/test_filter_service.py`](code_reference/tests/test_filter_service.py.md) | Provides regression coverage for filter service, including expected success paths, validation rules, and failure behavior. | 1,130 |
| [`tests/test_main.py`](code_reference/tests/test_main.py.md) | Provides regression coverage for main, including expected success paths, validation rules, and failure behavior. | 20 |
| [`tests/test_preferred_work_grouping_service.py`](code_reference/tests/test_preferred_work_grouping_service.py.md) | Provides regression coverage for preferred work grouping service, including expected success paths, validation rules, and failure behavior. | 130 |
| [`tests/test_project_structure.py`](code_reference/tests/test_project_structure.py.md) | Provides regression coverage for project structure, including expected success paths, validation rules, and failure behavior. | 45 |
| [`tests/test_schema_manager.py`](code_reference/tests/test_schema_manager.py.md) | Provides regression coverage for schema manager, including expected success paths, validation rules, and failure behavior. | 145 |
| [`tests/test_semantic_document_service.py`](code_reference/tests/test_semantic_document_service.py.md) | Provides regression coverage for semantic document service, including expected success paths, validation rules, and failure behavior. | 86 |
| [`tests/test_semantic_search_service.py`](code_reference/tests/test_semantic_search_service.py.md) | Provides regression coverage for semantic search service, including expected success paths, validation rules, and failure behavior. | 352 |
| [`tests/test_semantic_service.py`](code_reference/tests/test_semantic_service.py.md) | Provides regression coverage for semantic service, including expected success paths, validation rules, and failure behavior. | 668 |
| [`tests/test_technical_skill_grouping_service.py`](code_reference/tests/test_technical_skill_grouping_service.py.md) | Provides regression coverage for technical skill grouping service, including expected success paths, validation rules, and failure behavior. | 102 |
| [`tests/test_ui_layout.py`](code_reference/tests/test_ui_layout.py.md) | Provides regression coverage for ui layout, including expected success paths, validation rules, and failure behavior. | 165 |
| [`tests/test_value_normalizer.py`](code_reference/tests/test_value_normalizer.py.md) | Provides regression coverage for value normalizer, including expected success paths, validation rules, and failure behavior. | 101 |
| [`tests/test_vector_store_service.py`](code_reference/tests/test_vector_store_service.py.md) | Provides regression coverage for vector store service, including expected success paths, validation rules, and failure behavior. | 72 |
| [`tests/test_web_app.py`](code_reference/tests/test_web_app.py.md) | Provides regression coverage for web app, including expected success paths, validation rules, and failure behavior. | 530 |

## `version.txt`

| Source file | Responsibility | Lines |
|---|---|---:|
| [`version.txt`](code_reference/version.txt.md) | Supports the WSP Offline System as the repository artifact `version.txt`. | 2 |

## `wsp_launcher.pyw`

| Source file | Responsibility | Lines |
|---|---|---:|
| [`wsp_launcher.pyw`](code_reference/wsp_launcher.pyw.md) | Provides the Windows desktop/tray launch experience, single-instance behavior, browser opening, process logging, and graceful shutdown controls. | 220 |
