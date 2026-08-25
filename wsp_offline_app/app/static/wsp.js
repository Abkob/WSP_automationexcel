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
    initDashboardControls();
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
  if (activePath === "/student-profile") {
    initStudentProfilePage();
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
  initStudentContextMenu();

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

  const printProfileButton = document.querySelector("#print-student-profile");
  if (printProfileButton) printProfileButton.addEventListener("click", () => window.print());

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
let dashboardState = { data: null, activeTab: "overview", requestId: 0, optionsReady: false };
let dashboardFilterTimer = null;
const dashboardMultiSelects = {};
const dashboardMultiRoots = {
  faculty: "dashboard-ms-faculty",
  major: "dashboard-ms-major",
  class_year: "dashboard-ms-class",
};

function refreshActiveView() {
  if (activePath === "/") loadDashboard();
  if (activePath === "/filters") runSearch();
  if (activePath === "/excel-sheets") loadExcelSheets();
  if (activePath === "/student-profile") loadStudentProfile(document.body.dataset.studentId);
  if (activePath === "/import") loadImportCenter();
  if (activePath === "/system-status") loadSystemStatus();
}

async function loadDashboard() {
  const requestId = ++dashboardState.requestId;
  const loading = document.querySelector("#dashboard-loading");
  const content = document.querySelector("#dashboard-tab-content");
  if (loading) loading.hidden = false;
  content?.classList.add("is-refreshing");
  try {
    const query = new URLSearchParams(collectDashboardFilters());
    const response = await fetch(`/api/dashboard?${query.toString()}`);
    if (!response.ok) throw new Error("Dashboard data could not be loaded");
    const data = await response.json();
    if (requestId !== dashboardState.requestId) return;
    dashboardState.data = data;
    populateDashboardFilters(data);
    renderDashboardSelection(data);
    renderDashboardActiveView();
    syncDashboardUrl();
  } catch (error) {
    if (content) content.innerHTML = `<div class="dashboard-error-state"><strong>Dashboard unavailable</strong><span>${escapeHtml(error.message)}</span><button type="button" onclick="loadDashboard()">Try again</button></div>`;
  } finally {
    if (requestId === dashboardState.requestId) {
      if (loading) loading.hidden = true;
      content?.classList.remove("is-refreshing");
    }
  }
}

function initDashboardControls() {
  const form = document.querySelector("#dashboard-filter-form");
  if (!form || form.dataset.bound === "true") return;
  form.dataset.bound = "true";

  const params = new URLSearchParams(window.location.search);
  dashboardState.activeTab = params.get("view") || "overview";
  Object.keys(dashboardMultiRoots).forEach((key) => {
    initDashboardMultiSelect(key, () => {
      if (key === "faculty") updateDashboardMajorOptions();
      clearTimeout(dashboardFilterTimer);
      dashboardFilterTimer = setTimeout(loadDashboard, 450);
    });
    setDashboardMultiValues(key, splitDashboardFilterValue(params.get(key)));
  });
  const aidControl = form.elements.namedItem("aid");
  if (aidControl && params.has("aid")) aidControl.value = params.get("aid");

  form.addEventListener("change", (event) => {
    if (!event.target.matches("select")) return;
    loadDashboard();
  });
  form.addEventListener("input", (event) => {
    if (!event.target.matches("input")) return;
    clearTimeout(dashboardFilterTimer);
    dashboardFilterTimer = setTimeout(loadDashboard, 320);
  });

  document.querySelectorAll("[data-dashboard-tab]").forEach((button) => {
    button.addEventListener("click", () => {
      dashboardState.activeTab = button.dataset.dashboardTab;
      renderDashboardActiveView();
      syncDashboardUrl();
    });
  });
  document.querySelector("#dashboard-clear-filters")?.addEventListener("click", clearDashboardFilters);
  document.querySelector("#dashboard-toggle-filters")?.addEventListener("click", () => {
    const filterGrid = document.querySelector("#dashboard-filter-form");
    const button = document.querySelector("#dashboard-toggle-filters");
    const collapsed = filterGrid?.classList.toggle("is-collapsed") || false;
    if (button) {
      button.setAttribute("aria-expanded", String(!collapsed));
      button.innerHTML = `${collapsed ? "Show" : "Hide"} filters <span>${collapsed ? "⌄" : "⌃"}</span>`;
    }
  });
}

function splitDashboardFilterValue(value) {
  return String(value || "").split(",").map((item) => item.trim()).filter(Boolean);
}

function initDashboardMultiSelect(key, onChange) {
  const root = document.getElementById(dashboardMultiRoots[key]);
  if (!root || dashboardMultiSelects[key]) return;
  const placeholder = root.dataset.placeholder || "Any";
  const state = { options: [], selected: new Set(), onChange };
  dashboardMultiSelects[key] = state;
  root.innerHTML = `
    <button type="button" class="ms-trigger dashboard-ms-trigger" data-open="false" aria-haspopup="listbox" aria-expanded="false">
      <span class="ms-trigger-label">${escapeHtml(placeholder)}</span><span class="ms-trigger-arrow">▼</span>
    </button>
    <div class="ms-dropdown dashboard-ms-dropdown" role="listbox" aria-multiselectable="true">
      <input class="ms-search" type="search" placeholder="Search options…" autocomplete="off">
      <div class="ms-list"></div>
      <div class="ms-clear-row"><button type="button" class="ms-clear-btn">Clear selection</button><span class="ms-count"></span></div>
    </div>`;

  const trigger = root.querySelector(".ms-trigger");
  const dropdown = root.querySelector(".ms-dropdown");
  const search = root.querySelector(".ms-search");
  const list = root.querySelector(".ms-list");
  const count = root.querySelector(".ms-count");
  const optionLabel = (value) => state.options.find((option) => option.value === value)?.label || value;

  const renderTrigger = () => {
    const values = [...state.selected];
    trigger.querySelector(".ms-trigger-label").textContent = values.length === 0
      ? placeholder
      : values.length === 1
        ? optionLabel(values[0])
        : `${values.length} selected`;
    count.textContent = values.length ? `${values.length} selected` : "None selected";
    root.classList.toggle("has-selection", values.length > 0);
  };
  const renderOptions = () => {
    const query = String(search.value || "").trim().toLowerCase();
    const visible = state.options.filter((option) => !query || option.label.toLowerCase().includes(query));
    list.innerHTML = visible.length ? visible.map((option) => `
      <label class="ms-option"><input type="checkbox" value="${escapeHtml(option.value)}" ${state.selected.has(option.value) ? "checked" : ""}><span>${escapeHtml(option.label)}</span></label>`).join("")
      : `<div class="ms-empty">No matching options</div>`;
    list.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
      checkbox.addEventListener("change", () => {
        if (checkbox.checked) state.selected.add(checkbox.value);
        else state.selected.delete(checkbox.value);
        renderTrigger();
        state.onChange?.();
      });
    });
  };

  state.render = () => { renderTrigger(); renderOptions(); };
  state.setValues = (values, notify = false) => {
    const allowed = new Set(state.options.map((option) => option.value));
    const clean = [...new Set(values || [])].filter((value) => !allowed.size || allowed.has(value));
    state.selected = new Set(clean);
    state.render();
    if (notify) state.onChange?.();
  };
  state.setOptions = (options, preferredValues = null) => {
    state.options = (options || []).map((option) => typeof option === "string"
      ? { value: option, label: option }
      : { value: String(option.value), label: String(option.label || option.value) });
    state.setValues(preferredValues === null ? [...state.selected] : preferredValues);
  };

  const close = () => {
    dropdown.classList.remove("open");
    trigger.dataset.open = "false";
    trigger.setAttribute("aria-expanded", "false");
  };
  state.close = close;
  trigger.addEventListener("click", (event) => {
    event.stopPropagation();
    const opening = !dropdown.classList.contains("open");
    Object.values(dashboardMultiSelects).forEach((other) => other.close?.());
    if (opening) {
      dropdown.classList.add("open");
      trigger.dataset.open = "true";
      trigger.setAttribute("aria-expanded", "true");
      search.value = "";
      renderOptions();
      search.focus();
    }
  });
  search.addEventListener("input", renderOptions);
  root.querySelector(".ms-clear-btn").addEventListener("click", () => state.setValues([], true));
  dropdown.addEventListener("click", (event) => event.stopPropagation());
  document.addEventListener("click", close);
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") close(); });
  state.render();
}

function getDashboardMultiValues(key) {
  return dashboardMultiSelects[key] ? [...dashboardMultiSelects[key].selected] : [];
}

