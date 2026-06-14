const activePath = document.body.dataset.activePath;
const FILTER_PREFS_KEY = "wsp_filter_prefs_v1";

function saveFilterPrefs() {
  const payload = collectSearchPayload();
  localStorage.setItem(FILTER_PREFS_KEY, JSON.stringify(payload));
  flashPrefsSaved();
}

function loadFilterPrefs() {
  const raw = localStorage.getItem(FILTER_PREFS_KEY);
  if (!raw) return false;
  try {
    const prefs = JSON.parse(raw);
    const form = document.querySelector("#search-form");
    if (!form) return false;
    const set = (name, val) => {
      const el = form.querySelector(`[name="${name}"]`);
      if (el && val !== undefined && val !== "" && val !== null) el.value = val;
    };
    set("semantic_query", prefs.semantic_query);
    set("semantic_threshold", prefs.semantic_threshold);
    set("gpa_min", prefs.gpa_min);
    set("gpa_max", prefs.gpa_max);
    set("probation", prefs.probation);
    set("financial_aid", prefs.financial_aid);
    set("dorms", prefs.dorms);
    if (prefs.majors && prefs.majors.length) setMultiSelectValues("ms-major", prefs.majors);
    if (prefs.classes && prefs.classes.length) setMultiSelectValues("ms-class", prefs.classes);
    set("sort_field", prefs.sort_field);
    set("sort_direction", prefs.sort_direction);
    set("page_size", prefs.page_size);
    set("name_query", prefs.name_query);
    set("technical_skills_query", prefs.technical_skills_query);
    if (prefs.include_missing) {
      const cb = form.querySelector("[name='include_missing']");
      if (cb) cb.checked = true;
    }
    const gi = document.querySelector("#global-search-input");
    if (gi && prefs.global_query) gi.value = prefs.global_query;
    updateThresholdOutput();
    return true;
  } catch (_) { return false; }
}

function clearFilterPrefs() {
  localStorage.removeItem(FILTER_PREFS_KEY);
  flashPrefsCleared();
}

function getSavedPrefs() {
  const raw = localStorage.getItem(FILTER_PREFS_KEY);
  if (!raw) return null;
  try { return JSON.parse(raw); } catch (_) { return null; }
}

function flashPrefsSaved() {
  const el = document.querySelector("#prefs-badge");
  if (!el) return;
  el.textContent = "✓ Preferences saved";
  el.className = "prefs-badge saved visible";
  clearTimeout(el._timer);
  el._timer = setTimeout(() => el.classList.remove("visible"), 2200);
}

function flashPrefsCleared() {
  const el = document.querySelector("#prefs-badge");
  if (!el) return;
  el.textContent = "Preferences cleared";
  el.className = "prefs-badge cleared visible";
  clearTimeout(el._timer);
  el._timer = setTimeout(() => el.classList.remove("visible"), 2200);
}

function buildPrefsSummary(prefs) {
  if (!prefs) return "No saved preferences.";
  const parts = [];
  if (prefs.gpa_min) parts.push(`GPA ≥ ${prefs.gpa_min}`);
  if (prefs.gpa_max) parts.push(`GPA ≤ ${prefs.gpa_max}`);
  if (prefs.majors && prefs.majors.length) parts.push(`Major: ${prefs.majors.join(", ")}`);
  if (prefs.classes && prefs.classes.length) parts.push(`Class: ${prefs.classes.join(", ")}`);
  if (prefs.probation && prefs.probation !== "any") parts.push(`Probation: ${prefs.probation}`);
  if (prefs.financial_aid && prefs.financial_aid !== "any") parts.push(`Aid: ${prefs.financial_aid}`);
  if (prefs.dorms && prefs.dorms !== "any") parts.push(`Dorms: ${prefs.dorms}`);
  if (prefs.semantic_query) parts.push(`AI query: "${prefs.semantic_query}"`);
  if (prefs.global_query) parts.push(`Search: "${prefs.global_query}"`);
  if (prefs.name_query) parts.push(`Name: ${prefs.name_query}`);
  if (prefs.technical_skills_query) parts.push(`Skills: ${prefs.technical_skills_query}`);
  if (prefs.page_size) parts.push(`Top ${prefs.page_size} results`);
  return parts.length ? parts.join(" · ") : "All students (no filters)";
}

