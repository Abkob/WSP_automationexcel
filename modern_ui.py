"""
Modern UI components for the main window.
"""

import logging
import os
from typing import List, Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QToolButton,
    QVBoxLayout,
)

from styles import AppTheme

logger = logging.getLogger("StudentManager.ModernUI")


def _load_scaled_logo(filename: str, max_width: int, max_height: int) -> Optional[QPixmap]:
    """Load and scale a logo asset if available."""
    path = AppTheme.asset_path(filename)
    if not os.path.exists(path):
        return None

    pixmap = QPixmap(path)
    if pixmap.isNull():
        return None

    return pixmap.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)


class ModernActionBar(QFrame):
    """Top action bar with grouped actions."""

    loadRequested = pyqtSignal()
    saveRequested = pyqtSignal()
    exportRequested = pyqtSignal(str)  # mode: all/current/filtered
    archivesRequested = pyqtSignal()
    newTabRequested = pyqtSignal()
    shortcutsRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("ModernActionBar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)

        load_btn = self._create_action_button("Load Data", "Load data file (Ctrl+O)", primary=True)
        load_btn.clicked.connect(self.loadRequested.emit)
        layout.addWidget(load_btn)

        save_btn = self._create_action_button("Save View", "Save current view (Ctrl+S)")
        save_btn.clicked.connect(self.saveRequested.emit)
        layout.addWidget(save_btn)

        export_btn = self._create_action_button("Export", "Export data to Excel")
        export_menu = QMenu(self)
        export_menu.addAction("All Data", lambda: self.exportRequested.emit("all"))
        export_menu.addAction("Current Tab", lambda: self.exportRequested.emit("current"))
        export_menu.addAction("Filtered Rows", lambda: self.exportRequested.emit("filtered"))
        export_btn.setMenu(export_menu)
        export_btn.setPopupMode(QToolButton.InstantPopup)
        layout.addWidget(export_btn)

        layout.addWidget(self._create_separator())

        new_tab_btn = self._create_action_button("New Tab", "Create a new custom view")
        new_tab_btn.clicked.connect(self.newTabRequested.emit)
        layout.addWidget(new_tab_btn)

        archives_btn = self._create_action_button("Archives", "Browse archived data")
        archives_btn.clicked.connect(self.archivesRequested.emit)
        layout.addWidget(archives_btn)

        layout.addStretch()

        help_btn = self._create_action_button("Help", "Keyboard shortcuts")
        help_btn.setFixedWidth(74)
        help_btn.clicked.connect(self.shortcutsRequested.emit)
        layout.addWidget(help_btn)

        self.setStyleSheet(
            f"""
            #ModernActionBar {{
                background-color: {AppTheme.BACKGROUND};
                border: 1px solid {AppTheme.GRAY_200};
                border-radius: 8px;
            }}
            QToolButton {{
                background-color: {AppTheme.BACKGROUND};
                color: {AppTheme.TEXT};
                border: 1px solid {AppTheme.BORDER};
                border-radius: 7px;
                padding: 7px 12px;
                font-weight: 500;
                font-size: 9pt;
            }}
            QToolButton[primary="true"] {{
                background-color: {AppTheme.PRIMARY};
                color: #FFFFFF;
                border-color: {AppTheme.PRIMARY};
            }}
            QToolButton:hover {{
                background-color: {AppTheme.PRIMARY_LIGHT};
                border-color: {AppTheme.PRIMARY};
                color: {AppTheme.PRIMARY_DARK};
            }}
            QToolButton[primary="true"]:hover {{
                background-color: {AppTheme.PRIMARY_DARK};
                border-color: {AppTheme.PRIMARY_DARK};
                color: #FFFFFF;
            }}
            QToolButton:pressed {{
                background-color: {AppTheme.GRAY_100};
            }}
            """
        )

    def _create_action_button(self, text: str, tooltip: str = "", primary: bool = False) -> QToolButton:
        btn = QToolButton()
        btn.setText(text)
        btn.setToolTip(tooltip)
        btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
        btn.setProperty("primary", "true" if primary else "false")
        return btn

    def _create_separator(self) -> QFrame:
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setStyleSheet(f"background-color: {AppTheme.BORDER};")
        separator.setFixedWidth(1)
        return separator


class QuickFilterBar(QFrame):
    """Optional quick filter actions."""

    quickFilterRequested = pyqtSignal(str, str, object)  # column, operator, value
    clearRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("QuickFilterBar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        title = QLabel("Quick Filters")
        title.setStyleSheet(f"color: {AppTheme.TEXT}; font-weight: 700; font-size: 10pt;")
        layout.addWidget(title)

        self.gpa_high_btn = self._create_filter_chip("GPA >= 3.5", AppTheme.SUCCESS)
        self.gpa_high_btn.clicked.connect(lambda: self.quickFilterRequested.emit("GPA", ">=", 3.5))
        layout.addWidget(self.gpa_high_btn)

        self.gpa_medium_btn = self._create_filter_chip("GPA 2.5 - 3.5", AppTheme.INFO)
        self.gpa_medium_btn.clicked.connect(lambda: self.quickFilterRequested.emit("GPA", "range", (2.5, 3.5)))
        layout.addWidget(self.gpa_medium_btn)

        self.gpa_low_btn = self._create_filter_chip("GPA < 2.5", AppTheme.WARNING)
        self.gpa_low_btn.clicked.connect(lambda: self.quickFilterRequested.emit("GPA", "<", 2.5))
        layout.addWidget(self.gpa_low_btn)

        layout.addWidget(self._create_separator())

        self.active_btn = self._create_filter_chip("Active", AppTheme.PRIMARY)
        self.active_btn.clicked.connect(lambda: self.quickFilterRequested.emit("Status", "contains", "Active"))
        layout.addWidget(self.active_btn)

        self.probation_btn = self._create_filter_chip("Probation", AppTheme.WARNING)
        self.probation_btn.clicked.connect(lambda: self.quickFilterRequested.emit("Status", "contains", "Probation"))
        layout.addWidget(self.probation_btn)

        layout.addStretch()

        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent;
                color: {AppTheme.ERROR};
                border: 1px solid {AppTheme.ERROR};
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.ERROR};
                color: #FFFFFF;
            }}
            """
        )
        clear_btn.clicked.connect(self.clearRequested.emit)
        layout.addWidget(clear_btn)

        self.setStyleSheet(
            f"""
            #QuickFilterBar {{
                background-color: {AppTheme.SURFACE};
                border: 1px solid {AppTheme.BORDER};
                border-radius: 8px;
            }}
            """
        )

    def _create_filter_chip(self, text: str, color: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {color}22;
                color: {color};
                border: 1px solid {color};
                border-radius: 6px;
                padding: 6px 10px;
                font-weight: 700;
                font-size: 9pt;
            }}
            QPushButton:hover {{
                background-color: {color};
                color: #FFFFFF;
            }}
            """
        )
        return btn

    def _create_separator(self) -> QFrame:
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setStyleSheet(f"background-color: {AppTheme.BORDER};")
        separator.setFixedWidth(1)
        return separator