function setDashboardMultiValues(key, values, notify = false) {
  dashboardMultiSelects[key]?.setValues(values, notify);
}

function setDashboardMultiOptions(key, options, preferredValues = null) {
  dashboardMultiSelects[key]?.setOptions(options, preferredValues);
}

function collectDashboardFilters() {
  const form = document.querySelector("#dashboard-filter-form");
  if (!form) return {};
  const payload = {};
  Object.keys(dashboardMultiRoots).forEach((key) => {
    const values = getDashboardMultiValues(key);
    if (values.length) payload[key] = values.join(",");
  });
  const aid = String(form.elements.namedItem("aid")?.value || "any");
  if (aid !== "any") payload.aid = aid;
  return payload;
}

function populateDashboardFilters(data) {
  const form = document.querySelector("#dashboard-filter-form");
  if (!form) return;
  const current = Object.fromEntries(Object.keys(dashboardMultiRoots).map((key) => [key, getDashboardMultiValues(key)]));
  const faculties = data.filter_options?.faculties || [];
  const classes = data.filter_options?.classes || [];
  setDashboardMultiOptions("faculty", faculties.map((item) => ({
    value: item.code,
    label: `${item.code} · ${item.short_name} (${Number(item.count).toLocaleString()})`,
  })), current.faculty.length ? current.faculty : (data.selection?.faculty || []));
  setDashboardMultiOptions("class_year", classes, current.class_year.length ? current.class_year : (data.selection?.class_year || []));
  updateDashboardMajorOptions(current.major.length ? current.major : (data.selection?.major || []));
  dashboardState.optionsReady = true;
}

function updateDashboardMajorOptions(preferredValues = null) {
  const data = dashboardState.data;
  if (!data) return;
  const facultyCodes = getDashboardMultiValues("faculty");
  const current = preferredValues === null ? getDashboardMultiValues("major") : preferredValues;
  const facultyOptions = data.filter_options?.faculties || [];
  const majors = facultyCodes.length
    ? [...new Set(facultyOptions.filter((item) => facultyCodes.includes(item.code)).flatMap((item) => item.majors || []))].sort()
    : (data.filter_options?.majors || []);
  setDashboardMultiOptions("major", majors, current);
}

function clearDashboardFilters() {
  const form = document.querySelector("#dashboard-filter-form");
  if (!form) return;
  Object.keys(dashboardMultiRoots).forEach((key) => setDashboardMultiValues(key, []));
  form.elements.namedItem("aid").value = "any";
  updateDashboardMajorOptions([]);
  loadDashboard();
}

function syncDashboardUrl() {
  if (activePath !== "/") return;
  const params = new URLSearchParams(collectDashboardFilters());
  if (dashboardState.activeTab !== "overview") params.set("view", dashboardState.activeTab);
  const query = params.toString();
  window.history.replaceState({}, "", query ? `/?${query}` : "/");
}

function renderDashboardSelection(data) {
  renderDashboardFilterChips(data.selection || {});
}

function renderDashboardFilterChips(selection) {
  const target = document.querySelector("#dashboard-filter-chips");
  if (!target) return;
  const labels = {
    faculty: "Faculty",
    major: "Major",
    class_year: "Class",
    aid: "Aid",
  };
  const chips = Object.entries(selection).filter(([, value]) => Array.isArray(value) ? value.length : value !== null && value !== "" && value !== "any");
  const clearButton = document.querySelector("#dashboard-clear-filters");
  if (clearButton) clearButton.disabled = chips.length === 0;
  target.innerHTML = chips.length
    ? `<span>Active view</span>${chips.map(([key, value]) => `<button type="button" data-dashboard-clear="${escapeHtml(key)}"><strong>${escapeHtml(labels[key] || key)}</strong>${escapeHtml((Array.isArray(value) ? value.join(", ") : String(value)).replaceAll("_", " "))}<i>×</i></button>`).join("")}`
    : `<span class="dashboard-all-students-chip"><i></i>Showing the complete current applicant pool</span>`;
  target.querySelectorAll("[data-dashboard-clear]").forEach((button) => {
    button.addEventListener("click", () => {
      const key = button.dataset.dashboardClear;
      if (dashboardMultiRoots[key]) setDashboardMultiValues(key, []);
      else {
        const control = document.querySelector("#dashboard-filter-form")?.elements.namedItem(key);
        if (control) control.value = "any";
      }
      if (key === "faculty") updateDashboardMajorOptions([]);
      loadDashboard();
    });
  });
}

function renderDashboardActiveView() {
  const data = dashboardState.data;
  const target = document.querySelector("#dashboard-tab-content");
  if (!data || !target) return;
  document.querySelectorAll("[data-dashboard-tab]").forEach((button) => {
    button.classList.toggle("active", button.dataset.dashboardTab === dashboardState.activeTab);
    button.setAttribute("aria-selected", String(button.dataset.dashboardTab === dashboardState.activeTab));
  });

  const views = {
    overview: renderDashboardOverview,
    academics: renderDashboardAcademics,
    workstudy: renderDashboardWorkStudy,
    support: renderDashboardSupport,
    quality: renderDashboardQuality,
  };
  (views[dashboardState.activeTab] || renderDashboardOverview)(target, data);
}

function renderDashboardOverview(target, data) {
  const metrics = data.metrics || {};
  target.innerHTML = `
    ${renderDashboardKpis([
      { label: "Candidate pool", value: metrics.total_students, detail: data.selection_label || "All current applicants", tone: "aub", glyph: "CP" },
      { label: "Previous experience", value: metrics.experience_count, detail: `${numberPercent(metrics.experience_rate)} described prior work`, tone: "teal", glyph: "EX", progress: metrics.experience_rate },
      { label: "Receiving financial aid", value: metrics.financial_aid_count, detail: `${numberPercent(metrics.financial_aid_rate)} of the candidate pool`, tone: "blue", glyph: "FA", action: "aid:yes", progress: metrics.financial_aid_rate },
      { label: "Dorm residents", value: metrics.dorm_count, detail: `${numberPercent(metrics.dorm_rate)} of the candidate pool`, tone: "gold", glyph: "DR", progress: metrics.dorm_rate },
    ])}
    <section class="dashboard-section-block dashboard-talent-section">
      ${dashboardSectionHead("What applicants can contribute", "A quick view of the strongest skill and role-interest signals in the current candidate pool.", "Talent snapshot")}
      <div class="dashboard-signal-grid">
        ${renderDashboardSignalBoard("Top technical skill areas", "Skills", data.charts.technical_skills, "candidates")}
        ${renderDashboardSignalBoard("Preferred work areas", "Interests", data.charts.work_preferences, "candidates")}
      </div>
    </section>
    ${renderDashboardFacultyComparison(data)}
    ${renderDashboardStudentPanel(data, "Candidate directory", "Open a profile to review the applicant’s original skills, optional experience, and preferred work.", "candidate", data.candidate_students)}
    <div id="latest-import"></div>
  `;
  renderLatestImport(data.latest_import);
  bindDashboardInteractions(target);
}

function renderDashboardAcademics(target, data) {
  const metrics = data.metrics || {};
  target.innerHTML = `
    ${renderDashboardKpis([
      { label: "Candidates", value: metrics.total_students, detail: data.selection_label || "Current pool", tone: "aub", glyph: "CP" },
      { label: "Prior work experience", value: metrics.experience_count, detail: `${numberPercent(metrics.experience_rate)} describe previous experience`, tone: "blue", glyph: "EX", progress: metrics.experience_rate },
      { label: "Majors represented", value: metrics.major_count, detail: "Academic backgrounds in this pool", tone: "gold", glyph: "MJ" },
      { label: "Class levels", value: metrics.class_count, detail: "Student stages represented in this pool", tone: "teal", glyph: "CL" },
    ])}
    <section class="dashboard-section-block">
      ${dashboardSectionHead("Who is in the candidate pool", "Explore applicants by academic home and stage, then open any profile for placement details.", "Candidate composition")}
      <div id="dashboard-academic-charts" class="chart-grid dashboard-chart-grid"></div>
    </section>
    ${renderDashboardStudentPanel(data, "Candidate directory", "Browse applicant profiles here, or use Search & Match for a specific role request.", "candidate", data.candidate_students)}
  `;
  renderChartGrid("dashboard-academic-charts", [
    { title: "Candidates by major", eyebrow: "Academic background", type: "ranked-bars", points: data.charts.students_by_major, unit: "candidates", limit: 8, filterKey: "major" },
    { title: "Candidates by class", eyebrow: "Student stage", type: "ranked-bars", points: data.charts.students_by_class, unit: "candidates", limit: 8, filterKey: "class_year" },
    { title: "Prior experience by faculty", eyebrow: "Experience coverage", type: "percent-bars", points: data.charts.experience_rate_by_faculty, unit: "%", limit: 7, filterKey: "faculty" },
    { title: "Financial aid by faculty", eyebrow: "Funding context", type: "percent-bars", points: data.charts.aid_rate_by_faculty, unit: "%", limit: 7, filterKey: "faculty" },
  ]);
  bindDashboardInteractions(target);
}