document.addEventListener("DOMContentLoaded", () => {
  if (activePath === "/") {
    loadDashboard();
  }
  if (activePath === "/filters") {
    loadFilterOptions().then(() => {
      const restored = loadFilterPrefs();
      runSearch();
      if (restored) {
        const badge = document.querySelector("#prefs-badge");
        if (badge) {
          badge.textContent = "✓ Preferences restored";
          badge.className = "prefs-badge saved visible";
          badge._timer = setTimeout(() => badge.classList.remove("visible"), 3000);
        }
      }
    });
    refreshIndexCoverage();
  }
  if (activePath === "/excel-sheets") {
    loadExcelSheets();
  }
  if (activePath === "/import") {
    loadImportCenter();
    loadBackupVault();
    startImportFolderAutoRefresh();
    refreshIndexCoverage();
    const reindexBtn = document.getElementById("index-reindex-btn");
    if (reindexBtn) reindexBtn.addEventListener("click", triggerReindex);
  }
  if (activePath === "/system-status") {
    loadSystemStatus();
    initDiagnosticChecks();
  }

  const refreshButton = document.querySelector("#refresh-dashboard");
  if (refreshButton) {
    refreshButton.addEventListener("click", refreshActiveView);
  }

  const exitBtn = document.querySelector("#app-exit-btn");
  if (exitBtn) {
    exitBtn.addEventListener("click", async () => {
      if (!confirm("Close WSP Offline System?\n\nThe server will stop and this window can be closed.")) return;
      exitBtn.textContent = "Closing…";
      exitBtn.disabled = true;
      try {
        await fetch("/api/shutdown", { method: "POST" });
      } catch (_) { /* server dropped the connection — expected */ }
      document.body.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:center;height:100vh;
                    font-family:system-ui,sans-serif;flex-direction:column;gap:16px;color:#475569;">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5">
            <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2z"/>
            <line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <p style="font-size:18px;font-weight:600;margin:0;">WSP Offline System has stopped.</p>
          <p style="margin:0;color:#94a3b8;">You can close this window.</p>
        </div>`;
    });
  }

  const form = document.querySelector("#search-form");
  if (form) {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      runSearch();
    });
    let autoSaveTimer = null;
    form.addEventListener("change", () => {
      clearTimeout(autoSaveTimer);
      autoSaveTimer = setTimeout(saveFilterPrefs, 800);
    });
    form.addEventListener("input", () => {
      clearTimeout(autoSaveTimer);
      autoSaveTimer = setTimeout(saveFilterPrefs, 800);
    });
    form.addEventListener("ms-change", () => {
      runSearch();
      saveFilterPrefs();
    });
  }

  const clearPrefsBtn = document.querySelector("#clear-filter-prefs");
  if (clearPrefsBtn) {
    clearPrefsBtn.addEventListener("click", () => { clearFilterPrefs(); });
  }

  const thresholdSlider = document.querySelector('input[name="semantic_threshold"]');
  if (thresholdSlider) {
    thresholdSlider.addEventListener("input", () => updateThresholdOutput());
    updateThresholdOutput();
  }

  const resetButton = document.querySelector("#reset-search");
  if (resetButton) {
    resetButton.addEventListener("click", () => {
      form.reset();
      const globalInput = document.querySelector("#global-search-input");
      if (globalInput) globalInput.value = "";
      clearMultiSelect("ms-major");
      clearMultiSelect("ms-class");
      updateThresholdOutput();
      runSearch();
    });
  }

  const globalSearchInput = document.querySelector("#global-search-input");
  if (globalSearchInput) {
    let globalDebounce = null;
    globalSearchInput.addEventListener("input", () => {
      clearTimeout(globalDebounce);
      globalDebounce = setTimeout(() => { runSearch(); saveFilterPrefs(); }, 280);
    });
  }

  const sheetsGlobalSearch = document.querySelector("#sheets-global-search");
  if (sheetsGlobalSearch) {
    let sheetsDebounce = null;
    sheetsGlobalSearch.addEventListener("input", () => {
      clearTimeout(sheetsDebounce);
      sheetsDebounce = setTimeout(() => renderSheetsGlobalSearch(), 220);
    });
  }

  const exportButton = document.querySelector("#export-results");
  if (exportButton) {
    exportButton.addEventListener("click", exportResults);
  }

  const reportButton = document.querySelector(".report-button");
  if (reportButton) {
    reportButton.addEventListener("click", () => window.print());
  }

  const importCandidateSelect = document.querySelector("#import-candidates");
  if (importCandidateSelect) {
    importCandidateSelect.addEventListener("change", () => {
      const input = document.querySelector("#import-path");
      if (input && importCandidateSelect.value) {
        input.value = importCandidateSelect.value;
      }
    });
  }

  const runImportButton = document.querySelector("#run-import");
  if (runImportButton) {
    runImportButton.addEventListener("click", runImportFromPath);
  }

  const saveImportFolderButton = document.querySelector("#save-import-folder");
  if (saveImportFolderButton) {
    saveImportFolderButton.addEventListener("click", saveImportFolder);
  }

  const openRefreshFolderButton = document.querySelector("#open-refresh-folder");
  if (openRefreshFolderButton) {
    openRefreshFolderButton.addEventListener("click", () => refreshUploadFolder({ automatic: false }));
  }

  const refreshUploadFolderButton = document.querySelector("#refresh-upload-folder");
  if (refreshUploadFolderButton) {
    refreshUploadFolderButton.addEventListener("click", () => refreshUploadFolder({ automatic: false }));
  }

  const refreshImportButton = document.querySelector("#refresh-import");
  if (refreshImportButton) {
    refreshImportButton.addEventListener("click", loadImportCenter);
  }

  const sheetSearch = document.querySelector("#sheet-search");
  if (sheetSearch) {
    sheetSearch.addEventListener("input", () => renderActiveSheet());
  }

  const editToggleBtn = document.querySelector("#sheet-edit-toggle");
  if (editToggleBtn) {
    editToggleBtn.addEventListener("click", () => {
      if (sheetState.editMode) {
        cancelSheetEdits();
      } else {
        sheetState.editMode = true;
        sheetState.pendingEdits = {};
        editToggleBtn.textContent = "Exit Edit";
        editToggleBtn.classList.add("active-edit");
        const banner = document.querySelector("#sheet-edit-banner");
        if (banner) banner.hidden = false;
        renderActiveSheet();
      }
    });
  }

  const saveEditsBtn = document.querySelector("#sheet-save-edits");
  if (saveEditsBtn) saveEditsBtn.addEventListener("click", saveSheetEdits);

  const cancelEditsBtn = document.querySelector("#sheet-cancel-edits");
  if (cancelEditsBtn) cancelEditsBtn.addEventListener("click", cancelSheetEdits);

  const refreshBackupsBtn = document.querySelector("#refresh-backups");
  if (refreshBackupsBtn) refreshBackupsBtn.addEventListener("click", loadBackupVault);

  const refreshSystemStatusButton = document.querySelector("#refresh-system-status");
  if (refreshSystemStatusButton) {
    refreshSystemStatusButton.addEventListener("click", loadSystemStatus);
  }

  const runDiagBtn = document.querySelector("#run-diagnostics-btn");
  if (runDiagBtn) {
    runDiagBtn.addEventListener("click", runDiagnostics);
  }

});

let sheetState = {
  sheets: [],
  activeKey: "",
  editMode: false,
  pendingEdits: {},  // { "rowIndex:colIndex": newValue }
};
let importAutoRefreshTimer = null;

// Column index → model field name for Current Students sheet
const STUDENT_EDITABLE_COLS = { 1: "STUD_NAME", 2: "MAJR_DESC", 3: "CLAS_DESC", 4: "CUM_GPA", 7: "STUD_EMAIL", 8: "FINANCIAL_AID", 9: "PROBATION", 10: "DORMS" };
const STUDENT_BOOL_COLS = new Set([8, 9, 10]);
const STUDENT_NUMERIC_COLS = new Set([4]);
const _chartInstances = {};

function refreshActiveView() {
  if (activePath === "/") loadDashboard();
  if (activePath === "/filters") runSearch();
  if (activePath === "/excel-sheets") loadExcelSheets();
  if (activePath === "/import") loadImportCenter();
  if (activePath === "/system-status") loadSystemStatus();
}

async function loadDashboard() {
  const response = await fetch("/api/dashboard");
  const data = await response.json();
  renderMetrics(data.metrics);
  renderLatestImport(data.latest_import);
  renderChartGrid("structured-charts", [
    { title: "Students by major",   type: "ranked-bars", points: data.charts.students_by_major,    unit: "students", limit: 8 },
    { title: "GPA distribution",    type: "histogram",   points: data.charts.gpa_distribution,      unit: "students", limit: 5 },
    { title: "Avg GPA by major",    type: "score-bars",  points: data.charts.average_gpa_by_major,  unit: "avg GPA",  limit: 6 },
    { title: "Probation by major",  type: "alert-bars",  points: data.charts.probation_by_major,    unit: "students", limit: 6 },
  ]);
}

async function loadFilterOptions() {
  const response = await fetch("/api/filter-options");
  const data = await response.json();
  initMultiSelect("ms-major", data.majors);
  initMultiSelect("ms-class", data.classes);
}

// ── index coverage indicator ──────────────────────────────────────────────────
let _coveragePoller = null;

async function refreshIndexCoverage() {
  const badge = document.getElementById("index-coverage-badge");
  const msg   = document.getElementById("index-reindex-msg");
  const btn   = document.getElementById("index-reindex-btn");
  const bar   = document.getElementById("index-coverage-bar");
  if (!badge) return;

  let data;
  try {
    const r = await fetch("/api/admin/index-status");
    data = await r.json();
  } catch (_) { return; }

  const { index_count, db_count, coverage_pct, reindex_running } = data;

  if (bar) bar.style.width = coverage_pct + "%";

  if (reindex_running) {
    badge.textContent = "Building " + coverage_pct + "%";
    badge.className = "index-coverage-badge building";
    if (msg) msg.textContent = "Indexing: " + index_count + " / " + db_count + " students encoded";
    if (btn) { btn.style.display = "none"; }
    if (bar) bar.className = "semantic-index-bar building";
    clearTimeout(_coveragePoller);
    _coveragePoller = setTimeout(refreshIndexCoverage, 4000);
    return;
  }

  if (coverage_pct >= 100) {
    badge.textContent = index_count + " students indexed";
    badge.className = "index-coverage-badge good";
    if (msg) msg.textContent = "AI search covers all " + db_count + " students.";
    if (btn) btn.style.display = "none";
    if (bar) bar.className = "semantic-index-bar good";
    clearTimeout(_coveragePoller);
    _coveragePoller = setTimeout(refreshIndexCoverage, 30000);
  } else if (coverage_pct >= 50) {
    badge.textContent = coverage_pct + "% indexed";
    badge.className = "index-coverage-badge warn";
    if (msg) msg.textContent = "Only " + index_count + " of " + db_count + " students indexed. Results may be biased.";
    if (btn) { btn.style.display = ""; btn.disabled = false; btn.textContent = "Rebuild Index"; }
    if (bar) bar.className = "semantic-index-bar warn";
    clearTimeout(_coveragePoller);
    _coveragePoller = setTimeout(refreshIndexCoverage, 8000);
  } else {
    badge.textContent = coverage_pct + "% — incomplete";
    badge.className = "index-coverage-badge danger";
    if (msg) msg.textContent = "Only " + index_count + " of " + db_count + " students are indexed. AI search is biased.";
    if (btn) { btn.style.display = ""; btn.disabled = false; btn.textContent = "Rebuild Now"; }
    if (bar) bar.className = "semantic-index-bar danger";
    clearTimeout(_coveragePoller);
    _coveragePoller = setTimeout(refreshIndexCoverage, 8000);
  }
}

async function triggerReindex() {
  const btn = document.getElementById("index-reindex-btn");
  const badge = document.getElementById("index-coverage-badge");
  if (btn) { btn.disabled = true; btn.textContent = "Starting..."; }
  if (badge) { badge.textContent = "Starting..."; badge.className = "index-coverage-badge building"; }
  try {
    await fetch("/api/admin/reindex", { method: "POST" });
  } catch (_) { /* server will reindex anyway */ }
  clearTimeout(_coveragePoller);
  _coveragePoller = setTimeout(refreshIndexCoverage, 2000);
}

async function runSearch() {
  const payload = collectSearchPayload();
  const started = performance.now();
  setSearchStatus("Searching");
  const response = await fetch("/api/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    setSearchStatus("Search failed");
    throw new Error(await response.text());
  }
  const data = await response.json();
  const elapsed = ((performance.now() - started) / 1000).toFixed(2);
  renderResults(data.rows);
  renderActiveFilterTags(payload);
  document.querySelector("#result-count").textContent = `${data.total_count.toLocaleString()} results`;
  setSearchStatus(`${elapsed}s`);
  document.querySelector("#export-status").textContent = "";
}

async function exportResults() {
  const status = document.querySelector("#export-status");
  status.textContent = "Exporting...";
  const response = await fetch("/api/export", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(collectSearchPayload()),
  });
  if (!response.ok) {
    status.textContent = "Export failed.";
    return;
  }
  const data = await response.json();
  status.textContent = `Exported ${data.row_count.toLocaleString()} rows to ${data.path}`;
}

async function loadExcelSheets() {
  const response = await fetch("/api/excel-sheets");
  const data = await response.json();
  renderSheetSourceMap(data.source_map || []);
  sheetState.sheets = data.sheets || [];
  sheetState.activeKey = sheetState.activeKey || sheetState.sheets[0]?.key || "";
  renderSheetTabs();
  renderActiveSheet();
  const editToggle = document.querySelector("#sheet-edit-toggle");
  if (editToggle) editToggle.hidden = sheetState.activeKey !== "Student_Directory";
}

function renderSheetSourceMap(items) {
  const target = document.querySelector("#sheet-source-map");
  if (!target) return;
  target.innerHTML = items.map((item) => `
    <article class="source-card">
      <span>${escapeHtml(item.label)}</span>
      <strong>${escapeHtml(item.value)}</strong>
      <p>${escapeHtml(item.detail)}</p>
    </article>
  `).join("");
}

function renderSheetTabs() {
  const tabs = document.querySelector("#sheet-tabs");
  if (!tabs) return;
  tabs.innerHTML = sheetState.sheets.map((sheet) => `
    <button class="sheet-tab ${sheet.key === sheetState.activeKey ? "active" : ""}" type="button" role="tab" aria-selected="${sheet.key === sheetState.activeKey}" data-sheet-key="${escapeHtml(sheet.key)}">
      <span>${escapeHtml(sheet.label)}</span>
      <small>${escapeHtml(sheet.description)}</small>
    </button>
  `).join("");
  tabs.querySelectorAll("[data-sheet-key]").forEach((button) => {
    button.addEventListener("click", () => {
      if (sheetState.editMode) cancelSheetEdits();
      sheetState.activeKey = button.dataset.sheetKey;
      const globalInput = document.querySelector("#sheets-global-search");
      const editToggle = document.querySelector("#sheet-edit-toggle");
      if (editToggle) editToggle.hidden = sheetState.activeKey !== "Student_Directory";
      if (globalInput && globalInput.value.trim()) {
        renderSheetsGlobalSearch();
      } else {
        if (globalInput) globalInput.value = "";
        renderSheetTabs();
        renderActiveSheet();
      }
    });
  });
}

function renderSheetsGlobalSearch() {
  const input = document.querySelector("#sheets-global-search");
  const resultsEl = document.querySelector("#sheets-global-results");
  const workspaceEl = document.querySelector(".sheet-workspace");
  if (!input || !resultsEl || !workspaceEl) return;

  const query = input.value.trim().toLowerCase();

  // Clear the banner and always keep the workspace visible
  resultsEl.hidden = true;
  workspaceEl.hidden = false;

  if (!query) {
    // Restore normal sheet render without any filter
    renderSheetTabs();
    renderActiveSheet();
    return;
  }

  // Count matches per sheet so tabs can show badge counts
  const matchCounts = {};
  for (const sheet of sheetState.sheets) {
    let count = 0;
    for (const row of (sheet.rows || [])) {
      if ((row || []).some((cell) => String(cell ?? "").toLowerCase().includes(query))) count++;
    }
    matchCounts[sheet.key] = count;
  }

  const totalMatches = Object.values(matchCounts).reduce((a, b) => a + b, 0);

  // If current sheet has 0 matches, switch to the first sheet that does
  if (matchCounts[sheetState.activeKey] === 0) {
    const firstHit = sheetState.sheets.find((s) => matchCounts[s.key] > 0);
    if (firstHit) sheetState.activeKey = firstHit.key;
  }

  // Show match counts on tabs
  const tabs = document.querySelector("#sheet-tabs");
  if (tabs) {
    tabs.innerHTML = sheetState.sheets.map((sheet) => {
      const n = matchCounts[sheet.key] || 0;
      const badge = n > 0 ? `<em class="sheet-tab-badge">${n}</em>` : "";
      return `<button class="sheet-tab ${sheet.key === sheetState.activeKey ? "active" : ""}" type="button" role="tab" aria-selected="${sheet.key === sheetState.activeKey}" data-sheet-key="${escapeHtml(sheet.key)}">
        <span>${escapeHtml(sheet.label)}${badge}</span>
        <small>${escapeHtml(sheet.description)}</small>
      </button>`;
    }).join("");
    tabs.querySelectorAll("[data-sheet-key]").forEach((button) => {
      button.addEventListener("click", () => {
        sheetState.activeKey = button.dataset.sheetKey;
        renderSheetsGlobalSearch();
      });
    });
  }

  // Show banner above table
  if (totalMatches > 0) {
    const sheetMatches = matchCounts[sheetState.activeKey] || 0;
    resultsEl.innerHTML = `<div class="global-results-banner">
      Showing <strong>${sheetMatches.toLocaleString()}</strong> matching row${sheetMatches !== 1 ? "s" : ""} on this sheet
      — <strong>${totalMatches.toLocaleString()}</strong> total across all sheets
    </div>`;
    resultsEl.hidden = false;
  } else {
    resultsEl.innerHTML = `<div class="global-results-empty">No results for <strong>${escapeHtml(query)}</strong> across any sheet.</div>`;
    resultsEl.hidden = false;
  }

  // Render the active sheet with the global query as its row filter
  renderActiveSheetWithQuery(query);
}

function renderActiveSheetWithQuery(globalQuery) {
  const sheet = sheetState.sheets.find((item) => item.key === sheetState.activeKey);
  const table = document.querySelector("#sheet-table");
  const summary = document.querySelector("#sheet-summary");
  const status = document.querySelector("#sheet-status");
  if (!sheet || !table || !summary) return;

  const query = globalQuery || "";
  const allRows = sheet.rows || [];
  const rows = allRows.filter((row) => !query || row.some((cell) => String(cell ?? "").toLowerCase().includes(query)));

  summary.innerHTML = `
    <article><strong>${rows.length.toLocaleString()}</strong><span>matching rows</span></article>
    <article><strong>${(sheet.headers || []).length.toLocaleString()}</strong><span>columns</span></article>
    <article><strong>${escapeHtml(sheet.label)}</strong><span>${escapeHtml(sheet.description)}</span></article>
  `;

  table.innerHTML = `
    <thead>
      <tr><th>#</th>${(sheet.headers || []).map((header, index) => `<th><small>COL ${excelColumnName(index)}</small>${escapeHtml(header)}</th>`).join("")}</tr>
    </thead>
    <tbody>
      ${rows.map((row, rowIndex) => {
        const originalRowIndex = allRows.indexOf(row);
        const cells = (sheet.headers || []).map((_, colIndex) => {
          const val = row[colIndex] ?? "";
          return `<td>${highlightText(val, query)}</td>`;
        }).join("");
        return `<tr data-row-index="${rowIndex}"><td>${originalRowIndex + 1}</td>${cells}</tr>`;
      }).join("") || `<tr><td colspan="${(sheet.headers || []).length + 1}" class="empty-state">No rows match <strong>${escapeHtml(query)}</strong>.</td></tr>`}
    </tbody>
  `;
}

function renderActiveSheet() {
  const sheet = sheetState.sheets.find((item) => item.key === sheetState.activeKey);
  const table = document.querySelector("#sheet-table");
  const summary = document.querySelector("#sheet-summary");
  const status = document.querySelector("#sheet-status");
  if (!sheet || !table || !summary || !status) return;

  const isStudentSheet = sheet.key === "Student_Directory";
  const editMode = isStudentSheet && sheetState.editMode;
  const query = String(document.querySelector("#sheet-search")?.value || "").trim().toLowerCase();
  const allRows = sheet.rows || [];
  const rows = allRows.filter((row) => !query || row.some((cell) => String(cell ?? "").toLowerCase().includes(query)));
  const pendingCount = Object.keys(sheetState.pendingEdits).length;

  summary.innerHTML = `
    <article><strong>${rows.length.toLocaleString()}</strong><span>visible rows</span></article>
    <article><strong>${(sheet.headers || []).length.toLocaleString()}</strong><span>columns</span></article>
    <article><strong>${escapeHtml(sheet.label)}</strong><span>${escapeHtml(sheet.description)}</span></article>
    ${editMode && pendingCount ? `<article><strong style="color:var(--aub)">${pendingCount}</strong><span>unsaved change${pendingCount !== 1 ? "s" : ""}</span></article>` : ""}
  `;

  table.innerHTML = `
    <thead>
      <tr><th>#</th>${(sheet.headers || []).map((header, index) => `<th><small>COL ${excelColumnName(index)}</small>${escapeHtml(header)}</th>`).join("")}</tr>
    </thead>
    <tbody>
      ${rows.map((row, rowIndex) => {
        const originalRowIndex = allRows.indexOf(row);
        const cells = (sheet.headers || []).map((_, colIndex) => {
          const editKey = `${originalRowIndex}:${colIndex}`;
          const currentVal = sheetState.pendingEdits[editKey] !== undefined ? sheetState.pendingEdits[editKey] : (row[colIndex] ?? "");
          const hasEdit = sheetState.pendingEdits[editKey] !== undefined;
          const cellId = `${excelColumnName(colIndex)}${rowIndex + 1}`;

          if (editMode && STUDENT_EDITABLE_COLS[colIndex] !== undefined) {
            if (STUDENT_BOOL_COLS.has(colIndex)) {
              return `<td class="${hasEdit ? "cell-edited" : ""}"><select class="edit-cell-select" data-row="${originalRowIndex}" data-col="${colIndex}">
                <option value="" ${currentVal === "" ? "selected" : ""}></option>
                <option value="Yes" ${currentVal === "Yes" ? "selected" : ""}>Yes</option>
                <option value="No" ${currentVal === "No" ? "selected" : ""}>No</option>
              </select></td>`;
            }
            if (STUDENT_NUMERIC_COLS.has(colIndex)) {
              return `<td class="${hasEdit ? "cell-edited" : ""}"><input class="edit-cell-input" type="number" min="0" max="4" step="0.01" data-row="${originalRowIndex}" data-col="${colIndex}" value="${escapeHtml(String(currentVal))}"></td>`;
            }
            return `<td class="${hasEdit ? "cell-edited" : ""}"><input class="edit-cell-input" type="text" data-row="${originalRowIndex}" data-col="${colIndex}" value="${escapeHtml(String(currentVal))}"></td>`;
          }
          return `<td tabindex="0" data-cell="${cellId}" class="${hasEdit ? "cell-edited" : ""}">${highlightText(row[colIndex] ?? "", query)}</td>`;
        }).join("");
        return `<tr data-row-index="${rowIndex}">${`<td>${rowIndex + 1}</td>`}${cells}</tr>`;
      }).join("") || `<tr><td colspan="${(sheet.headers || []).length + 1}" class="empty-state">No sheet rows found.</td></tr>`}
    </tbody>
  `;

  if (editMode) {
    table.querySelectorAll(".edit-cell-input, .edit-cell-select").forEach((input) => {
      input.addEventListener("change", () => {
        const r = Number(input.dataset.row);
        const c = Number(input.dataset.col);
        const orig = allRows[r]?.[c] ?? "";
        if (input.value !== String(orig)) {
          sheetState.pendingEdits[`${r}:${c}`] = input.value;
        } else {
          delete sheetState.pendingEdits[`${r}:${c}`];
        }
        renderSummaryEditCount();
      });
    });
  } else {
    table.querySelectorAll("td[data-cell]").forEach((cell) => {
      cell.addEventListener("click", () => setFormulaPreview(cell));
      cell.addEventListener("focus", () => setFormulaPreview(cell));
    });
  }

  const editCount = Object.keys(sheetState.pendingEdits).length;
  const saveBtn = document.querySelector("#sheet-save-edits");
  if (saveBtn) saveBtn.disabled = editCount === 0;
  status.textContent = editMode
    ? `Edit mode — ${editCount} unsaved change(s). ${rows.length} rows shown.`
    : `${sheet.label}: ${rows.length.toLocaleString()} rows shown from local database.`;
}

function renderSummaryEditCount() {
  const editCount = Object.keys(sheetState.pendingEdits).length;
  const saveBtn = document.querySelector("#sheet-save-edits");
  if (saveBtn) saveBtn.disabled = editCount === 0;
  const status = document.querySelector("#sheet-status");
  if (status) status.textContent = `Edit mode — ${editCount} unsaved change(s).`;
}

function cancelSheetEdits() {
  sheetState.editMode = false;
  sheetState.pendingEdits = {};
  const toggle = document.querySelector("#sheet-edit-toggle");
  if (toggle) { toggle.textContent = "Edit"; toggle.classList.remove("active-edit"); }
  const banner = document.querySelector("#sheet-edit-banner");
  if (banner) banner.hidden = true;
  renderActiveSheet();
}

async function saveSheetEdits() {
  const sheet = sheetState.sheets.find((s) => s.key === "Student_Directory");
  if (!sheet) return;
  const saveBtn = document.querySelector("#sheet-save-edits");
  const status = document.querySelector("#sheet-status");
  if (saveBtn) saveBtn.disabled = true;
  if (status) status.textContent = "Saving…";

  // Group edits by row → build updates per student
  const byRow = {};
  for (const [key, value] of Object.entries(sheetState.pendingEdits)) {
    const [rowStr, colStr] = key.split(":");
    const rowIdx = Number(rowStr);
    const colIdx = Number(colStr);
    const studId = sheet.rows[rowIdx]?.[0];  // column 0 = STUD_ID
    if (!studId) continue;
    if (!byRow[studId]) byRow[studId] = { stud_id: studId, fields: {} };
    const field = STUDENT_EDITABLE_COLS[colIdx];
    if (!field) continue;
    let val = value;
    if (STUDENT_BOOL_COLS.has(colIdx)) val = value === "Yes" ? true : value === "No" ? false : null;
    if (STUDENT_NUMERIC_COLS.has(colIdx)) val = value === "" ? null : Number(value);
    byRow[studId].fields[field] = val;
  }

  const updates = Object.values(byRow).filter((u) => Object.keys(u.fields).length > 0);
  if (!updates.length) { cancelSheetEdits(); return; }

  try {
    const r = await fetch("/api/students/update", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ updates }),
    });
    const data = await r.json();
    if (!r.ok) { if (status) status.textContent = data.detail || "Save failed."; if (saveBtn) saveBtn.disabled = false; return; }
    cancelSheetEdits();
    await loadExcelSheets();
    if (status) status.textContent = `✓ ${data.message}`;
  } catch (err) {
    if (status) status.textContent = `Save error: ${err}`;
    if (saveBtn) saveBtn.disabled = false;
  }
}

async function loadBackupVault() {
  const content = document.querySelector("#backup-vault-content");
  if (!content) return;
  content.innerHTML = `<p style="color:var(--faint);font-size:13px;padding:8px 0">Loading…</p>`;
  try {
    const r = await fetch("/api/backups");
    const data = await r.json();
    renderBackupVault(data);
  } catch (err) {
    if (content) content.innerHTML = `<p style="color:var(--danger)">Failed to load backups: ${escapeHtml(String(err))}</p>`;
  }
}

function renderBackupVault(data) {
  const content = document.querySelector("#backup-vault-content");
  if (!content) return;
  const backups = data.backups || [];
  const archives = data.excel_archives || [];

  const reasonLabel = { pre_import: "Pre-import", post_import: "Post-import", manual_edit: "Manual edit", pre_restore: "Pre-restore" };
  const reasonClass = { pre_import: "reason-pre", post_import: "reason-post", manual_edit: "reason-manual", pre_restore: "reason-restore" };

  const backupRows = backups.length
    ? backups.map((b) => `
      <tr>
        <td>${escapeHtml(b.created_at)}</td>
        <td><span class="backup-reason ${reasonClass[b.reason] || ""}">${escapeHtml(reasonLabel[b.reason] || b.reason)}</span></td>
        <td>${escapeHtml(b.size)}</td>
        <td><span class="table-pill ${b.integrity === true ? "good" : b.integrity === false ? "warn" : ""}">${b.integrity === true ? "OK" : b.integrity === false ? "Warn" : "—"}</span></td>
        <td><button class="restore-btn secondary-button" type="button" data-path="${escapeHtml(b.path)}" style="min-height:28px;padding:0 10px;font-size:11px">Restore</button></td>
      </tr>
    `).join("")
    : `<tr><td colspan="5" class="empty-state">No backups yet — run an import to generate backups.</td></tr>`;

  const archiveSection = archives.length ? `
    <div style="margin-top:18px">
      <div class="section-title" style="margin:0 0 10px">Excel Archive (original workbooks)</div>
      <div class="backup-folder-path">${escapeHtml(data.excel_archive_folder)}</div>
      <div class="compact-table-wrap" style="margin-top:8px">
        <table class="admin-table">
          <thead><tr><th>File</th><th>Size</th><th>Modified</th></tr></thead>
          <tbody>
            ${archives.map((a) => `<tr><td>${escapeHtml(a.filename)}</td><td>${escapeHtml(a.size)}</td><td>${escapeHtml(a.modified_at)}</td></tr>`).join("")}
          </tbody>
        </table>
      </div>
    </div>
  ` : "";

  content.innerHTML = `
    <div class="backup-folder-path" style="margin-bottom:12px">${escapeHtml(data.backup_folder)}</div>
    <div class="compact-table-wrap">
      <table class="admin-table backup-table">
        <thead><tr><th>Timestamp</th><th>Reason</th><th>Size</th><th>Integrity</th><th></th></tr></thead>
        <tbody>${backupRows}</tbody>
      </table>
    </div>
    ${archiveSection}
  `;

  content.querySelectorAll(".restore-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const path = btn.dataset.path;
      if (!confirm(`Restore database from:\n${path}\n\nAn emergency backup of the current database will be created first. Continue?`)) return;
      restoreBackup(path, btn);
    });
  });
}

async function restoreBackup(path, btn) {
  if (btn) btn.disabled = true;
  const content = document.querySelector("#backup-vault-content");
  try {
    const r = await fetch("/api/backup/restore", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ backup_path: path }),
    });
    const data = await r.json();
    if (!r.ok) { alert(data.detail || "Restore failed."); if (btn) btn.disabled = false; return; }
    alert(`✓ ${data.message}\n\nThe page will reload to reflect the restored data.`);
    window.location.reload();
  } catch (err) {
    alert(`Restore failed: ${err}`);
    if (btn) btn.disabled = false;
  }
}

function setFormulaPreview(cell) {
  const label = document.querySelector("#active-cell-label");
  const preview = document.querySelector("#formula-preview");
  document.querySelectorAll("#sheet-table td.is-selected").forEach((item) => item.classList.remove("is-selected"));
  cell.classList.add("is-selected");
  if (label) label.textContent = cell.dataset.cell || "A1";
  if (preview) preview.value = cell.textContent.trim();
}

async function loadImportCenter() {
  const response = await fetch("/api/import-center");
  const data = await response.json();
  renderImportCenter(data);
}

function renderImportCenter(data) {
  renderAutoExportCard();
  const pathInput = document.querySelector("#import-path");
  const importFolderInput = document.querySelector("#import-folder-path");
  const watchedFolder = document.querySelector("#watched-folder");
  const candidates = document.querySelector("#import-candidates");
  if (importFolderInput) importFolderInput.value = data.import_folder?.path || data.paths?.import_folder || "";
  if (pathInput && !pathInput.value) pathInput.value = data.paths?.default_workbook || "";
  if (watchedFolder) watchedFolder.value = data.paths?.watched_folder || "";
  if (candidates) {
    const candidateFiles = data.candidate_file_options || (data.candidate_files || []).map((path) => ({ path, filename: fileName(path), source: "Workspace" }));
    candidates.innerHTML = candidateFiles.length
      ? candidateFiles.map((file) => `<option value="${escapeHtml(file.path)}">${escapeHtml(file.filename)} - ${escapeHtml(file.source)} - ${escapeHtml(file.modified_at || "")}</option>`).join("")
      : `<option value="">No Excel files found</option>`;
    if (candidateFiles.length && pathInput && !pathInput.value) {
      pathInput.value = candidateFiles[0].path;
    }
  }

  renderImportFolderSummary(data.import_folder || {});
  renderBackupPolicy(data.backup_policy || {});
  renderPathStack(data.paths || {});
  renderImportPipeline(data);
  renderSchemaTable(data.columns || []);
  renderImportConsole(data.recent_logs || []);
}

function renderImportFolderSummary(folder) {
  const target = document.querySelector("#import-folder-summary");
  if (!target) return;
  const currentFile = folder.current_file;
  target.innerHTML = `
    <div>
      <span>Current workbook</span>
      <strong>${escapeHtml(currentFile?.filename || "No workbook in folder yet")}</strong>
      <small>${escapeHtml(currentFile ? `${currentFile.size} - modified ${currentFile.modified_at}` : "Drop an .xlsx file into the folder to start.")}</small>
    </div>
    <div>
      <span>Folder archive</span>
      <strong>${escapeHtml(String(folder.archive_file_count || 0))} files</strong>
      <small>${escapeHtml(folder.archive_folder || "")}</small>
    </div>
    <div>
      <span>Auto check</span>
      <strong>${escapeHtml(String(folder.poll_interval_seconds || 30))}s</strong>
      <small>${escapeHtml(folder.instructions || "")}</small>
    </div>
  `;
}

function renderBackupPolicy(policy) {
  const target = document.querySelector("#backup-policy");
  if (!target) return;
  const items = [
    ["Pre-import backup", policy.pre_import],
    ["Archive original", policy.archive],
    ["Transaction", policy.transaction],
    ["Post-import backup", policy.post_import],
  ];
  target.innerHTML = items.map(([label, detail]) => `
    <article>
      <span>${escapeHtml(label)}</span>
      <p>${escapeHtml(detail || "")}</p>
    </article>
  `).join("");
}

function renderPathStack(paths) {
  const container = document.querySelector("#import-paths");
  if (!container) return;
  const entries = [
    ["Import Folder", paths.import_folder || paths.upload_folder || paths.watched_folder],
    ["Export Folder", paths.export_folder],
    ["Folder archive", paths.archive_folder],
    ["Database backups", paths.backup_folder],
  ];
  container.innerHTML = entries.map(([label, value]) => `
    <div class="path-row">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value || "Not configured")}</strong>
    </div>
  `).join("");
}

function renderImportPipeline(data) {
  const target = document.querySelector("#import-pipeline");
  if (!target) return;
  const latest = data.latest_import;
  const steps = [
    ["Workbook accepted", latest ? latest.filename : "Waiting for an Excel file", latest ? "completed" : "idle"],
    ["Pre-import backup created", `${(data.recent_backups || []).length} recent backup records`, (data.recent_backups || []).length ? "completed" : "idle"],
    ["Schema validated and mapped", `${(data.columns || []).length} registered columns visible`, (data.columns || []).length ? "completed" : "idle"],
    ["Rows merged into SQLite", latest ? `${latest.rows_added} new, ${latest.rows_updated} updated` : "No completed import yet", latest ? "completed" : "idle"],
    ["Post-import backup created", "Created after successful imports", (data.recent_backups || []).length > 1 ? "completed" : "idle"],
  ];
  target.innerHTML = steps.map(([label, detail, state]) => renderPipelineStep(label, detail, state)).join("");
}

function renderPipelineStep(label, detail, state) {
  return `
    <div class="pipeline-step ${escapeHtml(state)}">
      <span class="pipeline-dot" aria-hidden="true"></span>
      <strong>${escapeHtml(label)}</strong>
      <small>${escapeHtml(detail)}</small>
    </div>
  `;
}

function renderSchemaTable(columns) {
  const table = document.querySelector("#schema-table");
  const count = document.querySelector("#schema-count");
  if (count) count.textContent = `${columns.length} columns`;
  if (!table) return;
  table.innerHTML = `
    <thead><tr><th>Column</th><th>Type</th><th>Status</th><th>First</th><th>Last</th></tr></thead>
    <tbody>
      ${columns.map((column) => `
        <tr>
          <td>${escapeHtml(column.column_name)}</td>
          <td>${escapeHtml(column.detected_type)}</td>
          <td><span class="table-pill ${column.status === "Active" ? "good" : "warn"}">${escapeHtml(column.status)}</span></td>
          <td>${escapeHtml(column.first_seen_batch_id || "")}</td>
          <td>${escapeHtml(column.last_seen_batch_id || "")}</td>
        </tr>
      `).join("") || `<tr><td colspan="5" class="empty-state">No schema rows registered yet.</td></tr>`}
    </tbody>
  `;
}

function renderImportConsole(logs) {
  const target = document.querySelector("#import-console");
  const count = document.querySelector("#log-count");
  if (count) count.textContent = `${logs.length} events`;
  if (!target) return;
  target.innerHTML = logs.map((log) => `
    <div class="console-row ${escapeHtml(log.event_type)}">
      <span>[${escapeHtml(log.created_at || "pending")}]</span>
      <strong>${escapeHtml(log.event_type)}</strong>
      <p>${escapeHtml(log.message)}</p>
    </div>
  `).join("") || `<div class="console-row"><span>[ready]</span><strong>INFO</strong><p>No import events logged yet.</p></div>`;
}

async function runImportFromPath() {
  const input = document.querySelector("#import-path");
  const button = document.querySelector("#run-import");
  const status = document.querySelector("#import-run-status");
  const path = String(input?.value || "").trim();
  if (!path) {
    if (status) status.textContent = "Choose a workbook path first.";
    return;
  }
  if (button) button.disabled = true;
  if (status) status.textContent = "Running import with archive and backups...";
  try {
    const response = await fetch("/api/import/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path }),
    });
    const data = await response.json();
    if (!response.ok) {
      if (status) status.textContent = data.detail || "Import failed.";
      return;
    }
    if (status) {
      status.textContent = `Batch ${data.batch_id} completed: ${data.new_rows} new, ${data.updated_rows} updated, ${data.unchanged_rows} unchanged.`;
    }
    await loadImportCenter();
  } finally {
    if (button) button.disabled = false;
  }
}

function renderAutoExportCard() {
  const el = document.querySelector("#auto-export-card");
  if (!el) return;
  const prefs = getSavedPrefs();
  const summary = buildPrefsSummary(prefs);
  el.innerHTML = `
    <div class="panel-head">
      <div>
        <h2>Auto Export</h2>
        <p>Export filtered results using your saved filter preferences from the Filtering tab.</p>
      </div>
      <span class="mode-pill">${prefs ? "Preferences loaded" : "No preferences"}</span>
    </div>
    <div class="auto-export-prefs">
      <span class="auto-export-label">Current saved filters</span>
      <p class="auto-export-summary">${escapeHtml(summary)}</p>
    </div>
    <div class="action-row" style="margin-top:14px">
      <button class="primary-button" id="do-auto-export" type="button" ${prefs ? "" : "disabled"}>Export Now</button>
      <a href="/filters" class="secondary-button" style="display:inline-flex;align-items:center;text-decoration:none">Edit Filters</a>
    </div>
    <div id="auto-export-status" class="inline-status" aria-live="polite" style="margin-top:10px"></div>
  `;
  const btn = el.querySelector("#do-auto-export");
  if (btn) btn.addEventListener("click", runAutoExport);
}

async function runAutoExport() {
  const btn = document.querySelector("#do-auto-export");
  const status = document.querySelector("#auto-export-status");
  const prefs = getSavedPrefs();
  if (!prefs) { if (status) status.textContent = "No saved preferences — set filters first."; return; }
  if (btn) btn.disabled = true;
  if (status) status.textContent = "Exporting…";
  try {
    const r = await fetch("/api/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...prefs, page_size: 500 }),
    });
    const data = await r.json();
    if (!r.ok) { if (status) status.textContent = data.detail || "Export failed."; return; }
    if (status) status.textContent = `Exported ${data.row_count.toLocaleString()} rows → ${data.path}`;
  } catch (err) {
    if (status) status.textContent = `Export failed: ${err}`;
  } finally {
    if (btn) btn.disabled = false;
  }
}

async function saveImportFolder() {
  const input = document.querySelector("#import-folder-path");
  const button = document.querySelector("#save-import-folder");
  const status = document.querySelector("#import-run-status");
  const path = String(input?.value || "").trim();
  if (!path) {
    if (status) status.textContent = "Choose an Import Folder path first.";
    return;
  }
  if (button) button.disabled = true;
  if (status) status.textContent = "Saving Import Folder...";
  try {
    const response = await fetch("/api/import-folder", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path }),
    });
    const data = await response.json();
    if (!response.ok) {
      if (status) status.textContent = data.detail || "Could not save Import Folder.";
      return;
    }
    if (status) status.textContent = `Import Folder saved: ${data.folder}`;
    await loadImportCenter();
  } finally {
    if (button) button.disabled = false;
  }
}

async function refreshUploadFolder({ automatic }) {
  const button = document.querySelector("#refresh-upload-folder");
  const status = document.querySelector("#import-run-status");
  if (button && !automatic) button.disabled = true;
  if (status) status.textContent = automatic ? "Auto-checking Import Folder..." : "Checking Import Folder...";
  try {
    const response = await fetch("/api/import/refresh-folder", { method: "POST" });
    const data = await response.json();
    if (!response.ok) {
      if (status) status.textContent = data.detail || "Import Folder check failed.";
      return;
    }
    const archived = data.archived_files?.length ? `, ${data.archived_files.length} archived` : "";
    const summary = `${data.checked} checked, ${data.imported} imported, ${data.skipped} already used, ${data.failed} failed${archived}`;
    if (status) status.textContent = `${automatic ? "Auto check" : "Import Folder check"}: ${summary}.`;
    await loadImportCenter();
  } finally {
    if (button) button.disabled = false;
  }
}

function startImportFolderAutoRefresh() {
  if (importAutoRefreshTimer) {
    clearInterval(importAutoRefreshTimer);
  }
  setTimeout(() => refreshUploadFolder({ automatic: true }), 1500);
  importAutoRefreshTimer = setInterval(() => refreshUploadFolder({ automatic: true }), 30000);
}

async function loadSystemStatus() {
  const response = await fetch("/api/system-status");
  const data = await response.json();
  renderSystemStatus(data);
}

function renderSystemStatus(data) {
  renderHealthOverview(data.health || {});
  renderSystemInfo(data.system || {});
}

function renderHealthOverview(h) {
  const el = document.querySelector("#health-overview");
  if (!el) return;
  const dbState = h.database?.ok ? "good" : "warn";
  const importAge = h.last_import ? `Last import: ${escapeHtml(h.last_import)}` : "No imports yet";
  const backupAge = h.latest_backup ? `Latest: ${escapeHtml(h.latest_backup)}` : "No backups yet";
  el.innerHTML = `
    <div class="health-card-grid">
      <article class="health-card">
        <span class="health-card-label">Active Students</span>
        <strong class="health-card-value">${(h.students?.active ?? 0).toLocaleString()}</strong>
        <p>${(h.students?.total ?? 0).toLocaleString()} total in database</p>
      </article>
      <article class="health-card ${dbState}">
        <span class="health-card-label">Database</span>
        <strong class="health-card-value">${escapeHtml(h.database?.size || "—")}</strong>
        <p>${escapeHtml(h.database?.ok ? "SQLite healthy" : "Not found")}</p>
      </article>
      <article class="health-card">
        <span class="health-card-label">Last Import</span>
        <strong class="health-card-value">${h.import_count ? escapeHtml(String(h.import_count)) : "0"} batches</strong>
        <p>${escapeHtml(importAge)}</p>
      </article>
      <article class="health-card ${h.backup_count ? "good" : "warn"}">
        <span class="health-card-label">Backup Vault</span>
        <strong class="health-card-value">${h.backup_count ?? 0}</strong>
        <p>${escapeHtml(backupAge)}</p>
      </article>
    </div>
  `;
}

function renderSystemInfo(s) {
  const el = document.querySelector("#system-info-panel");
  if (!el) return;
  const diskColor = s.disk_used_pct > 90 ? "#C85F00" : s.disk_used_pct > 75 ? "#f59e0b" : "var(--good)";
  el.innerHTML = `
    <div class="sysinfo-grid">
      <div class="sysinfo-block">
        <span>Python</span><strong>${escapeHtml(s.python_version || "—")}</strong>
      </div>
      <div class="sysinfo-block">
        <span>Platform</span><strong>${escapeHtml(s.platform || "—")}</strong>
      </div>
      <div class="sysinfo-block">
        <span>Embedding model</span><strong>${escapeHtml(s.embedding_model || "—")}</strong>
      </div>
      <div class="sysinfo-block">
        <span>Port</span><strong>${escapeHtml(String(s.port || "8080"))}</strong>
      </div>
      <div class="sysinfo-block">
        <span>Database</span><strong>${escapeHtml(s.database_size || "—")}</strong>
        <small>${escapeHtml(s.database_path || "")}</small>
      </div>
      <div class="sysinfo-block">
        <span>Vector index</span><strong>${escapeHtml(s.index_size || "—")}</strong>
        <small>${escapeHtml(s.index_path || "")}</small>
      </div>
      <div class="sysinfo-block">
        <span>Import folder</span><strong>—</strong>
        <small>${escapeHtml(s.import_folder || "")}</small>
      </div>
      <div class="sysinfo-block">
        <span>Export folder</span><strong>—</strong>
        <small>${escapeHtml(s.export_folder || "")}</small>
      </div>
      <div class="sysinfo-block">
        <span>Backup folder</span><strong>—</strong>
        <small>${escapeHtml(s.backup_folder || "")}</small>
      </div>
      <div class="sysinfo-block sysinfo-disk">
        <span>Disk usage</span>
        <strong>${escapeHtml(String(s.disk_used_pct || 0))}%</strong>
        <div class="disk-bar"><div class="disk-bar-fill" style="width:${s.disk_used_pct || 0}%;background:${diskColor}"></div></div>
        <small>${escapeHtml(s.disk_free || "?")} free of ${escapeHtml(s.disk_total || "?")}</small>
      </div>
    </div>
  `;
}

let _diagChecks = [];
let _diagSelected = new Set();

async function initDiagnosticChecks() {
  try {
    const r = await fetch("/api/system-status/diagnostics/checks");
    const data = await r.json();
    _diagChecks = data.checks || [];
    _diagSelected = new Set(_diagChecks.map((c) => c.key));
    renderDiagControls();
  } catch (_) {}
}

function renderDiagControls() {
  const container = document.querySelector("#diag-controls");
  if (!container || !_diagChecks.length) return;
  container.innerHTML = `
    <div class="diag-toggle-row">
      ${_diagChecks.map((c) => `
        <button class="diag-toggle ${_diagSelected.has(c.key) ? "active" : ""}" type="button" data-check="${escapeHtml(c.key)}">
          ${escapeHtml(c.label)}
        </button>
      `).join("")}
      <button class="diag-toggle-all" type="button" id="diag-select-all">All</button>
    </div>
  `;
  container.querySelectorAll(".diag-toggle[data-check]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const k = btn.dataset.check;
      if (_diagSelected.has(k)) { _diagSelected.delete(k); btn.classList.remove("active"); }
      else { _diagSelected.add(k); btn.classList.add("active"); }
    });
  });
  const allBtn = container.querySelector("#diag-select-all");
  if (allBtn) {
    allBtn.addEventListener("click", () => {
      const allActive = _diagSelected.size === _diagChecks.length;
      if (allActive) {
        _diagSelected.clear();
        container.querySelectorAll(".diag-toggle[data-check]").forEach((b) => b.classList.remove("active"));
      } else {
        _diagChecks.forEach((c) => _diagSelected.add(c.key));
        container.querySelectorAll(".diag-toggle[data-check]").forEach((b) => b.classList.add("active"));
      }
    });
  }
}

async function runDiagnostics() {
  const btn = document.querySelector("#run-diagnostics-btn");
  const section = document.querySelector("#diagnostics-section");
  const grid = document.querySelector("#diagnostic-results");
  const pill = document.querySelector("#diag-summary-pill");
  const bar = document.querySelector("#diag-progress-bar");
  const barWrap = document.querySelector("#diag-progress-wrap");
  const barLabel = document.querySelector("#diag-progress-label");
  if (!grid) return;

  const selected = _diagChecks.filter((c) => _diagSelected.has(c.key));
  if (!selected.length) return;

  if (btn) { btn.disabled = true; btn.textContent = "Running…"; }
  const resultsSection = document.querySelector("#diagnostics-section");
  if (resultsSection) resultsSection.hidden = false;
  if (section) section.hidden = false;
  if (pill) { pill.textContent = "Running…"; pill.className = "mode-pill"; }
  if (barWrap) barWrap.hidden = false;

  // Place skeleton cards for each selected check
  grid.innerHTML = selected.map((c) => `
    <article class="diag-card diag-loading" id="diag-card-${escapeHtml(c.key)}">
      <div class="diag-card-head">
        <span class="diag-icon diag-pending">…</span>
        <span class="diag-name">${escapeHtml(c.label)}</span>
      </div>
      <div class="diag-shimmer"></div>
    </article>
  `).join("");

  let passed = 0, warned = 0, failed = 0;

  for (let i = 0; i < selected.length; i++) {
    const check = selected[i];
    const pct = Math.round(((i) / selected.length) * 100);
    if (bar) bar.style.width = `${pct}%`;
    if (barLabel) barLabel.textContent = `${i} / ${selected.length} — ${check.label}…`;

    try {
      const r = await fetch("/api/system-status/diagnostics/single", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ check: check.key }),
      });
      const res = await r.json();
      if (res.status === "pass") passed++;
      else if (res.status === "warn") warned++;
      else failed++;

      const cardEl = document.getElementById(`diag-card-${check.key}`);
      if (cardEl) {
        cardEl.outerHTML = renderDiagCard(res);
      }
    } catch (err) {
      failed++;
      const cardEl = document.getElementById(`diag-card-${check.key}`);
      if (cardEl) {
        cardEl.outerHTML = renderDiagCard({ key: check.key, name: check.label, status: "fail", value: "Error", detail: String(err), ms: 0, details: {} });
      }
    }
  }

  if (bar) bar.style.width = "100%";
  if (barLabel) barLabel.textContent = `${selected.length} / ${selected.length} — Complete`;
  setTimeout(() => { if (barWrap) barWrap.hidden = true; }, 1200);

  if (pill) {
    pill.textContent = `${passed} passed · ${warned} warned · ${failed} failed`;
    pill.className = `mode-pill ${failed > 0 ? "diag-fail" : warned > 0 ? "diag-warn" : "diag-pass"}`;
  }
  if (btn) { btn.disabled = false; btn.textContent = "Run All Diagnostics"; }
}

function renderDiagCard(res) {
  const icons = { pass: "✓", warn: "⚠", fail: "✕" };
  const icon = icons[res.status] || "?";
  const detailRows = Object.entries(res.details || {}).map(([k, v]) => `
    <div class="diag-detail-row">
      <span>${escapeHtml(k)}</span>
      <strong>${escapeHtml(String(v))}</strong>
    </div>
  `).join("");
  return `
    <article class="diag-card diag-${escapeHtml(res.status)} diag-reveal">
      <div class="diag-card-head">
        <span class="diag-icon">${icon}</span>
        <span class="diag-name">${escapeHtml(res.name)}</span>
        <span class="diag-ms">${res.ms}ms</span>
      </div>
      <strong class="diag-value">${escapeHtml(res.value)}</strong>
      <p class="diag-detail">${escapeHtml(res.detail)}</p>
      ${detailRows ? `<div class="diag-details-grid">${detailRows}</div>` : ""}
    </article>
  `;
}

function renderDiagSkeleton(n) {
  return Array.from({ length: n }, () => `<article class="diag-card diag-loading"><div class="diag-shimmer"></div></article>`).join("");
}

function collectSearchPayload() {
  const form = document.querySelector("#search-form");
  const formData = new FormData(form);
  const globalQuery = String(document.querySelector("#global-search-input")?.value || "").trim();
  return {
    global_query: globalQuery || "",
    semantic_query: valueOf(formData, "semantic_query"),
    name_query: valueOf(formData, "name_query"),
    technical_skills_query: valueOf(formData, "technical_skills_query"),
    gpa_min: valueOf(formData, "gpa_min"),
    gpa_max: valueOf(formData, "gpa_max"),
    majors: getMultiSelectValues("ms-major"),
    classes: getMultiSelectValues("ms-class"),
    probation: valueOf(formData, "probation") || "any",
    financial_aid: valueOf(formData, "financial_aid") || "any",
    dorms: valueOf(formData, "dorms") || "any",
    sort_field: valueOf(formData, "sort_field") || "STUD_ID",
    sort_direction: valueOf(formData, "sort_direction") || "asc",
    include_missing: formData.has("include_missing"),
    semantic_threshold: valueOf(formData, "semantic_threshold") || "0.10",
    page_size: Number(valueOf(formData, "page_size") || 25),
  };
}

function valueOf(formData, key) {
  return String(formData.get(key) || "").trim();
}

function renderMetrics(metrics) {
  const total = metrics.total_students || 0;
  const gpaVal = metrics.average_gpa === null ? "—" : Number(metrics.average_gpa).toFixed(2);
  const probPct = total > 0 ? formatPercent(metrics.probation_count, total) : "0%";
  const aidPct = total > 0 ? formatPercent(metrics.financial_aid_count, total) : "0%";
  const defs = [
    { label: "Active Students", value: total,                         sub: "In current workbook" },
    { label: "Average GPA",     value: gpaVal,                        sub: "All active students" },
    { label: "On Probation",    value: metrics.probation_count,       sub: `${probPct} of students` },
    { label: "Financial Aid",   value: metrics.financial_aid_count,   sub: `${aidPct} receiving support` },
  ];
  document.querySelector("#metric-grid").innerHTML = defs.map(({ label, value, sub }) => `
    <article class="metric-card">
      <span>${escapeHtml(label)}</span>
      <strong>${formatValue(value)}</strong>
      <small>${escapeHtml(sub)}</small>
    </article>
  `).join("");
}

function renderChartGrid(targetId, chartSpecs) {
  Object.values(_chartInstances).forEach((c) => { try { c.destroy(); } catch (_) {} });
  Object.keys(_chartInstances).forEach((k) => delete _chartInstances[k]);

  const target = document.querySelector(`#${targetId}`);
  target.innerHTML = chartSpecs.map((spec, index) => renderChartCard(normalizeChartSpec(spec), index)).join("");

  chartSpecs.forEach((spec, index) => {
    const normalized = normalizeChartSpec(spec);
    requestAnimationFrame(() => initChartJs(`chart-canvas-${index}`, normalized));
  });
}

function normalizeChartSpec(spec) {
  if (Array.isArray(spec)) {
    return { title: spec[0], type: "ranked-bars", points: spec[1], unit: "records", limit: 8 };
  }
  return {
    title: spec.title,
    type: spec.type || "ranked-bars",
    points: spec.points || [],
    unit: spec.unit || "records",
    limit: spec.limit || 8,
  };
}

function normalizePoints(points) {
  return (points || []).map((point) => ({
    label: String(point.label || "Unknown"),
    value: Number(point.value) || 0,
  }));
}

function renderChartCard(spec, index) {
  const canvasId = `chart-canvas-${index}`;
  const allPoints = normalizePoints(spec.points);
  const visible = allPoints.slice(0, spec.limit);
  const topPoint = findTopPoint(visible);
  const total = chartTotal(allPoints, spec);
  const summary = chartSummary(spec, visible, allPoints);
  const pill = renderChartStatPill(spec, topPoint, total);

  return `
    <article class="chart-card" aria-label="${escapeHtml(spec.title)}">
      <div class="chart-head">
        <div>
          <h3>${escapeHtml(spec.title)}</h3>
          <p>${escapeHtml(summary)}</p>
        </div>
        ${pill}
      </div>
      <div class="chart-canvas-wrap">
        <canvas id="${escapeHtml(canvasId)}" role="img" aria-label="${escapeHtml(spec.title)}"></canvas>
      </div>
    </article>
  `;
}

function initChartJs(canvasId, spec) {
  if (typeof Chart === "undefined") return;
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  const allPoints = normalizePoints(spec.points);
  const points = allPoints.slice(0, spec.limit || 8);
  const labels = points.map((p) => p.label);
  const values = points.map((p) => p.value);
  const valueTotal = values.reduce((s, v) => s + v, 0);

  const gridLine = { color: "rgba(15, 23, 42, 0.05)" };
  const noBorder = { display: false };
  const mutedTick = { font: { size: 11, family: "ui-sans-serif, system-ui, -apple-system, sans-serif" }, color: "#94a3b8" };
  const boldTick = { font: { size: 12, weight: "700", family: "ui-sans-serif, system-ui, -apple-system, sans-serif" }, color: "#334155" };

  const tooltip = {
    backgroundColor: "#0f172a",
    titleColor: "#e2e8f0",
    bodyColor: "#94a3b8",
    borderColor: "rgba(255,255,255,0.08)",
    borderWidth: 1,
    padding: { x: 12, y: 10 },
    cornerRadius: 8,
    titleFont: { size: 12, weight: "800" },
    bodyFont: { size: 12 },
    displayColors: false,
    callbacks: {
      label: (item) => {
        if (spec.type === "score-bars") return ` GPA ${Number(item.raw).toFixed(2)}`;
        const pct = valueTotal > 0 ? ` (${((item.raw / valueTotal) * 100).toFixed(1)}%)` : "";
        return ` ${Number(item.raw).toLocaleString()} ${spec.unit}${pct}`;
      },
    },
  };

  const animIn = { duration: 750, easing: "easeOutQuart" };
  let config;

  if (spec.type === "ranked-bars") {
    config = {
      type: "bar",
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: "#840132",
          hoverBackgroundColor: "#a3193f",
          borderRadius: 5,
          borderSkipped: false,
        }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        animation: animIn,
        plugins: { legend: { display: false }, tooltip },
        scales: {
          x: { grid: gridLine, border: noBorder, ticks: mutedTick },
          y: { grid: { display: false }, border: noBorder, ticks: boldTick },
        },
      },
    };

  } else if (spec.type === "histogram") {
    const grad = ctx.createLinearGradient(0, 0, 0, 250);
    grad.addColorStop(0, "rgba(132, 1, 50, 0.52)");
    grad.addColorStop(1, "rgba(132, 1, 50, 0.03)");
    config = {
      type: "line",
      data: {
        labels,
        datasets: [{
          data: values,
          fill: true,
          backgroundColor: grad,
          borderColor: "#840132",
          borderWidth: 2.5,
          tension: 0.42,
          pointBackgroundColor: "#fff",
          pointBorderColor: "#840132",
          pointBorderWidth: 2.5,
          pointRadius: 5,
          pointHoverRadius: 7,
          pointHoverBackgroundColor: "#840132",
          pointHoverBorderColor: "#fff",
          pointHoverBorderWidth: 2.5,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 900, easing: "easeOutQuart" },
        plugins: { legend: { display: false }, tooltip },
        scales: {
          x: { grid: { display: false }, border: noBorder, ticks: boldTick },
          y: { grid: gridLine, border: noBorder, ticks: mutedTick, beginAtZero: true },
        },
      },
    };

  } else if (spec.type === "score-bars") {
    const tealGrad = ctx.createLinearGradient(0, 0, (canvas.parentElement || canvas).offsetWidth || 400, 0);
    tealGrad.addColorStop(0, "rgba(23, 87, 87, 0.65)");
    tealGrad.addColorStop(1, "#175757");
    config = {
      type: "bar",
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: tealGrad,
          hoverBackgroundColor: "#1c6868",
          borderRadius: 5,
          borderSkipped: false,
        }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        animation: animIn,
        plugins: { legend: { display: false }, tooltip },
        scales: {
          x: { grid: gridLine, border: noBorder, ticks: mutedTick, min: 0, max: 4 },
          y: { grid: { display: false }, border: noBorder, ticks: boldTick },
        },
      },
    };

  } else if (spec.type === "alert-bars") {
    config = {
      type: "bar",
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: "rgba(200, 95, 0, 0.82)",
          hoverBackgroundColor: "#C85F00",
          borderRadius: 5,
          borderSkipped: false,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: animIn,
        plugins: { legend: { display: false }, tooltip },
        scales: {
          x: { grid: { display: false }, border: noBorder, ticks: boldTick },
          y: { grid: gridLine, border: noBorder, ticks: mutedTick, beginAtZero: true },
        },
      },
    };
  }

  if (config) {
    _chartInstances[canvasId] = new Chart(ctx, config);
  }
}

