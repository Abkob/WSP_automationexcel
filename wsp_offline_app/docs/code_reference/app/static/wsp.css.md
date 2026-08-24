# `app/static/wsp.css`

[Open source](../../../../app/static/wsp.css) · [Code documentation index](../../../CODE_REFERENCE.md) · [Feature and code flows](../../../FEATURES_AND_CODE_FLOW.md)

## Responsibility

Defines the complete AUB-branded responsive visual system for navigation, dashboards, tables, profiles, forms, diagnostics, printing, and loading states.

## File facts

- **Type:** `.css`
- **Size:** 3,618 lines
- **Layer:** `app`

## Dependencies and integration

- `CSS custom property --surface`
- `CSS custom property --surface-soft`
- `CSS custom property --panel`
- `CSS custom property --ink`
- `CSS custom property --muted`
- `CSS custom property --faint`
- `CSS custom property --line`
- `CSS custom property --line-soft`
- `CSS custom property --aub`
- `CSS custom property --aub-2`
- `CSS custom property --aub-soft`
- `CSS custom property --chart-track`
- `CSS custom property --chart-neutral`
- `CSS custom property --chart-neutral-strong`
- `CSS custom property --chart-gold`
- `CSS custom property --chart-selected`
- `CSS custom property --accent-teal`
- `CSS custom property --accent-teal-soft`
- `CSS custom property --accent-navy`
- `CSS custom property --accent-navy-soft`
- `CSS custom property --accent-green`
- `CSS custom property --accent-green-soft`
- `CSS custom property --accent-blue`
- `CSS custom property --accent-blue-soft`
- `CSS custom property --accent-orange`
- `CSS custom property --accent-orange-soft`
- `CSS custom property --blue-soft`
- `CSS custom property --slate-strong`
- `CSS custom property --good`
- `CSS custom property --good-soft`
- `CSS custom property --warn`
- `CSS custom property --warn-soft`
- `CSS custom property --danger`
- `CSS custom property --shadow`
- `CSS custom property --shadow-lg`
- `CSS custom property --dash-navy`
- `CSS custom property --dash-cream`
- `CSS custom property --dash-maroon-deep`
- `CSS custom property --kpi-color`
- `CSS custom property --kpi-soft`
- `CSS custom property --kpi-color`
- `CSS custom property --kpi-soft`
- `CSS custom property --kpi-color`
- `CSS custom property --kpi-soft`
- `CSS custom property --kpi-color`
- `CSS custom property --kpi-soft`
- `CSS custom property --kpi-color`
- `CSS custom property --kpi-soft`
- `CSS custom property --kpi-color`
- `CSS custom property --kpi-soft`

## Public symbols and executable sections