function renderDashboardWorkStudy(target, data) {
  const metrics = data.metrics || {};
  const grouping = data.preferred_work_grouping || {};
  const skillGrouping = data.technical_skill_grouping || {};
  target.innerHTML = `
    ${renderDashboardKpis([
      { label: "Skill signals", value: skillGrouping.skill_topic_mentions || 0, detail: "Technical skill mentions grouped locally", tone: "aub", glyph: "SK" },
      { label: "Work preferences", value: metrics.work_preference_count, detail: `${numberPercent(metrics.work_preference_rate)} include a preferred area`, tone: "blue", glyph: "WP", progress: metrics.work_preference_rate },
      { label: "With experience", value: metrics.experience_count, detail: `${numberPercent(metrics.experience_rate)} include previous work`, tone: "teal", glyph: "EX", progress: metrics.experience_rate },
      { label: "Signals to review", value: Number(grouping.review_count || 0) + Number(skillGrouping.review_count || 0), detail: "Uncertain skill or preference groupings", tone: (Number(grouping.review_count || 0) + Number(skillGrouping.review_count || 0)) ? "warn" : "good", glyph: "RV" },
    ])}
    <section class="dashboard-section-block">
      ${dashboardSectionHead("Skills and role interests", "Similar free-text answers are organized into clear placement signals while every applicant’s original wording stays intact.", "Matching intelligence")}
      <details class="dashboard-method-note ${grouping.method === "review_fallback" || skillGrouping.method === "review_fallback" ? "warning" : ""}">
        <summary><span class="dashboard-grouping-orb">AI</span><div><strong>How local grouping works</strong><small>Original answers stay untouched; embeddings organize similar wording for overview charts.</small></div><b>Details</b></summary>
        <div class="dashboard-method-detail">
      <div class="dashboard-grouping-note ${grouping.method === "review_fallback" ? "warning" : ""}">
        <span class="dashboard-grouping-orb">AI</span>
        <div><strong>${grouping.method === "review_fallback" ? "Grouping needs attention" : "Grouped locally with offline embeddings"}</strong><small>${escapeHtml(String(grouping.model || "Offline model").split("/").pop())} · no student text is rewritten</small></div>
        <dl><div><dt>${Number(grouping.assigned_count || 0).toLocaleString()}</dt><dd>Assigned</dd></div><div><dt>${Number(grouping.flexible_count || 0).toLocaleString()}</dt><dd>Flexible</dd></div><div><dt>${Number(grouping.emerging_field_count || 0).toLocaleString()}</dt><dd>Emerging fields</dd></div><div><dt>${Number(grouping.review_count || 0).toLocaleString()}</dt><dd>Needs review</dd></div></dl>
      </div>
      <div class="dashboard-grouping-note ${skillGrouping.method === "review_fallback" ? "warning" : ""}">
        <span class="dashboard-grouping-orb">SK</span>
        <div><strong>${skillGrouping.method === "review_fallback" ? "Skill grouping needs attention" : "Technical skills compared across students"}</strong><small>Repeated rough phrases and spelling variants can form dynamic skill topics</small></div>
        <dl><div><dt>${Number(skillGrouping.mapped_count || 0).toLocaleString()}</dt><dd>Mapped terms</dd></div><div><dt>${Number(skillGrouping.emerging_topic_count || 0).toLocaleString()}</dt><dd>Dynamic topics</dd></div><div><dt>${Number(skillGrouping.review_count || 0).toLocaleString()}</dt><dd>Needs review</dd></div></dl>
      </div>
        </div>
      </details>
      <div class="dashboard-signal-grid dashboard-signal-grid-wide">
        ${renderDashboardSignalBoard("Technical skill areas", "Skills", data.charts.technical_skills, "candidates", 10)}
        ${renderDashboardSignalBoard("Preferred work areas", "Interests", data.charts.work_preferences, "candidates", 10)}
      </div>
    </section>
    ${renderDashboardStudentPanel(data, "Applicant talent directory", "Review each applicant’s preferred work area and original response. Previous experience remains optional context.", "work", data.workstudy_students)}
  `;
  bindDashboardInteractions(target);
}

function renderDashboardSupport(target, data) {
  const metrics = data.metrics || {};
  const withoutAid = Math.max(0, Number(metrics.total_students || 0) - Number(metrics.financial_aid_count || 0));
  target.innerHTML = `
    ${renderDashboardKpis([
      { label: "Receiving financial aid", value: metrics.financial_aid_count, detail: `${numberPercent(metrics.financial_aid_rate)} of this pool`, tone: "aub", glyph: "FA", action: "aid:yes", progress: metrics.financial_aid_rate },
      { label: "No aid flag", value: withoutAid, detail: `${numberPercent(100 - Number(metrics.financial_aid_rate || 0))} of this pool`, tone: "blue", glyph: "NA", action: "aid:no", progress: 100 - Number(metrics.financial_aid_rate || 0) },
      { label: "Dorm residents", value: metrics.dorm_count, detail: `${numberPercent(metrics.dorm_rate)} may need location-aware roles`, tone: "teal", glyph: "DR", progress: metrics.dorm_rate },
      { label: "Aid + dorm", value: metrics.aid_dorm_count, detail: "Applicants with both support indicators", tone: "gold", glyph: "AD" },
    ])}
    <section class="dashboard-section-block">
      ${dashboardSectionHead("Funding and logistics context", "Use these indicators to understand support and location context during placement—never as a measure of candidate quality.", "Applicant context")}
      <div id="dashboard-support-charts" class="chart-grid dashboard-chart-grid"></div>
    </section>
    ${renderDashboardStudentPanel(data, "Funding and housing directory", "Aid recipients and dorm residents are grouped for placement logistics and program coordination.", "support", data.support_students)}
  `;
  renderChartGrid("dashboard-support-charts", [
    { title: "Aid rate by faculty", eyebrow: "Financial aid coverage", type: "percent-bars", points: data.charts.aid_rate_by_faculty, unit: "%", limit: 7, filterKey: "faculty" },
    { title: "Dorm rate by faculty", eyebrow: "Housing coverage", type: "percent-bars", points: data.charts.dorm_rate_by_faculty, unit: "%", limit: 7, filterKey: "faculty" },
    { title: "Aid rate by class", eyebrow: "Progression context", type: "percent-bars", points: data.charts.aid_rate_by_class, unit: "%", limit: 8, filterKey: "class_year" },
  ]);
  bindDashboardInteractions(target);
}