function renderChartStatPill(spec, topPoint, total) {
  if (!topPoint) {
    return `<span class="chart-total"><strong>0</strong><small>${escapeHtml(spec.unit)}</small></span>`;
  }
  if (spec.type === "score-bars") {
    return `<span class="chart-total"><strong>${escapeHtml(formatChartValue(topPoint.value, "score"))}</strong><small>highest avg</small></span>`;
  }
  return `<span class="chart-total"><strong>${escapeHtml(formatChartValue(total))}</strong><small>${escapeHtml(spec.unit)}</small></span>`;
}

function chartSummary(spec, visible, allPoints) {
  if (!visible.length) {
    return "No data yet — import a workbook to populate.";
  }
  const topPoint = findTopPoint(visible);
  const total = chartTotal(allPoints, spec);
  if (spec.type === "score-bars") {
    const bottom = visible[visible.length - 1];
    const spread = (topPoint.value - bottom.value).toFixed(2);
    return `Highest: ${topPoint.label} · ${formatChartValue(topPoint.value, "score")} avg · spread ${spread} pts`;
  }
  if (spec.type === "histogram") {
    const topShare = total > 0 ? formatPercent(topPoint.value, total) : "0%";
    return `Largest band: ${topPoint.label} · ${topPoint.value.toLocaleString()} students · ${topShare} of cohort`;
  }
  if (spec.type === "alert-bars") {
    const totalAffected = allPoints.reduce((s, p) => s + p.value, 0);
    return `${totalAffected.toLocaleString()} on probation · most affected: ${topPoint.label} (${topPoint.value})`;
  }
  const topShare = total > 0 ? formatPercent(topPoint.value, total) : "0%";
  return `${topPoint.label} · ${topPoint.value.toLocaleString()} ${spec.unit} · ${topShare} of cohort`;
}

