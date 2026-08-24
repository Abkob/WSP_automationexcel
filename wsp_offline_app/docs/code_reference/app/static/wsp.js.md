# `app/static/wsp.js`

[Open source](../../../../app/static/wsp.js) · [Code documentation index](../../../CODE_REFERENCE.md) · [Feature and code flows](../../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Implements all browser-side interaction: dashboard navigation, filtering, saved preferences, semantic-search progress, data editing, profile navigation, import operations, backup restore, and diagnostics.

## File facts

- **Type:** `.js`
- **Size:** 3,140 lines
- **Layer:** `app`

## Dependencies and integration

- `localStorage`
- `fetch`
- `Chart`
- `FormData`
- `history`
- `navigator.clipboard`

### Routes or endpoints

- `/api/admin/index-status`
- `/api/admin/reindex?force=true`
- `/api/backup/restore`
- `/api/backups`
- `/api/dashboard?${query.toString()}`
- `/api/excel-sheets`
- `/api/export`
- `/api/filter-options`
- `/api/import-center`
- `/api/import-folder`
- `/api/import/refresh-folder`
- `/api/import/run`
- `/api/search`
- `/api/shutdown`
- `/api/students/${encodeURIComponent(String(studentId))}/profile`
- `/api/students/lookup?limit=5`
- `/api/students/lookup?q=${encodeURIComponent(String(query || `
- `/api/students/update`
- `/api/system-status`
- `/api/system-status/diagnostics/checks`
- `/api/system-status/diagnostics/single`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 4 | function | `saveFilterPrefs()` | Browser-side interaction or rendering function. |
| 10 | function | `loadFilterPrefs()` | Browser-side interaction or rendering function. |
| 46 | function | `clearFilterPrefs()` | Browser-side interaction or rendering function. |
| 51 | function | `getSavedPrefs()` | Browser-side interaction or rendering function. |
| 57 | function | `flashPrefsSaved()` | Browser-side interaction or rendering function. |
| 66 | function | `flashPrefsCleared()` | Browser-side interaction or rendering function. |
| 75 | function | `buildPrefsSummary(prefs)` | Browser-side interaction or rendering function. |
| 336 | function | `refreshActiveView()` | Browser-side interaction or rendering function. |
| 345 | function | `loadDashboard()` | Browser-side interaction or rendering function. |
| 372 | function | `initDashboardControls()` | Browser-side interaction or rendering function. |
| 419 | function | `splitDashboardFilterValue(value)` | Browser-side interaction or rendering function. |
| 423 | function | `initDashboardMultiSelect(key, onChange)` | Browser-side interaction or rendering function. |
| 514 | function | `getDashboardMultiValues(key)` | Browser-side interaction or rendering function. |
| 518 | function | `setDashboardMultiValues(key, values, notify = false)` | Browser-side interaction or rendering function. |
| 522 | function | `setDashboardMultiOptions(key, options, preferredValues = null)` | Browser-side interaction or rendering function. |
| 526 | function | `collectDashboardFilters()` | Browser-side interaction or rendering function. |
| 539 | function | `populateDashboardFilters(data)` | Browser-side interaction or rendering function. |
| 554 | function | `updateDashboardMajorOptions(preferredValues = null)` | Browser-side interaction or rendering function. |
| 566 | function | `clearDashboardFilters()` | Browser-side interaction or rendering function. |
| 575 | function | `syncDashboardUrl()` | Browser-side interaction or rendering function. |
| 583 | function | `renderDashboardSelection(data)` | Browser-side interaction or rendering function. |
| 587 | function | `renderDashboardFilterChips(selection)` | Browser-side interaction or rendering function. |
| 616 | function | `renderDashboardActiveView()` | Browser-side interaction or rendering function. |
| 635 | function | `renderDashboardOverview(target, data)` | Browser-side interaction or rendering function. |
| 659 | function | `renderDashboardAcademics(target, data)` | Browser-side interaction or rendering function. |
| 683 | function | `renderDashboardWorkStudy(target, data)` | Browser-side interaction or rendering function. |
| 721 | function | `renderDashboardSupport(target, data)` | Browser-side interaction or rendering function. |
| 745 | function | `renderDashboardQuality(target, data)` | Browser-side interaction or rendering function. |
| 783 | function | `renderDashboardKpis(items)` | Browser-side interaction or rendering function. |
| 793 | function | `renderDashboardSignalBoard(title, eyebrow, rawPoints, unit = "candidates", limit = 6)` | Browser-side interaction or rendering function. |
| 806 | function | `renderDashboardFacultyComparison(data)` | Browser-side interaction or rendering function. |
| 826 | function | `renderDashboardStudentPanel(data, title, description, mode = "status", selectedRows = null, emptyText = "No students match this view.")` | Browser-side interaction or rendering function. |
| 855 | function | `dashboardSectionHead(title, description, label)` | Browser-side interaction or rendering function. |
| 859 | function | `bindDashboardInteractions(root)` | Browser-side interaction or rendering function. |
| 869 | function | `handleDashboardAction(action)` | Browser-side interaction or rendering function. |
| 882 | function | `applyDashboardFilter(key, value)` | Browser-side interaction or rendering function. |
| 899 | function | `handleDashboardChartSelection(filterKey, value)` | Browser-side interaction or rendering function. |
| 903 | function | `metricNumber(value, decimals = 0)` | Browser-side interaction or rendering function. |
| 908 | function | `numberPercent(value)` | Browser-side interaction or rendering function. |
| 912 | function | `loadFilterOptions()` | Browser-side interaction or rendering function. |
| 922 | function | `refreshIndexCoverage()` | Browser-side interaction or rendering function. |
| 977 | function | `triggerReindex()` | Browser-side interaction or rendering function. |
| 994 | function | `startSearchProgress(usesSemanticSearch)` | Browser-side interaction or rendering function. |
| 1029 | function | `finishSearchProgress(message, failed = false)` | Browser-side interaction or rendering function. |
| 1048 | function | `runSearch()` | Browser-side interaction or rendering function. |
| 1084 | function | `exportResults()` | Browser-side interaction or rendering function. |
| 1100 | function | `loadExcelSheets()` | Browser-side interaction or rendering function. |
| 1112 | function | `renderSheetSourceMap(items)` | Browser-side interaction or rendering function. |
| 1124 | function | `renderSheetTabs()` | Browser-side interaction or rendering function. |
| 1151 | function | `renderSheetsGlobalSearch()` | Browser-side interaction or rendering function. |
| 1224 | function | `renderActiveSheetWithQuery(globalQuery)` | Browser-side interaction or rendering function. |
| 1264 | function | `renderActiveSheet()` | Browser-side interaction or rendering function. |
| 1352 | function | `renderSummaryEditCount()` | Browser-side interaction or rendering function. |
| 1360 | function | `cancelSheetEdits()` | Browser-side interaction or rendering function. |
| 1370 | function | `saveSheetEdits()` | Browser-side interaction or rendering function. |
| 1415 | function | `loadBackupVault()` | Browser-side interaction or rendering function. |
| 1428 | function | `renderBackupVault(data)` | Browser-side interaction or rendering function. |
| 1484 | function | `restoreBackup(path, btn)` | Browser-side interaction or rendering function. |
| 1503 | function | `setFormulaPreview(cell)` | Browser-side interaction or rendering function. |
| 1512 | function | `loadImportCenter()` | Browser-side interaction or rendering function. |
| 1518 | function | `renderImportCenter(data)` | Browser-side interaction or rendering function. |
| 1545 | function | `renderImportFolderSummary(folder)` | Browser-side interaction or rendering function. |
| 1568 | function | `renderBackupPolicy(policy)` | Browser-side interaction or rendering function. |
| 1585 | function | `renderPathStack(paths)` | Browser-side interaction or rendering function. |
| 1602 | function | `renderImportPipeline(data)` | Browser-side interaction or rendering function. |
| 1616 | function | `renderPipelineStep(label, detail, state)` | Browser-side interaction or rendering function. |
| 1626 | function | `renderSchemaTable(columns)` | Browser-side interaction or rendering function. |
| 1647 | function | `renderImportConsole(logs)` | Browser-side interaction or rendering function. |
| 1661 | function | `runImportFromPath()` | Browser-side interaction or rendering function. |
| 1692 | function | `renderAutoExportCard()` | Browser-side interaction or rendering function. |
| 1719 | function | `runAutoExport()` | Browser-side interaction or rendering function. |
| 1742 | function | `saveImportFolder()` | Browser-side interaction or rendering function. |
| 1771 | function | `refreshUploadFolder({ automatic })` | Browser-side interaction or rendering function. |
| 1792 | function | `startImportFolderAutoRefresh()` | Browser-side interaction or rendering function. |
| 1800 | function | `loadSystemStatus()` | Browser-side interaction or rendering function. |
| 1806 | function | `renderSystemStatus(data)` | Browser-side interaction or rendering function. |
| 1811 | function | `renderHealthOverview(h)` | Browser-side interaction or rendering function. |
| 1843 | function | `renderSystemInfo(s)` | Browser-side interaction or rendering function. |
| 1894 | function | `initDiagnosticChecks()` | Browser-side interaction or rendering function. |
| 1904 | function | `renderDiagControls()` | Browser-side interaction or rendering function. |
| 1939 | function | `runDiagnostics()` | Browser-side interaction or rendering function. |
| 2013 | function | `renderDiagCard(res)` | Browser-side interaction or rendering function. |
| 2036 | function | `renderDiagSkeleton(n)` | Browser-side interaction or rendering function. |
| 2040 | function | `collectSearchPayload()` | Browser-side interaction or rendering function. |
| 2064 | function | `valueOf(formData, key)` | Browser-side interaction or rendering function. |
| 2068 | function | `renderMetrics(metrics)` | Browser-side interaction or rendering function. |
| 2088 | function | `renderChartGrid(targetId, chartSpecs)` | Browser-side interaction or rendering function. |
| 2112 | function | `normalizeChartSpec(spec)` | Browser-side interaction or rendering function. |
| 2127 | function | `normalizePoints(points)` | Browser-side interaction or rendering function. |
| 2136 | function | `renderChartCard(spec, index)` | Browser-side interaction or rendering function. |
| 2166 | function | `renderSinglePointSpotlight(spec, point, total)` | Browser-side interaction or rendering function. |
| 2188 | function | `initChartJs(canvasId, spec)` | Browser-side interaction or rendering function. |
| 2384 | function | `renderChartStatPill(spec, topPoint, total)` | Browser-side interaction or rendering function. |
| 2397 | function | `chartSummary(spec, visible, allPoints)` | Browser-side interaction or rendering function. |
| 2428 | function | `findTopPoint(points)` | Browser-side interaction or rendering function. |
| 2432 | function | `chartTotal(points, spec)` | Browser-side interaction or rendering function. |
| 2438 | function | `chartColor(index)` | Browser-side interaction or rendering function. |
| 2443 | function | `renderLatestImport(summary)` | Browser-side interaction or rendering function. |
| 2482 | function | `renderResults(rows)` | Browser-side interaction or rendering function. |
| 2510 | function | `renderActiveFilterTags(payload)` | Browser-side interaction or rendering function. |
| 2538 | function | `updateThresholdOutput()` | Browser-side interaction or rendering function. |
| 2550 | function | `initMultiSelect(rootId, allOptions)` | Browser-side interaction or rendering function. |
| 2673 | function | `getMultiSelectValues(rootId)` | Browser-side interaction or rendering function. |
| 2677 | function | `setMultiSelectValues(rootId, values)` | Browser-side interaction or rendering function. |
| 2726 | function | `clearMultiSelect(rootId)` | Browser-side interaction or rendering function. |
| 2730 | function | `fillSelect(name, values)` | Browser-side interaction or rendering function. |
| 2746 | function | `setSearchStatus(value)` | Browser-side interaction or rendering function. |
| 2753 | function | `formatChartValue(value, style = "number")` | Browser-side interaction or rendering function. |
| 2764 | function | `formatPercent(value, total)` | Browser-side interaction or rendering function. |
| 2775 | function | `slugify(value)` | Browser-side interaction or rendering function. |
| 2782 | function | `excelColumnName(index)` | Browser-side interaction or rendering function. |
| 2793 | function | `fileName(path)` | Browser-side interaction or rendering function. |
| 2797 | function | `formatValue(value)` | Browser-side interaction or rendering function. |
| 2804 | function | `escapeHtml(value)` | Browser-side interaction or rendering function. |
| 2813 | function | `highlightText(text, query)` | Browser-side interaction or rendering function. |
| 2835 | function | `initStudentProfilePage()` | Browser-side interaction or rendering function. |
| 2869 | function | `runStudentLookup(query)` | Browser-side interaction or rendering function. |
| 2900 | function | `hideStudentLookup()` | Browser-side interaction or rendering function. |
| 2907 | function | `loadProfileSuggestions()` | Browser-side interaction or rendering function. |
| 2923 | function | `openStudentProfile(studentId)` | Browser-side interaction or rendering function. |
| 2928 | function | `loadStudentProfile(studentId)` | Browser-side interaction or rendering function. |
| 2956 | function | `renderStudentProfile(data)` | Browser-side interaction or rendering function. |
| 3010 | function | `renderProfileGroup(group, title, description)` | Browser-side interaction or rendering function. |
| 3018 | function | `renderProfileField(item)` | Browser-side interaction or rendering function. |
| 3026 | function | `renderSkillsCard(skills)` | Browser-side interaction or rendering function. |
| 3037 | function | `renderSupportCard(items)` | Browser-side interaction or rendering function. |
| 3048 | function | `renderAdditionalFields(items)` | Browser-side interaction or rendering function. |
| 3056 | function | `renderRecordCard(record)` | Browser-side interaction or rendering function. |
| 3069 | function | `renderTimelineCard(items)` | Browser-side interaction or rendering function. |
| 3075 | function | `formatProfileDate(value)` | Browser-side interaction or rendering function. |
| 3082 | function | `profileInitials(name)` | Browser-side interaction or rendering function. |
| 3086 | function | `bindStudentProfileActions(root = document)` | Browser-side interaction or rendering function. |
| 3102 | function | `initStudentContextMenu()` | Browser-side interaction or rendering function. |
| 3126 | function | `showStudentContextMenu(studentId, x, y)` | Browser-side interaction or rendering function. |
| 3136 | function | `hideStudentContextMenu()` | Browser-side interaction or rendering function. |

## Runtime flow

1. The application or development workflow loads `app/static/wsp.js` when its app responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