function renderDashboardQuality(target, data) {
  const quality = data.quality || {};
  const issues = [
    ["Missing email", quality.missing_email, "Contact students reliably", "EM"],
    ["Missing mobile", quality.missing_mobile, "Complete contact records", "MB"],
    ["Missing major", quality.missing_major, "Resolve academic ownership", "MJ"],
    ["Missing technical skills", quality.missing_skills, "Improve candidate matching", "SK"],
    ["Missing work preference", quality.missing_work_preference, "Improve placement relevance", "WP"],
    ["Unmapped faculty", quality.unmapped_faculty, "Review major-to-faculty mapping", "FM"],
    ["Inactive historical records", quality.inactive_records, "Retained outside the active population", "HI"],
  ].sort((a, b) => Number(b[1] || 0) - Number(a[1] || 0));
  target.innerHTML = `
    ${renderDashboardKpis([
      { label: "Core records complete", value: quality.complete_records || 0, detail: `${numberPercent(quality.complete_rate)} of this population`, tone: "good", glyph: "OK", progress: quality.complete_rate },
      { label: "Records with gaps", value: quality.missing_any_core || 0, detail: "Missing at least one required profile field", tone: quality.missing_any_core ? "warn" : "good", glyph: "DQ" },
      { label: "Unmapped faculty", value: quality.unmapped_faculty || 0, detail: "Majors retained safely outside a faculty", tone: quality.unmapped_faculty ? "warn" : "good", glyph: "FM" },
      { label: "Inactive history", value: quality.inactive_records || 0, detail: "Records absent from the latest import", tone: "blue", glyph: "HI" },
    ])}
    <section class="dashboard-quality-layout">
      <article class="dashboard-section-block">
        ${dashboardSectionHead("Field completion", "Sorted from the weakest field upward so cleanup priorities are immediate.", "Completeness")}
        <div id="dashboard-quality-charts" class="chart-grid dashboard-chart-grid"></div>
      </article>
      <article class="dashboard-issue-panel">
        <div class="dashboard-issue-head"><div><p class="eyebrow">Cleanup queue</p><h2>Issues by impact</h2><span>Counts update with the dashboard filters.</span></div><a href="/excel-sheets">Open Data Explorer →</a></div>
        <div class="dashboard-issue-list">${issues.map(([label, value, detail, glyph]) => `<div class="dashboard-issue-row ${Number(value || 0) === 0 ? "clear" : ""}"><span>${escapeHtml(glyph)}</span><div><strong>${escapeHtml(label)}</strong><small>${escapeHtml(detail)}</small></div><b>${Number(value || 0).toLocaleString()}</b></div>`).join("")}</div>
      </article>
    </section>
    ${renderDashboardStudentPanel(data, "Records to inspect", "Records with the most missing core fields appear first.", "quality", data.quality_students, "No active records need core-field or faculty-mapping cleanup in this view.")}
    <div id="latest-import"></div>
  `;
  renderChartGrid("dashboard-quality-charts", [
    { title: "Completion by field", eyebrow: "Weakest first", type: "percent-bars", points: data.charts.data_completeness, unit: "%", limit: 6 },
  ]);
  renderLatestImport(data.latest_import);
  bindDashboardInteractions(target);
}

function renderDashboardKpis(items) {
  return `<section class="dashboard-kpi-grid" aria-label="Key indicators">${items.map((item) => `
    <${item.action ? "button" : "article"} class="dashboard-kpi-card ${escapeHtml(item.tone || "aub")} ${item.action ? "is-action" : ""}" ${item.action ? `type="button" data-dashboard-action="${escapeHtml(item.action)}"` : ""}>
      <span class="dashboard-kpi-glyph">${escapeHtml(item.glyph || "•")}</span>
      <div class="dashboard-kpi-copy"><small>${escapeHtml(item.label)}</small><strong>${typeof item.value === "number" ? item.value.toLocaleString() : escapeHtml(item.value)}</strong><p>${escapeHtml(item.detail || "")}</p></div>
      <div class="dashboard-kpi-progress"><i style="width:${Math.max(0, Math.min(100, Number(item.progress || 0)))}%"></i></div>
      ${item.action ? `<span class="dashboard-kpi-arrow">View ↗</span>` : ""}
    </${item.action ? "button" : "article"}>`).join("")}</section>`;
}

function renderDashboardSignalBoard(title, eyebrow, rawPoints, unit = "candidates", limit = 6) {
  const points = normalizePoints(rawPoints).slice(0, limit);
  const maximum = Math.max(1, ...points.map((point) => point.value));
  return `<article class="dashboard-signal-board">
    <header><div><span>${escapeHtml(eyebrow)}</span><h3>${escapeHtml(title)}</h3></div><small>${points.length} visible areas</small></header>
    ${points.length ? `<ol>${points.map((point, index) => `<li>
      <span class="dashboard-signal-rank">${String(index + 1).padStart(2, "0")}</span>
      <div><strong>${escapeHtml(point.label)}</strong><i><b style="width:${Math.max(4, (point.value / maximum) * 100)}%;--signal-color:${escapeHtml(point.color || "#840132")}"></b></i><small>${escapeHtml(point.detail || "Grouped from original applicant text")}</small></div>
      <em>${Number(point.value).toLocaleString()} <small>${escapeHtml(unit)}</small></em>
    </li>`).join("")}</ol>` : `<p class="empty-state">No applicant signals are available for this view.</p>`}
  </article>`;
}

function renderDashboardFacultyComparison(data) {
  const selected = data.selection?.faculty || [];
  const all = data.faculty_summary || [];
  const faculties = all.filter((faculty) => Number(faculty.count || 0) > 0);
  const hidden = all.length - faculties.length;
  return `<section class="dashboard-section-block dashboard-faculty-comparison">
    ${dashboardSectionHead("Candidate context by faculty", "Compare candidate volume, previous experience, financial aid, and housing context in one view.", "Candidate coverage")}
    <div class="dashboard-faculty-table-wrap"><table class="dashboard-faculty-table"><thead><tr><th>Faculty</th><th>Candidates</th><th>Prior experience</th><th>Aid context</th><th>Dorm context</th><th></th></tr></thead><tbody>${faculties.map((faculty) => `
      <tr class="${selected.includes(faculty.code) ? "selected" : ""}">
        <td><span style="--faculty-color:${escapeHtml(faculty.color)}">${escapeHtml(faculty.code)}</span><div><strong>${escapeHtml(faculty.short_name)}</strong><small>${Number(faculty.major_count || 0)} represented majors</small></div></td>
        <td><strong>${Number(faculty.count).toLocaleString()}</strong><small>${numberPercent(faculty.share)} of view</small></td>
        <td><strong>${numberPercent(faculty.experience_rate)}</strong><small>${Number(faculty.experience_count).toLocaleString()} candidates</small></td>
        <td><strong>${numberPercent(faculty.aid_rate)}</strong><small>${Number(faculty.aid_count).toLocaleString()} students</small></td>
        <td><strong>${numberPercent(faculty.dorm_rate)}</strong><small>${Number(faculty.dorm_count).toLocaleString()} students</small></td>
        <td><button type="button" data-dashboard-faculty="${escapeHtml(faculty.code)}" aria-label="${selected.includes(faculty.code) ? "Remove" : "Add"} ${escapeHtml(faculty.short_name)}">${selected.includes(faculty.code) ? "Remove" : "Add"} →</button></td>
      </tr>`).join("")}</tbody></table></div>
    ${hidden ? `<p class="dashboard-zero-note">${hidden} facult${hidden === 1 ? "y has" : "ies have"} no records in this population and ${hidden === 1 ? "is" : "are"} hidden.</p>` : ""}
  </section>`;
}

function renderDashboardStudentPanel(data, title, description, mode = "status", selectedRows = null, emptyText = "No students match this view.") {
  const rows = selectedRows || data.students || [];
  const detailHeader = mode === "work" ? "Placement profile" : mode === "quality" ? "Data gaps" : mode === "support" ? "Funding / housing" : "Preferred work";
  const detailCell = (student) => {
    if (mode === "candidate") return `<td class="dashboard-work-cell"><span class="dashboard-work-group" style="--work-color:${escapeHtml(student.work_preference_group_color || "#64748B")}">${escapeHtml(student.work_preference_group)}</span><small title="${escapeHtml(student.work_preference)}">${escapeHtml(student.work_preference)}</small></td>`;
    if (mode === "work") return `<td class="dashboard-work-cell"><span class="dashboard-work-group" style="--work-color:${escapeHtml(student.work_preference_group_color || "#64748B")}">${escapeHtml(student.work_preference_group)}</span><small title="${escapeHtml(student.work_preference)}">${escapeHtml(student.work_preference)}</small></td>`;
    if (mode === "quality") return `<td><span class="dashboard-row-status ${student.core_missing_count ? "attention" : "clear"}">${student.core_missing_count ? `${Number(student.core_missing_count)} core fields missing` : "Complete"}</span></td>`;
    if (mode === "support") return `<td><span class="dashboard-row-status ${student.financial_aid || student.dorms ? "context" : "clear"}">${student.financial_aid ? "Aid" : "No aid flag"} · ${student.dorms ? "Dorm" : "No dorm flag"}</span></td>`;
    return `<td class="dashboard-work-cell"><span class="dashboard-work-group" style="--work-color:${escapeHtml(student.work_preference_group_color || "#64748B")}">${escapeHtml(student.work_preference_group)}</span><small title="${escapeHtml(student.work_preference)}">${escapeHtml(student.work_preference)}</small></td>`;
  };
  return `<section class="dashboard-student-panel">
    <div class="dashboard-student-head">
      <div><p class="eyebrow">Applicant drill-through</p><h2>${escapeHtml(title)}</h2><span>${escapeHtml(description)}</span></div>
      <a href="/filters" class="dashboard-view-all">Open Search & Match <b>→</b></a>
    </div>
    <div class="dashboard-student-table-wrap"><table class="dashboard-student-table">
      <thead><tr><th>Candidate</th><th>Faculty / major</th><th>Class</th><th>Experience</th><th>${escapeHtml(detailHeader)}</th><th></th></tr></thead>
      <tbody>${rows.length ? rows.map((student) => `<tr data-student-id="${escapeHtml(student.student_id)}">
        <td><a href="/student-profile/${encodeURIComponent(student.student_id)}"><span class="dashboard-student-avatar" style="--student-color:${escapeHtml(student.faculty_color)}">${escapeHtml(profileInitials(student.name))}</span><span><strong>${escapeHtml(student.name)}</strong><small>${escapeHtml(student.student_id)}</small></span></a></td>
        <td><span class="dashboard-faculty-tag" style="--student-color:${escapeHtml(student.faculty_color)}">${escapeHtml(student.faculty)}</span><small>${escapeHtml(student.major)}</small></td>
        <td>${escapeHtml(student.class_year)}</td><td><span class="dashboard-experience-state ${student.has_experience ? "yes" : "no"}">${student.has_experience ? "Provided" : "Not provided"}</span></td>
        ${detailCell(student)}
        <td><a class="dashboard-row-arrow" href="/student-profile/${encodeURIComponent(student.student_id)}" aria-label="Open ${escapeHtml(student.name)} profile">→</a></td>
      </tr>`).join("") : `<tr><td colspan="6" class="empty-state">${escapeHtml(emptyText)}</td></tr>`}</tbody>
    </table></div>
    <div class="dashboard-student-foot"><span>${mode === "quality" ? `${rows.length.toLocaleString()} active records require inspection` : `Showing ${rows.length.toLocaleString()} candidates from ${Number(data.total_matches || 0).toLocaleString()} matching applicants`}</span><small>Right-click any row for profile actions.</small></div>
  </section>`;
}