function findTopPoint(points) {
  return points.reduce((top, point) => (top === null || point.value > top.value ? point : top), null);
}

function chartTotal(points, spec) {
  if (spec.type === "score-bars") return 4;
  return points.reduce((total, point) => total + point.value, 0);
}

function chartColor(index) {
  const colors = ["#840132", "#64748b", "#175757", "#142D66", "#005E99", "#26613A", "#C85F00", "#4B1757"];
  return colors[index % colors.length];
}

function renderLatestImport(summary) {
  const panel = document.querySelector("#latest-import");
  if (!summary) {
    panel.className = "import-strip empty";
    panel.innerHTML = "No imports yet — drop an Excel workbook into the Import Folder to populate the database.";
    return;
  }
  const statusClass = summary.status === "completed" ? "completed" : summary.status === "failed" ? "failed" : "pending";
  let importedAt = "";
  try {
    importedAt = new Date(summary.imported_at).toLocaleString("en-US", { dateStyle: "medium", timeStyle: "short" });
  } catch (_) {
    importedAt = summary.imported_at || "";
  }
  const newCols = summary.new_columns || [];
  const missingCols = summary.missing_columns || [];
  const missingClass = summary.rows_missing > 0 ? "import-strip-alert" : "";
  panel.className = "import-strip";
  panel.innerHTML = `
    <div class="import-strip-row">
      <div class="import-strip-meta">
        <span class="import-strip-label">Last import</span>
        <strong>${escapeHtml(summary.filename)}</strong>
        <span class="import-strip-time">${escapeHtml(importedAt)}</span>
        <span class="import-status-badge ${statusClass}">${escapeHtml(summary.status)}</span>
      </div>
      <div class="import-strip-counts">
        <div><strong>${Number(summary.rows_added).toLocaleString()}</strong><span>new</span></div>
        <div><strong>${Number(summary.rows_updated).toLocaleString()}</strong><span>updated</span></div>
        <div><strong>${Number(summary.rows_unchanged).toLocaleString()}</strong><span>unchanged</span></div>
        <div class="${missingClass}"><strong>${Number(summary.rows_missing).toLocaleString()}</strong><span>missing</span></div>
      </div>
    </div>
    ${summary.status === "failed" && summary.error_message ? `<div class="import-strip-notice warn">${escapeHtml(summary.error_message)}</div>` : ""}
    ${newCols.length ? `<div class="import-strip-notice info">${newCols.length} new column(s): ${escapeHtml(newCols.slice(0, 4).join(", "))}${newCols.length > 4 ? " …" : ""}</div>` : ""}
    ${missingCols.length ? `<div class="import-strip-notice warn">${missingCols.length} column(s) missing: ${escapeHtml(missingCols.slice(0, 4).join(", "))}${missingCols.length > 4 ? " …" : ""}</div>` : ""}
  `;
}

