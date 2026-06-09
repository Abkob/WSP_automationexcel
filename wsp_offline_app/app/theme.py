from __future__ import annotations


APP_PRIMARY_COLOR = "#1f6f8b"
APP_ACCENT_COLOR = "#2f7d57"
APP_WARNING_COLOR = "#b7791f"
APP_DANGER_COLOR = "#b42318"
APP_SURFACE_COLOR = "#f7f9fb"
APP_TEXT_COLOR = "#1f2933"

PAGE_PADDING_CLASS = "px-4 py-4 md:px-6 md:py-5"
SHELL_MAX_WIDTH_CLASS = "w-full max-w-[1600px] mx-auto"
STATUS_CHIP_CLASS = "px-2 py-1 text-xs rounded bg-white/15"
SIDEBAR_LINK_CLASS = "w-full justify-start text-left"


def apply_theme(ui_module) -> None:
    ui_module.colors(
        primary=APP_PRIMARY_COLOR,
        secondary=APP_ACCENT_COLOR,
        accent=APP_WARNING_COLOR,
        positive=APP_ACCENT_COLOR,
        negative=APP_DANGER_COLOR,
    )
    ui_module.add_head_html(
        """
        <style>
          body {
            background: #f7f9fb;
            color: #1f2933;
          }
          .q-page-container {
            background: #f7f9fb;
          }
          :focus-visible {
            outline: 3px solid #b7791f;
            outline-offset: 2px;
          }
          .wsp-results-table .q-table th {
            font-weight: 700;
            color: #1f2933;
            background: #eef4f7;
          }
          .wsp-results-table .q-table td {
            max-width: 280px;
            white-space: normal;
            vertical-align: top;
          }
        </style>
        """
    )