function dashboardSectionHead(title, description, label) {
  return `<div class="dashboard-section-head"><div><p class="eyebrow">${escapeHtml(label)}</p><h2>${escapeHtml(title)}</h2><span>${escapeHtml(description)}</span></div><span class="dashboard-section-mark">AUB · WSP</span></div>`;
}

function bindDashboardInteractions(root) {
  root.querySelectorAll("[data-dashboard-faculty]").forEach((button) => {
    button.addEventListener("click", () => applyDashboardFilter("faculty", button.dataset.dashboardFaculty));
  });
  root.querySelectorAll("[data-dashboard-action]").forEach((button) => {
    button.addEventListener("click", () => handleDashboardAction(button.dataset.dashboardAction));
  });
  bindStudentProfileActions(root);
}

function handleDashboardAction(action) {
  if (!action) return;
  if (action === "clear") return clearDashboardFilters();
  const [key, value] = action.split(":");
  if (key === "tab") {
    dashboardState.activeTab = value;
    renderDashboardActiveView();
    syncDashboardUrl();
    return;
  }
  applyDashboardFilter(key, value);
}

function applyDashboardFilter(key, value) {
  const form = document.querySelector("#dashboard-filter-form");
  if (!form) return;
  if (dashboardMultiRoots[key]) {
    const values = getDashboardMultiValues(key);
    const next = values.includes(value) ? values.filter((item) => item !== value) : [...values, value];
    setDashboardMultiValues(key, next);
    if (key === "faculty") updateDashboardMajorOptions();
  } else {
    const control = form.elements.namedItem(key);
    if (!control) return;
    control.value = control.value === value ? "any" : value;
  }
  loadDashboard();
  document.querySelector("#dashboard-filter-shell")?.scrollIntoView?.({ behavior: "smooth", block: "start" });
}

function handleDashboardChartSelection(filterKey, value) {
  applyDashboardFilter(filterKey, value);
}

function metricNumber(value, decimals = 0) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return Number(value).toFixed(decimals);
}

function numberPercent(value) {
  return `${Number(value || 0).toFixed(1)}%`;
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
    if (btn) { btn.style.display = ""; btn.disabled = false; btn.textContent = "Re-embed All"; }
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
    await fetch("/api/admin/reindex?force=true", { method: "POST" });
  } catch (_) { /* server will reindex anyway */ }
  clearTimeout(_coveragePoller);
  _coveragePoller = setTimeout(refreshIndexCoverage, 2000);
}

let activeSearchController = null;
let searchProgressTimer = null;
let searchProgressHideTimer = null;
let searchRequestSequence = 0;

function startSearchProgress(usesSemanticSearch) {
  const progress = document.querySelector("#ai-search-progress");
  const title = document.querySelector("#ai-search-progress-title");
  const detail = document.querySelector("#ai-search-progress-detail");
  const panel = document.querySelector(".results-panel");
  if (!progress || !title || !detail) return;

  const stages = usesSemanticSearch
    ? [
        ["Understanding your search", "Reading the request and active filters"],
        ["Searching the local AI index", "Comparing relevant student profiles on this computer"],
        ["Ranking the strongest matches", "Scoring fit against skills and preferred work"],
        ["Preparing your results", "Adding a concise explanation for each match"],
      ]
    : [
        ["Applying your filters", "Checking the local student database"],
        ["Sorting matching students", "Organizing the strongest results first"],
        ["Preparing your results", "Building the results table"],
      ];

  clearInterval(searchProgressTimer);
  clearTimeout(searchProgressHideTimer);
  progress.hidden = false;
  progress.classList.remove("complete", "failed");
  panel?.setAttribute("aria-busy", "true");
  let stageIndex = 0;
  const showStage = () => {
    title.textContent = stages[stageIndex][0];
    detail.textContent = stages[stageIndex][1];
    stageIndex = Math.min(stageIndex + 1, stages.length - 1);
  };
  showStage();
  searchProgressTimer = setInterval(showStage, 650);
}

function finishSearchProgress(message, failed = false) {
  const progress = document.querySelector("#ai-search-progress");
  const title = document.querySelector("#ai-search-progress-title");
  const detail = document.querySelector("#ai-search-progress-detail");
  const panel = document.querySelector(".results-panel");
  clearInterval(searchProgressTimer);
  if (!progress || !title || !detail) return;

  progress.classList.toggle("failed", failed);
  progress.classList.toggle("complete", !failed);
  title.textContent = failed ? "Search could not finish" : "Matches ready";
  detail.textContent = message;
  panel?.removeAttribute("aria-busy");
  searchProgressHideTimer = setTimeout(() => {
    progress.hidden = true;
    progress.classList.remove("complete", "failed");
  }, failed ? 1800 : 650);
}