function renderResults(rows) {
  const body = document.querySelector("#results-body");
  if (!rows.length) {
    body.innerHTML = `<tr><td colspan="13" class="empty-state">No matching students.</td></tr>`;
    return;
  }
  const gq = String(document.querySelector("#global-search-input")?.value || "").trim();
  const hl = (v) => gq ? highlightText(v, gq) : escapeHtml(v);
  body.innerHTML = rows.map((row) => `
    <tr>
      <td>${hl(row.STUD_ID)}</td>
      <td>${hl(row.STUD_NAME)}</td>
      <td>${hl(row.MAJR_DESC)}</td>
      <td>${hl(row.CLAS_DESC)}</td>
      <td>${escapeHtml(row.CUM_GPA)}</td>
      <td>${escapeHtml(row.added_to_db_at)}</td>
      <td>${escapeHtml(row.modified_in_db_at)}</td>
      <td>${escapeHtml(row.PROBATION)}</td>
      <td>${escapeHtml(row.FINANCIAL_AID)}</td>
      <td class="score">${escapeHtml(row.semantic_score)}</td>
      <td class="text-cell explanation-cell">${escapeHtml(row.semantic_explanation)}</td>
      <td class="text-cell">${hl(row.WSP_TECHNICAL_SKILLS)}</td>
      <td class="text-cell">${hl(row.WSP_PREFERRED_TYPE_OF_WORK)}</td>
    </tr>
  `).join("");
}