| Line | Kind | Symbol | Role |
|---:|---|---|---|
| 1 | CSS selector | `:root` | Visual rule. |
| 38 | CSS selector | `*` | Visual rule. |
| 42 | CSS selector | `html` | Visual rule. |
| 46 | CSS selector | `body` | Visual rule. |
| 55 | CSS selector | `button, input, select, textarea` | Visual rule. |
| 62 | CSS selector | `button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible, a:focus-vis` | Visual rule. |
| 71 | CSS selector | `.admin-shell` | Visual rule. |
| 76 | CSS selector | `.sidebar` | Visual rule. |
| 90 | CSS selector | `.sidebar-exit` | Visual rule. |
| 95 | CSS selector | `.exit-app-btn` | Visual rule. |
| 110 | CSS selector | `.exit-app-btn:hover` | Visual rule. |
| 116 | CSS selector | `.brand` | Visual rule. |
| 125 | CSS selector | `.brand-logo` | Visual rule. |
| 132 | CSS selector | `.brand-subtitle` | Visual rule. |
| 146 | CSS selector | `nav` | Visual rule. |
| 152 | CSS selector | `.nav-label` | Visual rule. |
| 162 | CSS selector | `nav a, nav button` | Visual rule. |
| 182 | CSS selector | `nav button:disabled` | Visual rule. |
| 187 | CSS selector | `nav a.active` | Visual rule. |
| 193 | CSS selector | `nav a:hover, nav button:hover` | Visual rule. |
| 199 | CSS selector | `.nav-glyph` | Visual rule. |
| 212 | CSS selector | `nav a.active .nav-glyph` | Visual rule. |
| 217 | CSS selector | `.sidebar-status` | Visual rule. |
| 226 | CSS selector | `.sidebar-status div` | Visual rule. |
| 234 | CSS selector | `.sidebar-status strong` | Visual rule. |
| 238 | CSS selector | `.sidebar-status span:last-child` | Visual rule. |
| 244 | CSS selector | `.status-dot, .pulse-dot` | Visual rule. |
| 253 | CSS selector | `.status-dot.good, .pulse-dot` | Visual rule. |
| 258 | CSS selector | `.status-dot.amber` | Visual rule. |
| 262 | CSS selector | `.status-dot.maroon` | Visual rule. |
| 266 | CSS selector | `.status-dot.blue` | Visual rule. |
| 245 | CSS selector | `.pulse-dot` | Visual rule. |
| 274 | CSS selector | `@keyframes pulse` | Visual rule. |
| 276 | CSS selector | `0%,   100%` | Visual rule. |
| 281 | CSS selector | `50%` | Visual rule. |
| 286 | CSS selector | `.workspace` | Visual rule. |
| 293 | CSS selector | `.topbar` | Visual rule. |
| 308 | CSS selector | `.runtime-state` | Visual rule. |
| 320 | CSS selector | `.admin-account` | Visual rule. |
| 326 | CSS selector | `.topbar-logo` | Visual rule. |
| 333 | CSS selector | `.app-main` | Visual rule. |
| 342 | CSS selector | `.app-footer` | Visual rule. |
| 354 | CSS selector | `.view` | Visual rule. |
| 358 | CSS selector | `body[data-active-path="/"] #dashboard-view, body[data-active-path="/filters"] #filters-view, body[da` | Visual rule. |
| 367 | CSS selector | `.page-heading` | Visual rule. |
| 377 | CSS selector | `.page-heading h1` | Visual rule. |
| 386 | CSS selector | `.page-heading p` | Visual rule. |
| 392 | CSS selector | `.eyebrow` | Visual rule. |
| 401 | CSS selector | `h1, h2, h3` | Visual rule. |
| 407 | CSS selector | `.mode-pill, .icon-button` | Visual rule. |
| 422 | CSS selector | `.metric-grid` | Visual rule. |
| 429 | CSS selector | `.metric-card, .chart-card, .import-panel, .search-panel, .results-panel` | Visual rule. |
| 440 | CSS selector | `.metric-card` | Visual rule. |
| 444 | CSS selector | `.metric-card span` | Visual rule. |
| 453 | CSS selector | `.metric-card strong` | Visual rule. |
| 462 | CSS selector | `.metric-card small` | Visual rule. |
| 473 | CSS selector | `.section-title` | Visual rule. |
| 484 | CSS selector | `.chart-grid` | Visual rule. |
| 491 | CSS selector | `.chart-card` | Visual rule. |
| 497 | CSS selector | `.chart-card:hover` | Visual rule. |
| 502 | CSS selector | `.chart-canvas-wrap` | Visual rule. |
| 508 | CSS selector | `.chart-head` | Visual rule. |
| 519 | CSS selector | `.chart-card h3` | Visual rule. |
| 528 | CSS selector | `.chart-head p` | Visual rule. |
| 537 | CSS selector | `.chart-total` | Visual rule. |
| 551 | CSS selector | `.chart-total strong` | Visual rule. |
| 559 | CSS selector | `.chart-total small` | Visual rule. |
| 567 | CSS selector | `.import-strip` | Visual rule. |
| 578 | CSS selector | `.import-strip.empty` | Visual rule. |
| 584 | CSS selector | `.import-strip-row` | Visual rule. |
| 592 | CSS selector | `.import-strip-meta` | Visual rule. |
| 599 | CSS selector | `.import-strip-label` | Visual rule. |
| 608 | CSS selector | `.import-strip-meta strong` | Visual rule. |
| 618 | CSS selector | `.import-strip-time` | Visual rule. |
| 625 | CSS selector | `.import-strip-counts` | Visual rule. |
| 634 | CSS selector | `.import-strip-counts > div` | Visual rule. |
| 641 | CSS selector | `.import-strip-counts strong` | Visual rule. |
| 649 | CSS selector | `.import-strip-counts span` | Visual rule. |
| 657 | CSS selector | `.import-strip-alert strong` | Visual rule. |
| 659 | CSS selector | `.import-strip-notice` | Visual rule. |
| 667 | CSS selector | `.import-strip-notice.info` | Visual rule. |
| 672 | CSS selector | `.import-strip-notice.warn` | Visual rule. |
| 677 | CSS selector | `.import-panel` | Visual rule. |
| 682 | CSS selector | `.import-header` | Visual rule. |
| 692 | CSS selector | `.import-header strong` | Visual rule. |
| 699 | CSS selector | `.import-header small` | Visual rule. |
| 707 | CSS selector | `.import-stats-grid` | Visual rule. |
| 713 | CSS selector | `.import-stat` | Visual rule. |
| 722 | CSS selector | `.import-stat span` | Visual rule. |
| 730 | CSS selector | `.import-stat strong` | Visual rule. |
| 740 | CSS selector | `.import-stat.new strong` | Visual rule. |
| 742 | CSS selector | `.import-stat.updated strong` | Visual rule. |
| 743 | CSS selector | `.import-stat.missing strong` | Visual rule. |
| 744 | CSS selector | `.import-status-badge` | Visual rule. |
| 757 | CSS selector | `.import-status-badge.completed` | Visual rule. |
| 759 | CSS selector | `.import-status-badge.failed` | Visual rule. |
| 760 | CSS selector | `.import-status-badge.pending` | Visual rule. |
| 761 | CSS selector | `.import-notice` | Visual rule. |
| 770 | CSS selector | `.import-notice.error` | Visual rule. |
| 772 | CSS selector | `.import-notice.info` | Visual rule. |
| 773 | CSS selector | `.operation-card, .sheet-workspace` | Visual rule. |
| 781 | CSS selector | `mark.search-hl` | Visual rule. |
| 789 | CSS selector | `.global-search-bar` | Visual rule. |
| 793 | CSS selector | `.global-search-bar input` | Visual rule. |
| 806 | CSS selector | `.global-search-bar input:focus` | Visual rule. |
| 812 | CSS selector | `.global-search-bar input::placeholder` | Visual rule. |
| 817 | CSS selector | `.sheets-global-results` | Visual rule. |
| 823 | CSS selector | `.global-results-banner` | Visual rule. |
| 833 | CSS selector | `.sheet-tab-badge` | Visual rule. |
| 848 | CSS selector | `/* ── multi-select picker ─────────────────────────────────────────────────── */ .ms-field` | Visual rule. |
| 854 | CSS selector | `.ms-field-label` | Visual rule. |
| 862 | CSS selector | `.ms-root` | Visual rule. |
| 866 | CSS selector | `.ms-trigger` | Visual rule. |
| 884 | CSS selector | `.ms-trigger:focus-visible` | Visual rule. |
| 889 | CSS selector | `.ms-trigger[data-open="true"]` | Visual rule. |
| 892 | CSS selector | `.ms-trigger-label` | Visual rule. |
| 898 | CSS selector | `.ms-trigger-arrow` | Visual rule. |
| 904 | CSS selector | `.ms-trigger[data-open="true"] .ms-trigger-arrow` | Visual rule. |
| 907 | CSS selector | `.ms-dropdown` | Visual rule. |
| 922 | CSS selector | `.ms-dropdown.open` | Visual rule. |

## Runtime flow

1. The application or development workflow loads `app/static/wsp.css` when its app responsibility is needed.
2. Inputs are validated or normalized by the symbols/configuration listed above.
3. The file returns data, renders UI, persists state, runs an operational step, or asserts behavior according to its responsibility.
4. Failures propagate to the calling layer or are converted into logged/user-facing status where the source explicitly handles them.

## Maintenance notes

- Keep behavior synchronized with the linked feature flow and automated tests.
- Preserve local-first privacy: student records, exports, backups, and embeddings remain on the installed computer.
- Re-run `python scripts/generate_code_documentation.py` after changing public symbols, routes, or dependencies.