async function runSearch() {
  const payload = collectSearchPayload();
  const started = performance.now();
  const requestSequence = ++searchRequestSequence;
  if (activeSearchController) activeSearchController.abort();
  activeSearchController = new AbortController();
  setSearchStatus("Searching…");
  startSearchProgress(Boolean(payload.semantic_query));

  try {
    const response = await fetch("/api/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: activeSearchController.signal,
    });
    if (!response.ok) {
      throw new Error(await response.text());
    }
    const data = await response.json();
    if (requestSequence !== searchRequestSequence) return;
    const elapsed = ((performance.now() - started) / 1000).toFixed(2);
    renderResults(data.rows);
    renderActiveFilterTags(payload);
    document.querySelector("#result-count").textContent = `${data.total_count.toLocaleString()} results`;
    setSearchStatus(`${elapsed}s`);
    document.querySelector("#export-status").textContent = "";
    finishSearchProgress(`${data.total_count.toLocaleString()} students found in ${elapsed}s`);
  } catch (error) {
    if (error.name === "AbortError") return;
    setSearchStatus("Search failed");
    finishSearchProgress("Please try the search again.", true);
    console.error("Student search failed", error);
  }
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
  const editMode = sheet.key === "Student_Directory" && sheetState.editMode;

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
        const isStudentSheet = sheet.key === "Student_Directory";
        const cells = (sheet.headers || []).map((_, colIndex) => {
          const val = row[colIndex] ?? "";
          const content = isStudentSheet && !editMode && (colIndex === 0 || colIndex === 1)
            ? `<a class="student-profile-link" href="/student-profile/${encodeURIComponent(String(row[0] || ""))}" title="Open student profile">${highlightText(val, query)}</a>`
            : highlightText(val, query);
          return `<td>${content}</td>`;
        }).join("");
        const studentAttr = isStudentSheet ? ` data-student-id="${escapeHtml(row[0] || "")}"` : "";
        return `<tr data-row-index="${rowIndex}"${studentAttr}><td>${originalRowIndex + 1}</td>${cells}</tr>`;
      }).join("") || `<tr><td colspan="${(sheet.headers || []).length + 1}" class="empty-state">No rows match <strong>${escapeHtml(query)}</strong>.</td></tr>`}
    </tbody>
  `;
  bindStudentProfileActions(table);
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
          const content = isStudentSheet && (colIndex === 0 || colIndex === 1)
            ? `<a class="student-profile-link" href="/student-profile/${encodeURIComponent(String(row[0] || ""))}" title="Open student profile">${highlightText(row[colIndex] ?? "", query)}</a>`
            : highlightText(row[colIndex] ?? "", query);
          return `<td tabindex="0" data-cell="${cellId}" class="${hasEdit ? "cell-edited" : ""}">${content}</td>`;
        }).join("");
        const studentAttr = isStudentSheet && !editMode ? ` data-student-id="${escapeHtml(row[0] || "")}"` : "";
        return `<tr data-row-index="${rowIndex}"${studentAttr}>${`<td>${rowIndex + 1}</td>`}${cells}</tr>`;
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
    bindStudentProfileActions(table);
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

  target.querySelectorAll("[data-single-chart-filter]").forEach((spotlight) => {
    const activate = () => handleDashboardChartSelection(spotlight.dataset.singleChartFilter, spotlight.dataset.singleChartValue);
    spotlight.addEventListener("click", activate);
    spotlight.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        activate();
      }
    });
  });

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
    eyebrow: spec.eyebrow || "Analysis",
    type: spec.type || "ranked-bars",
    points: spec.points || [],
    unit: spec.unit || "records",
    limit: spec.limit || 8,
    filterKey: spec.filterKey || "",
  };
}

function normalizePoints(points) {
  return (points || []).map((point) => ({
    label: String(point.label || "Unknown"),
    value: Number(point.value) || 0,
    color: point.color || "",
    detail: point.detail || "",
  }));
}

function renderChartCard(spec, index) {
  const canvasId = `chart-canvas-${index}`;
  const allPoints = normalizePoints(spec.points);
  const visible = allPoints.slice(0, spec.limit);
  const topPoint = findTopPoint(visible);
  const total = chartTotal(allPoints, spec);
  const summary = chartSummary(spec, visible, allPoints);
  const isSingle = visible.length === 1;
  const pill = isSingle ? "" : renderChartStatPill(spec, topPoint, total);
  const chartBody = isSingle ? renderSinglePointSpotlight(spec, visible[0], total) : `
      <div class="chart-canvas-wrap">
        <canvas id="${escapeHtml(canvasId)}" role="img" aria-label="${escapeHtml(spec.title)}"></canvas>
      </div>`;

  return `
    <article class="chart-card ${isSingle ? "is-single-point" : ""} ${spec.filterKey ? "is-interactive" : ""}" aria-label="${escapeHtml(spec.title)}">
      <div class="chart-head">
        <div>
          <span class="chart-eyebrow">${escapeHtml(spec.eyebrow || "Analysis")}</span>
          <h3>${escapeHtml(spec.title)}</h3>
          <p>${escapeHtml(summary)}</p>
        </div>
        ${pill}
      </div>
      ${chartBody}
      ${spec.filterKey ? `<div class="chart-interaction-hint"><span>Click a value to filter the dashboard</span><b>↗</b></div>` : ""}
    </article>
  `;
}

function renderSinglePointSpotlight(spec, point, total) {
  const maximum = spec.type === "score-bars" ? 4 : spec.type === "percent-bars" ? 100 : Math.max(1, total);
  const progress = Math.max(0, Math.min(100, (Number(point.value) / maximum) * 100));
  const value = spec.type === "percent-bars"
    ? `${Number(point.value).toFixed(1)}%`
    : spec.type === "score-bars"
      ? Number(point.value).toFixed(2)
      : Number(point.value).toLocaleString();
  const context = spec.type === "percent-bars"
    ? `${Number(point.value).toFixed(1)}% rate in the selected group`
    : spec.type === "score-bars"
      ? `${Number(point.value).toFixed(2)} out of 4.00`
      : `100% of this chart’s current view`;
  const interaction = spec.filterKey
    ? `data-single-chart-filter="${escapeHtml(spec.filterKey)}" data-single-chart-value="${escapeHtml(point.label)}" role="button" tabindex="0"`
    : "";
  return `<div class="chart-single-spotlight ${spec.filterKey ? "is-clickable" : ""}" ${interaction} style="--single-progress:${progress * 3.6}deg;--single-color:${escapeHtml(point.color || "#840132")}">
    <div class="chart-single-orbit"><div><strong>${escapeHtml(value)}</strong><small>${escapeHtml(spec.unit)}</small></div></div>
    <div class="chart-single-copy"><span>Focused selection</span><strong>${escapeHtml(point.label)}</strong><p>${escapeHtml(context)}</p><small>Only one group remains after the current filters.</small></div>
  </div>`;
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
  const pointColors = points.map((point) => point.color || "#840132");

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
        if (spec.type === "percent-bars") return ` ${Number(item.raw).toFixed(1)}%`;
        const pct = valueTotal > 0 ? ` (${((item.raw / valueTotal) * 100).toFixed(1)}%)` : "";
        return ` ${Number(item.raw).toLocaleString()} ${spec.unit}${pct}`;
      },
      afterLabel: (item) => points[item.dataIndex]?.detail || "",
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
          backgroundColor: points.some((point) => point.color) ? pointColors : "#840132",
          hoverBackgroundColor: points.some((point) => point.color) ? pointColors : "#a3193f",
          borderRadius: 5,
          borderSkipped: false,
        }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        animation: animIn,
        onClick: (_event, elements) => {
          if (spec.filterKey && elements[0]) handleDashboardChartSelection(spec.filterKey, points[elements[0].index]?.label);
        },
        onHover: (event, elements) => { event.native.target.style.cursor = spec.filterKey && elements.length ? "pointer" : "default"; },
        plugins: { legend: { display: false }, tooltip },
        scales: {
          x: { grid: gridLine, border: noBorder, ticks: mutedTick },
          y: { grid: { display: false }, border: noBorder, ticks: boldTick },
        },
      },
    };

  } else if (spec.type === "histogram") {
    config = {
      type: "bar",
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: ["#5f1730", "#7a1831", "#9b3152", "#b9657d", "#d6a4b6"],
          hoverBackgroundColor: "#840132",
          borderRadius: 6,
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

  } else if (spec.type === "percent-bars") {
    config = {
      type: "bar",
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: points.some((point) => point.color) ? pointColors : "rgba(132, 1, 50, 0.82)",
          hoverBackgroundColor: points.some((point) => point.color) ? pointColors : "#840132",
          borderRadius: 5,
          borderSkipped: false,
        }],
      },
      options: {
        indexAxis: "y",
        responsive: true,
        maintainAspectRatio: false,
        animation: animIn,
        onClick: (_event, elements) => {
          if (spec.filterKey && elements[0]) handleDashboardChartSelection(spec.filterKey, points[elements[0].index]?.label);
        },
        onHover: (event, elements) => { event.native.target.style.cursor = spec.filterKey && elements.length ? "pointer" : "default"; },
        plugins: { legend: { display: false }, tooltip },
        scales: {
          x: { grid: gridLine, border: noBorder, ticks: { ...mutedTick, callback: (value) => `${value}%` }, min: 0, max: 100 },
          y: { grid: { display: false }, border: noBorder, ticks: boldTick },
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
        onClick: (_event, elements) => {
          if (spec.filterKey && elements[0]) handleDashboardChartSelection(spec.filterKey, points[elements[0].index]?.label);
        },
        onHover: (event, elements) => { event.native.target.style.cursor = spec.filterKey && elements.length ? "pointer" : "default"; },
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
        onClick: (_event, elements) => {
          if (spec.filterKey && elements[0]) handleDashboardChartSelection(spec.filterKey, points[elements[0].index]?.label);
        },
        onHover: (event, elements) => { event.native.target.style.cursor = spec.filterKey && elements.length ? "pointer" : "default"; },
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
  if (spec.type === "percent-bars") {
    return `<span class="chart-total"><strong>${escapeHtml(Number(topPoint.value).toFixed(1))}%</strong><small>highest rate</small></span>`;
  }
  return `<span class="chart-total"><strong>${escapeHtml(formatChartValue(total))}</strong><small>${escapeHtml(spec.unit)}</small></span>`;
}

function chartSummary(spec, visible, allPoints) {
  if (!visible.length) {
    return "No data yet — import a workbook to populate.";
  }
  const topPoint = findTopPoint(visible);
  const total = chartTotal(allPoints, spec);
  if (visible.length === 1) {
    const value = spec.type === "percent-bars" ? `${Number(topPoint.value).toFixed(1)}%` : `${formatChartValue(topPoint.value)} ${spec.unit}`;
    return `${topPoint.label} is the only group in view · ${value}`;
  }
  if (spec.type === "score-bars") {
    const bottom = visible[visible.length - 1];
    const spread = (topPoint.value - bottom.value).toFixed(2);
    return `Highest: ${topPoint.label} · ${formatChartValue(topPoint.value, "score")} avg · spread ${spread} pts`;
  }
  if (spec.type === "percent-bars") {
    const bottom = visible.reduce((lowest, point) => point.value < lowest.value ? point : lowest, visible[0]);
    return `Highest: ${topPoint.label} · ${Number(topPoint.value).toFixed(1)}% · lowest: ${bottom.label} ${Number(bottom.value).toFixed(1)}%`;
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
  if (spec.type === "percent-bars") return 100;
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
    <tr data-student-id="${escapeHtml(row.STUD_ID)}">
      <td><a class="student-profile-link" href="/student-profile/${encodeURIComponent(String(row.STUD_ID || ""))}" title="Open student profile">${hl(row.STUD_ID)}</a></td>
      <td><a class="student-profile-link student-profile-name" href="/student-profile/${encodeURIComponent(String(row.STUD_ID || ""))}" title="Open student profile">${hl(row.STUD_NAME)}</a></td>
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
  bindStudentProfileActions(body);
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

// Student profiles -----------------------------------------------------------
let profileLookupTimer = null;
let profileLookupRows = [];
let contextStudentId = "";

function initStudentProfilePage() {
  const input = document.querySelector("#profile-search-input");
  const directoryButton = document.querySelector("#profile-directory-btn");
  if (!input) return;

  input.addEventListener("input", () => {
    clearTimeout(profileLookupTimer);
    profileLookupTimer = setTimeout(() => runStudentLookup(input.value), 180);
  });
  input.addEventListener("focus", () => runStudentLookup(input.value));
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && profileLookupRows[0]) {
      event.preventDefault();
      openStudentProfile(profileLookupRows[0].student_id);
    }
    if (event.key === "Escape") hideStudentLookup();
  });
  if (directoryButton) {
    directoryButton.addEventListener("click", () => {
      input.focus();
      input.select();
      runStudentLookup(input.value);
      document.querySelector("#profile-finder")?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }
  document.addEventListener("click", (event) => {
    if (!event.target.closest("#profile-finder")) hideStudentLookup();
  });

  const studentId = String(document.body.dataset.studentId || "").trim();
  if (studentId) loadStudentProfile(studentId);
  else loadProfileSuggestions();
}

async function runStudentLookup(query) {
  const results = document.querySelector("#profile-search-results");
  const input = document.querySelector("#profile-search-input");
  if (!results || !input) return;
  results.hidden = false;
  input.setAttribute("aria-expanded", "true");
  results.innerHTML = `<div class="profile-search-message">Searching local student records…</div>`;
  try {
    const response = await fetch(`/api/students/lookup?q=${encodeURIComponent(String(query || ""))}&limit=10`);
    const data = await response.json();
    profileLookupRows = data.students || [];
    if (!profileLookupRows.length) {
      results.innerHTML = `<div class="profile-search-message">No students match <strong>${escapeHtml(query)}</strong>.</div>`;
      return;
    }
    results.innerHTML = profileLookupRows.map((student, index) => `
      <button class="profile-search-result" type="button" role="option" data-lookup-student="${escapeHtml(student.student_id)}" aria-selected="${index === 0}">
        <span class="profile-result-avatar">${escapeHtml(profileInitials(student.name))}</span>
        <span class="profile-result-copy"><strong>${highlightText(student.name, query)}</strong><small>${highlightText(student.student_id, query)} · ${highlightText(student.major, query)} · ${highlightText(student.class_year, query)}</small></span>
        <span class="profile-result-status ${student.is_current ? "current" : "missing"}">${student.is_current ? "Current" : "Missing"}</span>
        <span class="profile-result-arrow">→</span>
      </button>
    `).join("");
    results.querySelectorAll("[data-lookup-student]").forEach((button) => {
      button.addEventListener("click", () => openStudentProfile(button.dataset.lookupStudent));
    });
  } catch (_) {
    results.innerHTML = `<div class="profile-search-message error">Student lookup is temporarily unavailable.</div>`;
  }
}

function hideStudentLookup() {
  const results = document.querySelector("#profile-search-results");
  const input = document.querySelector("#profile-search-input");
  if (results) results.hidden = true;
  if (input) input.setAttribute("aria-expanded", "false");
}

async function loadProfileSuggestions() {
  const target = document.querySelector("#profile-recent-students");
  if (!target) return;
  try {
    const response = await fetch("/api/students/lookup?limit=5");
    const data = await response.json();
    target.innerHTML = (data.students || []).map((student) => `
      <a href="/student-profile/${encodeURIComponent(student.student_id)}">
        <span>${escapeHtml(profileInitials(student.name))}</span>
        <strong>${escapeHtml(student.name)}</strong>
        <small>${escapeHtml(student.student_id)} · ${escapeHtml(student.major)}</small>
      </a>
    `).join("");
  } catch (_) { target.innerHTML = ""; }
}

function openStudentProfile(studentId) {
  if (!studentId) return;
  window.location.href = `/student-profile/${encodeURIComponent(String(studentId))}`;
}

async function loadStudentProfile(studentId) {
  const content = document.querySelector("#student-profile-content");
  const loading = document.querySelector("#profile-loading");
  const empty = document.querySelector("#profile-empty");
  const error = document.querySelector("#profile-error");
  if (!content || !studentId) return;
  if (loading) loading.hidden = false;
  if (empty) empty.hidden = true;
  if (error) error.hidden = true;
  content.hidden = true;
  try {
    const response = await fetch(`/api/students/${encodeURIComponent(String(studentId))}/profile`);
    if (!response.ok) throw new Error(response.status === 404 ? "This student record could not be found." : "The student profile could not be loaded.");
    const data = await response.json();
    renderStudentProfile(data);
    const input = document.querySelector("#profile-search-input");
    if (input) input.value = `${data.identity.name} · ${data.identity.student_id}`;
    document.title = `${data.identity.name} · WSP Student Profile`;
  } catch (err) {
    if (error) {
      error.hidden = false;
      error.innerHTML = `<strong>Profile unavailable</strong><span>${escapeHtml(err.message)}</span><a href="/student-profile">Return to student search</a>`;
    }
  } finally {
    if (loading) loading.hidden = true;
  }
}

function renderStudentProfile(data) {
  const target = document.querySelector("#student-profile-content");
  if (!target) return;
  const identity = data.identity || {};
  const groups = Object.fromEntries((data.groups || []).map((group) => [group.key, group]));
  const badges = (data.badges || []).map((badge) => `<span class="profile-badge ${escapeHtml(badge.tone)}">${escapeHtml(badge.label)}</span>`).join("");
  const contactLinks = [
    identity.email ? `<a href="mailto:${escapeHtml(identity.email)}"><span>Email</span><strong>${escapeHtml(identity.email)}</strong></a>` : "",
    identity.mobile ? `<a href="tel:${escapeHtml(identity.mobile)}"><span>Mobile</span><strong>${escapeHtml(identity.mobile)}</strong></a>` : "",
  ].filter(Boolean).join("");

  target.innerHTML = `
    <article class="profile-hero">
      <div class="profile-hero-accent"></div>
      <div class="profile-identity">
        <div class="profile-avatar" aria-hidden="true">${escapeHtml(identity.initials || profileInitials(identity.name))}</div>
        <div class="profile-identity-copy">
          <div class="profile-badge-row">${badges}</div>
          <h2>${escapeHtml(identity.name)}</h2>
          <p>${escapeHtml(identity.major || "Major not provided")} <span>·</span> ${escapeHtml(identity.class_year || "Class not provided")}</p>
          <div class="profile-id-line"><span>Student ID</span><strong>${escapeHtml(identity.student_id)}</strong></div>
        </div>
        <div class="profile-contact-links">${contactLinks || `<span class="profile-no-contact">No contact details provided</span>`}</div>
      </div>
      <div class="profile-overview"><span>At a glance</span><p>${escapeHtml(data.overview || "Student overview is not available.")}</p></div>
    </article>

    <section class="profile-highlight-grid" aria-label="Student highlights">
      ${(data.highlights || []).map((item, index) => `
        <article class="profile-highlight-card tone-${index + 1}">
          <span>${escapeHtml(item.label)}</span><strong>${escapeHtml(item.value)}</strong><small>${escapeHtml(item.detail)}</small>
        </article>
      `).join("")}
    </section>

    <div class="profile-layout">
      <div class="profile-main-column">
        ${renderProfileGroup(groups.academic, "Academic record", "Core program, enrollment, and progress information.")}
        ${renderSkillsCard(data.skills || [])}
        ${renderProfileGroup(groups.work, "Work-study profile", "Experience and the kind of placement this student is seeking.")}
        ${renderSupportCard(data.support || [])}
        ${renderAdditionalFields(data.additional_fields || [])}
      </div>
      <aside class="profile-side-column">
        ${renderProfileGroup(groups.standing, "Standing & alerts", "Latest standing information and academic attention flags.")}
        ${renderProfileGroup(groups.contact, "Contact & application", "Contact details recorded in the imported workbook.")}
        ${renderRecordCard(data.record || {})}
        ${renderTimelineCard(data.timeline || [])}
      </aside>
    </div>
  `;
  target.hidden = false;
}

function renderProfileGroup(group, title, description) {
  if (!group) return "";
  return `<section class="profile-card profile-detail-card">
    <div class="profile-card-head"><div><p class="eyebrow">${escapeHtml(group.title)}</p><h3>${escapeHtml(title)}</h3></div><p>${escapeHtml(description)}</p></div>
    <dl class="profile-detail-grid">${(group.items || []).map(renderProfileField).join("")}</dl>
  </section>`;
}

function renderProfileField(item) {
  const missing = item.value === null || item.value === undefined || item.value === "";
  let value = missing ? "Not provided" : item.value;
  if (item.kind === "boolean" && !missing) value = item.value ? "Yes" : "No";
  if (item.kind === "number" && !missing) value = Number.isInteger(Number(item.value)) ? Number(item.value).toLocaleString() : Number(item.value).toFixed(2);
  return `<div class="profile-detail-item ${missing ? "is-missing" : ""}"><dt>${escapeHtml(item.label)}</dt><dd>${escapeHtml(value)}</dd></div>`;
}

function renderSkillsCard(skills) {
  return `<section class="profile-card profile-skills-card">
    <div class="profile-card-head"><div><p class="eyebrow">Capabilities</p><h3>Skills & languages</h3></div><p>Student-reported strengths from the WSP workbook.</p></div>
    <div class="profile-skill-groups">${skills.map((skill) => `
      <div class="profile-skill-group"><h4>${escapeHtml(skill.label)}</h4>
        ${(skill.values || []).length ? `<div class="profile-chip-list">${skill.values.map((value) => `<span>${escapeHtml(value)}</span>`).join("")}</div>` : `<p class="profile-missing-value">Not provided</p>`}
      </div>`).join("")}
    </div>
  </section>`;
}

function renderSupportCard(items) {
  return `<section class="profile-card profile-support-card">
    <div class="profile-card-head"><div><p class="eyebrow">Student support</p><h3>Aid, programs & housing</h3></div><p>Participation flags recorded in the current workbook.</p></div>
    <div class="profile-support-grid">${items.map((item) => {
      const state = item.value === true ? "yes" : item.value === false ? "no" : "unknown";
      const label = item.value === true ? "Yes" : item.value === false ? "No" : "Not provided";
      return `<div class="profile-support-item ${state}"><span class="profile-support-check">${item.value === true ? "✓" : item.value === false ? "—" : "?"}</span><div><strong>${escapeHtml(item.label)}</strong><small>${label}</small></div></div>`;
    }).join("")}</div>
  </section>`;
}

function renderAdditionalFields(items) {
  if (!items.length) return "";
  return `<section class="profile-card profile-detail-card">
    <div class="profile-card-head"><div><p class="eyebrow">Source workbook</p><h3>Additional information</h3></div><p>Extra columns preserved from Excel, beyond the standard WSP schema.</p></div>
    <dl class="profile-detail-grid">${items.map(renderProfileField).join("")}</dl>
  </section>`;
}

function renderRecordCard(record) {
  const items = [
    ["Record status", record.is_current ? "Current" : "Missing from latest import"],
    ["Added to database", formatProfileDate(record.added_at)],
    ["Last modified", formatProfileDate(record.modified_at || record.updated_at)],
    ["First source", record.first_seen_source || (record.first_seen_batch_id ? `Import #${record.first_seen_batch_id}` : "Not provided")],
    ["Latest source", record.last_seen_source || (record.last_seen_batch_id ? `Import #${record.last_seen_batch_id}` : "Not provided")],
  ];
  return `<section class="profile-card profile-record-card"><div class="profile-card-head"><div><p class="eyebrow">Data provenance</p><h3>Record details</h3></div></div>
    <dl>${items.map(([label, value]) => `<div><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value || "Not provided")}</dd></div>`).join("")}</dl>
  </section>`;
}