function renderActiveFilterTags(payload) {
  const container = document.querySelector("#active-filter-tags");
  if (!container) {
    return;
  }
  const tags = [];
  if (payload.global_query) tags.push(`Search: ${payload.global_query}`);
  if (payload.semantic_query) {
    tags.push(`AI: ${payload.semantic_query}`);
    tags.push(`Match >= ${Math.round(Number(payload.semantic_threshold || 0) * 100)}%`);
  }
  if (payload.name_query) tags.push(`Name contains ${payload.name_query}`);
  if (payload.technical_skills_query) tags.push(`Skills contain ${payload.technical_skills_query}`);
  if (payload.gpa_min) tags.push(`GPA >= ${payload.gpa_min}`);
  if (payload.gpa_max) tags.push(`GPA <= ${payload.gpa_max}`);
  if (payload.majors && payload.majors.length) tags.push(`Major = ${payload.majors.join(", ")}`);
  if (payload.classes && payload.classes.length) tags.push(`Class = ${payload.classes.join(", ")}`);
  if (payload.probation !== "any") tags.push(`Probation = ${payload.probation}`);
  if (payload.financial_aid !== "any") tags.push(`Aid = ${payload.financial_aid}`);
  if (payload.dorms !== "any") tags.push(`Dorms = ${payload.dorms}`);
  if (payload.include_missing) tags.push("Include missing");

  container.classList.toggle("has-tags", tags.length > 0);
  container.innerHTML = tags.length
    ? `<strong>Active Filters:</strong>${tags.map((tag) => `<span class="filter-chip">${escapeHtml(tag)}</span>`).join("")}`
    : "";
}