class CompactHeader(QFrame):
    """Branded header with logo mark and key dataset stats."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("CompactHeader")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(14)

        branding_wrapper = QHBoxLayout()
        branding_wrapper.setContentsMargins(0, 0, 0, 0)
        branding_wrapper.setSpacing(10)

        mark_label = QLabel()
        mark_logo = _load_scaled_logo("logo.png", 32, 32)
        if mark_logo is not None:
            mark_label.setPixmap(mark_logo)
            mark_label.setFixedSize(mark_logo.size())
        else:
            mark_label.setText("SM")
            mark_label.setStyleSheet(f"font-size: 11pt; color: {AppTheme.PRIMARY}; font-weight: 800;")
        branding_wrapper.addWidget(mark_label, 0, Qt.AlignVCenter)

        lockup_layout = QVBoxLayout()
        lockup_layout.setContentsMargins(0, 0, 0, 0)
        lockup_layout.setSpacing(2)

        self.title_label = QLabel("Student Admissions Manager")
        self.title_label.setStyleSheet(
            f"color: {AppTheme.PRIMARY_DARK}; font-size: 12.5pt; font-weight: 600; font-family: {AppTheme.FONT_UI_BOLD};"
        )
        lockup_layout.addWidget(self.title_label)

        subtitle = QLabel("Analytics Workspace")
        subtitle.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY}; font-size: 8.5pt; font-weight: 400;")
        lockup_layout.addWidget(subtitle)

        branding_wrapper.addLayout(lockup_layout)
        layout.addLayout(branding_wrapper)
        layout.addStretch()

        self.row_count_label, self._row_count_value, self._row_count_text = self._create_stat_pill("0", "students")
        layout.addWidget(self.row_count_label)

        self.filter_count_label, self._filter_count_value, self._filter_count_text = self._create_stat_pill("0", "filters")
        layout.addWidget(self.filter_count_label)

        self.file_label = QLabel("File: none")
        self.file_label.setObjectName("HeaderFileLabel")
        layout.addWidget(self.file_label)

        self.setStyleSheet(
            f"""
            #CompactHeader {{
                background-color: {AppTheme.BACKGROUND};
                border-bottom: 1px solid {AppTheme.GRAY_200};
            }}
            QLabel#HeaderFileLabel {{
                color: {AppTheme.TEXT_SECONDARY};
                border: 1px solid {AppTheme.BORDER};
                border-radius: 7px;
                background-color: {AppTheme.BACKGROUND};
                padding: 7px 10px;
                font-size: 8.5pt;
                font-weight: 400;
                min-width: 140px;
            }}
            """
        )

    def _create_stat_pill(self, value: str, label: str):
        container = QFrame()
        container.setObjectName("StatPill")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(1)
        layout.setAlignment(Qt.AlignCenter)

        value_label = QLabel(value)
        value_label.setObjectName("StatValue")
        value_label.setAlignment(Qt.AlignCenter)

        text_label = QLabel(label)
        text_label.setObjectName("StatText")
        text_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(value_label)
        layout.addWidget(text_label)

        self._set_stat_pill_active(container, active=False)
        return container, value_label, text_label

    def _set_stat_pill_active(self, pill: QFrame, active: bool):
        border = AppTheme.PRIMARY if active else AppTheme.GRAY_300
        bg = AppTheme.BACKGROUND
        value_color = AppTheme.PRIMARY_DARK if active else AppTheme.TEXT
        pill.setStyleSheet(
            f"""
            QFrame#StatPill {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 7px;
                min-width: 76px;
            }}
            QLabel#StatValue {{
                color: {value_color};
                font-size: 10.5pt;
                font-weight: 600;
                border: none;
                background: transparent;
            }}
            QLabel#StatText {{
                color: {AppTheme.TEXT_SECONDARY};
                font-size: 7.5pt;
                font-weight: 400;
                border: none;
                background: transparent;
                letter-spacing: 0.2px;
            }}
            """
        )

    def update_row_count(self, visible_count: int, total_count: Optional[int] = None):
        visible_count = max(0, int(visible_count))
        total = visible_count if total_count is None else max(0, int(total_count))

        self._row_count_value.setText(f"{visible_count:,}")
        self._row_count_text.setText("student" if total == 1 else "students")

        filtered = total > 0 and visible_count < total
        self._set_stat_pill_active(self.row_count_label, active=filtered)
        if filtered:
            self.row_count_label.setToolTip(f"Showing {visible_count:,} of {total:,}")
        else:
            self.row_count_label.setToolTip(f"{total:,} students")

    def update_filter_count(self, count: int):
        count = max(0, int(count))
        self._filter_count_value.setText(f"{count}")
        self._filter_count_text.setText("filter" if count == 1 else "filters")
        self._set_stat_pill_active(self.filter_count_label, active=(count > 0))
        self.filter_count_label.setToolTip(f"{count} active {'filter' if count == 1 else 'filters'}")

    def update_file_name(self, filename: str):
        clean_name = filename or "none"
        self.file_label.setText(f"File: {clean_name}")
        self.file_label.setToolTip(clean_name)


class ModernSearchBar(QFrame):
    """Search bar with text input and optional column scope."""

    searchChanged = pyqtSignal(str, str)  # text, column

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("ModernSearchBar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        label = QLabel("Search")
        label.setStyleSheet(f"font-weight: 500; color: {AppTheme.TEXT};")
        layout.addWidget(label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Find by name, ID, status, major...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMinimumHeight(34)
        self.search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_input, 1)

        scope_label = QLabel("Scope")
        scope_label.setStyleSheet(f"font-weight: 400; color: {AppTheme.TEXT_SECONDARY};")
        layout.addWidget(scope_label)

        self.column_combo = QComboBox()
        self.column_combo.addItem("All columns", "Global")
        self.column_combo.setMinimumWidth(170)
        self.column_combo.currentIndexChanged.connect(self._on_search_changed)
        layout.addWidget(self.column_combo)

        self.setStyleSheet(
            f"""
            #ModernSearchBar {{
                background-color: {AppTheme.BACKGROUND};
                border: 1px solid {AppTheme.GRAY_200};
                border-radius: 8px;
            }}
            QLineEdit {{
                border: 1px solid {AppTheme.BORDER};
                border-radius: 7px;
                background-color: {AppTheme.BACKGROUND};
                color: {AppTheme.TEXT};
                padding: 6px 10px;
                font-size: 10pt;
            }}
            QLineEdit:focus {{
                border: 1px solid {AppTheme.PRIMARY};
            }}
            QComboBox {{
                border: 1px solid {AppTheme.BORDER};
                border-radius: 7px;
                padding: 6px 10px;
                background-color: {AppTheme.BACKGROUND};
                color: {AppTheme.TEXT};
                font-weight: 500;
            }}
            """
        )

    def _on_search_changed(self):
        text = self.search_input.text()
        column = self.column_combo.currentData() or "Global"
        self.searchChanged.emit(text, column)

    def update_columns(self, columns: List[str]):
        current = self.column_combo.currentData()
        self.column_combo.clear()
        self.column_combo.addItem("All columns", "Global")
        for col in columns:
            self.column_combo.addItem(col, col)

        for i in range(self.column_combo.count()):
            if self.column_combo.itemData(i) == current:
                self.column_combo.setCurrentIndex(i)
                break