function renderTimelineCard(items) {
  return `<section class="profile-card profile-timeline-card"><div class="profile-card-head"><div><p class="eyebrow">History</p><h3>Record timeline</h3></div><p>Changes captured by workbook imports.</p></div>
    <ol class="profile-timeline">${items.length ? items.map((item) => `<li><span></span><div><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(formatProfileDate(item.date))}${item.source ? ` · ${escapeHtml(item.source)}` : ""}</small></div></li>`).join("") : `<li class="empty"><div><strong>No earlier changes recorded</strong><small>This is the only known version of the student record.</small></div></li>`}</ol>
  </section>`;
}

function formatProfileDate(value) {
  if (!value) return "Not provided";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return String(value);
  return parsed.toLocaleString("en-US", { dateStyle: "medium", timeStyle: "short" });
}

function profileInitials(name) {
  return String(name || "ST").trim().split(/\s+/).slice(0, 2).map((part) => part.charAt(0).toUpperCase()).join("") || "ST";
}

function bindStudentProfileActions(root = document) {
  root.querySelectorAll?.("[data-student-id]").forEach((row) => {
    if (row.dataset.profileActionsBound === "true") return;
    row.dataset.profileActionsBound = "true";
    row.addEventListener("contextmenu", (event) => {
      if (event.target.closest("input, select, textarea")) return;
      event.preventDefault();
      showStudentContextMenu(row.dataset.studentId, event.clientX, event.clientY);
    });
    row.addEventListener("dblclick", (event) => {
      if (event.target.closest("a, button, input, select, textarea")) return;
      openStudentProfile(row.dataset.studentId);
    });
  });
}