function updateThresholdOutput() {
  const input = document.querySelector('input[name="semantic_threshold"]');
  const output = document.querySelector("#threshold-output");
  if (input && output) {
    output.textContent = `${Math.round(Number(input.value || 0) * 100)}%`;
  }
}

// ── multi-select picker ───────────────────────────────────────────────────────
// State keyed by element id
const _msState = {};

function initMultiSelect(rootId, allOptions) {
  const root = document.getElementById(rootId);
  if (!root) return;
  const placeholder = root.dataset.placeholder || "Any";
  _msState[rootId] = { allOptions: allOptions || [], selected: new Set() };

  root.innerHTML = `
    <button type="button" class="ms-trigger" data-open="false" aria-haspopup="listbox" aria-expanded="false">
      <span class="ms-trigger-label">${escapeHtml(placeholder)}</span>
      <span class="ms-trigger-arrow">▼</span>
    </button>
    <div class="ms-dropdown" role="listbox" aria-multiselectable="true">
      <input class="ms-search" type="text" placeholder="Search..." autocomplete="off">
      <div class="ms-list"></div>
      <div class="ms-clear-row">
        <button type="button" class="ms-clear-btn">Clear all</button>
        <span class="ms-count"></span>
      </div>
    </div>
    <div class="ms-pills"></div>
  `;

  const trigger  = root.querySelector(".ms-trigger");
  const dropdown = root.querySelector(".ms-dropdown");
  const search   = root.querySelector(".ms-search");
  const list     = root.querySelector(".ms-list");
  const clearBtn = root.querySelector(".ms-clear-btn");
  const countEl  = root.querySelector(".ms-count");
  const pillsEl  = root.querySelector(".ms-pills");

  function renderOptions(filter) {
    const q = (filter || "").toLowerCase();
    const opts = _msState[rootId].allOptions.filter((o) => !q || o.toLowerCase().includes(q));
    if (!opts.length) {
      list.innerHTML = `<div class="ms-empty">No matches</div>`;
      return;
    }
    list.innerHTML = opts.map((o) => {
      const checked = _msState[rootId].selected.has(o) ? "checked" : "";
      return `<label class="ms-option"><input type="checkbox" value="${escapeHtml(o)}" ${checked}><span>${escapeHtml(o)}</span></label>`;
    }).join("");
    list.querySelectorAll("input[type=checkbox]").forEach((cb) => {
      cb.addEventListener("change", () => {
        if (cb.checked) _msState[rootId].selected.add(cb.value);
        else _msState[rootId].selected.delete(cb.value);
        renderPills();
        renderTriggerLabel();
        triggerChange();
      });
    });
  }

  function renderPills() {
    const sel = [..._msState[rootId].selected];
    countEl.textContent = sel.length ? `${sel.length} selected` : "";
    pillsEl.innerHTML = sel.map((v) => `
      <span class="ms-pill" data-val="${escapeHtml(v)}">
        <span>${escapeHtml(v)}</span>
        <button type="button" class="ms-pill-remove" aria-label="Remove ${escapeHtml(v)}">×</button>
      </span>
    `).join("");
    pillsEl.querySelectorAll(".ms-pill-remove").forEach((btn) => {
      btn.addEventListener("click", () => {
        _msState[rootId].selected.delete(btn.closest(".ms-pill").dataset.val);
        renderOptions(search.value);
        renderPills();
        renderTriggerLabel();
        triggerChange();
      });
    });
  }

  function renderTriggerLabel() {
    const sel = [..._msState[rootId].selected];
    trigger.querySelector(".ms-trigger-label").textContent =
      sel.length === 0 ? placeholder :
      sel.length === 1 ? sel[0] :
      `${sel.length} selected`;
  }

  function triggerChange() {
    root.dispatchEvent(new Event("ms-change", { bubbles: true }));
  }

  function openDropdown() {
    dropdown.classList.add("open");
    trigger.dataset.open = "true";
    trigger.setAttribute("aria-expanded", "true");
    search.value = "";
    renderOptions("");
    search.focus();
  }

  function closeDropdown() {
    dropdown.classList.remove("open");
    trigger.dataset.open = "false";
    trigger.setAttribute("aria-expanded", "false");
  }

  trigger.addEventListener("click", (e) => {
    e.stopPropagation();
    dropdown.classList.contains("open") ? closeDropdown() : openDropdown();
  });

  search.addEventListener("input", () => renderOptions(search.value));

  clearBtn.addEventListener("click", () => {
    _msState[rootId].selected.clear();
    renderOptions(search.value);
    renderPills();
    renderTriggerLabel();
    triggerChange();
  });

  dropdown.addEventListener("click", (e) => e.stopPropagation());

  document.addEventListener("click", () => closeDropdown());
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeDropdown(); });

  renderOptions("");
  renderPills();
}

function getMultiSelectValues(rootId) {
  return _msState[rootId] ? [..._msState[rootId].selected] : [];
}

function setMultiSelectValues(rootId, values) {
  if (!_msState[rootId]) return;
  _msState[rootId].selected = new Set(values || []);
  const root = document.getElementById(rootId);
  if (!root) return;
  const list  = root.querySelector(".ms-list");
  const pillsEl = root.querySelector(".ms-pills");
  const countEl = root.querySelector(".ms-count");
  const search = root.querySelector(".ms-search");
  const placeholder = root.dataset.placeholder || "Any";

  const sel = [..._msState[rootId].selected];
  countEl.textContent = sel.length ? `${sel.length} selected` : "";
  root.querySelector(".ms-trigger .ms-trigger-label").textContent =
    sel.length === 0 ? placeholder :
    sel.length === 1 ? sel[0] :
    `${sel.length} selected`;

  if (list) {
    const q = (search ? search.value : "").toLowerCase();
    const opts = _msState[rootId].allOptions.filter((o) => !q || o.toLowerCase().includes(q));
    list.innerHTML = opts.map((o) => {
      const checked = _msState[rootId].selected.has(o) ? "checked" : "";
      return `<label class="ms-option"><input type="checkbox" value="${escapeHtml(o)}" ${checked}><span>${escapeHtml(o)}</span></label>`;
    }).join("");
  }

  if (pillsEl) {
    pillsEl.innerHTML = sel.map((v) => `
      <span class="ms-pill" data-val="${escapeHtml(v)}">
        <span>${escapeHtml(v)}</span>
        <button type="button" class="ms-pill-remove" aria-label="Remove ${escapeHtml(v)}">×</button>
      </span>
    `).join("");
    pillsEl.querySelectorAll(".ms-pill-remove").forEach((btn) => {
      btn.addEventListener("click", () => {
        _msState[rootId].selected.delete(btn.closest(".ms-pill").dataset.val);
        if (list) {
          list.querySelectorAll("input[type=checkbox]").forEach((cb) => {
            if (cb.value === btn.closest(".ms-pill").dataset.val) cb.checked = false;
          });
        }
        setMultiSelectValues(rootId, [..._msState[rootId].selected]);
        root.dispatchEvent(new Event("ms-change", { bubbles: true }));
      });
    });
  }
}

function clearMultiSelect(rootId) {
  setMultiSelectValues(rootId, []);
}

function fillSelect(name, values) {
  const select = document.querySelector(`select[name="${name}"]`);
  if (!select) {
    return;
  }
  const firstOption = select.querySelector("option");
  select.innerHTML = "";
  select.appendChild(firstOption);
  values.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  });
}

function setSearchStatus(value) {
  const status = document.querySelector("#search-time");
  if (status) {
    status.textContent = value;
  }
}

function formatChartValue(value, style = "number") {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) {
    return String(value ?? "");
  }
  if (style === "score") {
    return numeric.toFixed(2);
  }
  return Number.isInteger(numeric) ? numeric.toLocaleString() : numeric.toFixed(2);
}

function formatPercent(value, total) {
  if (!total) {
    return "0%";
  }
  const percent = (Number(value) / Number(total)) * 100;
  if (!Number.isFinite(percent)) {
    return "0%";
  }
  return percent >= 10 ? `${percent.toFixed(0)}%` : `${percent.toFixed(1)}%`;
}

function slugify(value) {
  return String(value || "chart")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "") || "chart";
}

function excelColumnName(index) {
  let name = "";
  let number = Number(index) + 1;
  while (number > 0) {
    const remainder = (number - 1) % 26;
    name = String.fromCharCode(65 + remainder) + name;
    number = Math.floor((number - 1) / 26);
  }
  return name || "A";
}

function fileName(path) {
  return String(path || "").split(/[\\/]/).pop() || path;
}

function formatValue(value) {
  if (typeof value === "number") {
    return Number.isInteger(value) ? value.toLocaleString() : value.toFixed(2);
  }
  return escapeHtml(value);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function highlightText(text, query) {
  const raw = String(text ?? "");
  if (!query || !query.trim()) return escapeHtml(raw);
  const lower = raw.toLowerCase();
  const lq = query.toLowerCase().trim();
  let result = "";
  let i = 0;
  while (i < raw.length) {
    const idx = lower.indexOf(lq, i);
    if (idx === -1) { result += escapeHtml(raw.slice(i)); break; }
    result += escapeHtml(raw.slice(i, idx));
    result += `<mark class="search-hl">${escapeHtml(raw.slice(idx, idx + lq.length))}</mark>`;
    i = idx + lq.length;
  }
  return result;
}