function initStudentContextMenu() {
  const menu = document.querySelector("#student-context-menu");
  if (!menu || menu.dataset.bound === "true") return;
  menu.dataset.bound = "true";
  menu.querySelector("[data-profile-action='open']")?.addEventListener("click", () => openStudentProfile(contextStudentId));
  menu.querySelector("[data-profile-action='copy']")?.addEventListener("click", async () => {
    if (!contextStudentId) return;
    try { await navigator.clipboard.writeText(contextStudentId); }
    catch (_) {
      const holder = document.createElement("textarea");
      holder.value = contextStudentId;
      document.body.appendChild(holder);
      holder.select();
      document.execCommand("copy");
      holder.remove();
    }
    hideStudentContextMenu();
  });
  document.addEventListener("click", (event) => { if (!event.target.closest("#student-context-menu")) hideStudentContextMenu(); });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") hideStudentContextMenu(); });
  window.addEventListener("scroll", hideStudentContextMenu, { passive: true });
  window.addEventListener("resize", hideStudentContextMenu);
}

function showStudentContextMenu(studentId, x, y) {
  const menu = document.querySelector("#student-context-menu");
  if (!menu || !studentId) return;
  contextStudentId = String(studentId);
  menu.hidden = false;
  menu.style.left = `${Math.min(x, window.innerWidth - 230)}px`;
  menu.style.top = `${Math.min(y, window.innerHeight - 110)}px`;
  menu.querySelector("button")?.focus();
}

function hideStudentContextMenu() {
  const menu = document.querySelector("#student-context-menu");
  if (menu) menu.hidden = true;
}
