"""
Modern UI Components - Streamlined, clean, professional
Focus on 2-3 click workflows with visual clarity
"""

import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QToolButton, QFrame, QComboBox, QLineEdit, QMenu, QAction,
    QButtonGroup, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon
from styles import AppTheme
from typing import Optional, List

# Setup logger for this module
logger = logging.getLogger('StudentManager.ModernUI')


class ModernActionBar(QFrame):
    """Streamlined action bar with icon buttons and smart grouping."""

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
        """Create clean, organized action bar."""
        self.setObjectName("ModernActionBar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(12)

        # === FILE OPERATIONS ===
        load_btn = self._create_action_button("📁 Load", "Load data file (Ctrl+O)")
        load_btn.clicked.connect(self.loadRequested.emit)
        layout.addWidget(load_btn)

        save_btn = self._create_action_button("💾 Save", "Save current view (Ctrl+S)")
        save_btn.clicked.connect(self.saveRequested.emit)
        layout.addWidget(save_btn)

        # Export dropdown
        export_btn = self._create_action_button("📤 Export", "Export data to Excel")
        export_menu = QMenu(self)
        export_menu.addAction("📊 All Data", lambda: self.exportRequested.emit("all"))
        export_menu.addAction("📋 Current Tab", lambda: self.exportRequested.emit("current"))
        export_menu.addAction("🎯 Filtered Only", lambda: self.exportRequested.emit("filtered"))
        export_btn.setMenu(export_menu)
        export_btn.setPopupMode(QToolButton.InstantPopup)
        layout.addWidget(export_btn)

        # Separator
        layout.addWidget(self._create_separator())

        # === VIEW OPERATIONS ===
        new_tab_btn = self._create_action_button("➕ New Tab", "Create a new custom view")
        new_tab_btn.clicked.connect(self.newTabRequested.emit)
        layout.addWidget(new_tab_btn)

        archives_btn = self._create_action_button("📚 Archives", "Browse archived data")
        archives_btn.clicked.connect(self.archivesRequested.emit)
        layout.addWidget(archives_btn)

        layout.addStretch()

        # === HELP ===
        help_btn = self._create_action_button("❓", "Keyboard shortcuts")
        help_btn.setFixedWidth(40)
        help_btn.clicked.connect(self.shortcutsRequested.emit)
        layout.addWidget(help_btn)

        # Styling
        self.setStyleSheet(f"""
            #ModernActionBar {{
                background-color: {AppTheme.SURFACE};
                border: 1px solid {AppTheme.GRAY_300};
                border-radius: 6px;
            }}
            QToolButton {{
                background-color: {AppTheme.BACKGROUND};
                color: {AppTheme.TEXT};
                border: 1px solid {AppTheme.GRAY_300};
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 500;
                font-size: 9pt;
            }}
            QToolButton:hover {{
                background-color: {AppTheme.PRIMARY};
                border-color: {AppTheme.PRIMARY};
                color: #FFFFFF;
            }}
            QToolButton:pressed {{
                background-color: {AppTheme.PRIMARY_DARK};
                color: #FFFFFF;
            }}
        """)

    def _create_action_button(self, text: str, tooltip: str = "") -> QToolButton:
        """Create a modern action button."""
        btn = QToolButton()
        btn.setText(text)
        btn.setToolTip(tooltip)
        btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
        return btn

    def _create_separator(self) -> QFrame:
        """Create a vertical separator."""
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(f"background-color: {AppTheme.BORDER};")
        separator.setFixedWidth(2)
        return separator


class QuickFilterBar(QFrame):
    """Quick filter bar with instant filter buttons - 1-click filtering."""

    quickFilterRequested = pyqtSignal(str, str, object)  # column, operator, value
    clearRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Create quick filter interface."""
        self.setObjectName("QuickFilterBar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # Title
        title = QLabel("⚡ Quick Filters:")
        title.setStyleSheet(f"color: {AppTheme.TEXT}; font-weight: 700; font-size: 10pt;")
        layout.addWidget(title)

        # Quick filter chips
        self.gpa_high_btn = self._create_filter_chip("GPA ≥ 3.5", AppTheme.SUCCESS)
        self.gpa_high_btn.clicked.connect(lambda: self.quickFilterRequested.emit("GPA", ">=", 3.5))
        layout.addWidget(self.gpa_high_btn)

        self.gpa_medium_btn = self._create_filter_chip("GPA 2.5-3.5", AppTheme.INFO)
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

        # Clear all button
        clear_btn = QPushButton("✕ Clear All")
        clear_btn.setStyleSheet(f"""
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
        """)
        clear_btn.clicked.connect(self.clearRequested.emit)
        layout.addWidget(clear_btn)

        # Styling
        self.setStyleSheet(f"""
            #QuickFilterBar {{
                background-color: {AppTheme.SURFACE};
                border: 2px solid {AppTheme.BORDER};
                border-radius: 8px;
            }}
        """)

    def _create_filter_chip(self, text: str, color: str) -> QPushButton:
        """Create a quick filter chip button."""
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color}20;
                color: {color};
                border: 2px solid {color};
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 700;
                font-size: 9pt;
            }}
            QPushButton:hover {{
                background-color: {color};
                color: #FFFFFF;
            }}
        """)
        return btn

    def _create_separator(self) -> QFrame:
        """Create a vertical separator."""
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(f"background-color: {AppTheme.BORDER};")
        separator.setFixedWidth(2)
        return separator


class CompactHeader(QFrame):
    """Compact header with key stats - no wasted space."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Create compact header."""
        self.setObjectName("CompactHeader")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(20)

        # App title - smaller, cleaner
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)

        self.title = QLabel("Student Manager")
        self.title.setStyleSheet(f"color: {AppTheme.TEXT}; font-size: 14pt; font-weight: 700;")
        title_layout.addWidget(self.title)

        self.subtitle = QLabel("Filter, analyze, export")
        self.subtitle.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY}; font-size: 8pt;")
        title_layout.addWidget(self.subtitle)

        layout.addLayout(title_layout)

        layout.addStretch()

        # Stats - clean pills
        self.row_count_label = self._create_stat_pill("0", "students")
        layout.addWidget(self.row_count_label)

        self.filter_count_label = self._create_stat_pill("0", "filters")
        layout.addWidget(self.filter_count_label)

        self.file_label = QLabel("No file")
        self.file_label.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY}; font-size: 9pt; font-weight: 600;")
        layout.addWidget(self.file_label)

        # Styling
        self.setStyleSheet(f"""
            #CompactHeader {{
                background-color: {AppTheme.SURFACE};
                border-bottom: 1px solid {AppTheme.GRAY_300};
            }}
        """)

    def _create_stat_pill(self, value: str, label: str) -> QWidget:
        """Create a stat pill widget."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignCenter)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {AppTheme.PRIMARY}; font-size: 16pt; font-weight: 700;")
        value_label.setAlignment(Qt.AlignCenter)

        text_label = QLabel(label)
        text_label.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY}; font-size: 8pt;")
        text_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(value_label)
        layout.addWidget(text_label)

        container.setStyleSheet(f"""
            QWidget {{
                background-color: {AppTheme.BACKGROUND};
                border: 1px solid {AppTheme.GRAY_300};
                border-radius: 6px;
            }}
        """)

        return container

    def update_row_count(self, count: int):
        """Update row count display."""
        pill = self.row_count_label
        value_label = pill.findChild(QLabel)
        if value_label:
            value_label.setText(f"{count:,}")

    def update_filter_count(self, count: int):
        """Update filter count display."""
        pill = self.filter_count_label
        value_label = pill.findChild(QLabel)
        if value_label:
            value_label.setText(f"{count}")

    def update_file_name(self, filename: str):
        """Update file name display."""
        self.file_label.setText(filename or "No file")


class ModernSearchBar(QFrame):
    """Clean, integrated search bar."""

    searchChanged = pyqtSignal(str, str)  # text, column

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Create modern search interface."""
        self.setObjectName("ModernSearchBar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(12)

        # Search icon (emoji)
        icon_label = QLabel("🔍")
        icon_label.setStyleSheet("font-size: 14pt;")
        layout.addWidget(icon_label)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search students by name, ID, status...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_input, 1)

        # Column selector
        in_label = QLabel("in")
        in_label.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY}; font-weight: 600;")
        layout.addWidget(in_label)

        self.column_combo = QComboBox()
        self.column_combo.addItem("🌐 All Columns", "Global")
        self.column_combo.setMinimumWidth(160)
        self.column_combo.currentIndexChanged.connect(self._on_search_changed)
        layout.addWidget(self.column_combo)

        # Styling
        self.setStyleSheet(f"""
            #ModernSearchBar {{
                background-color: {AppTheme.BACKGROUND};
                border: 1px solid {AppTheme.GRAY_300};
                border-radius: 6px;
            }}
            QLineEdit {{
                border: none;
                font-size: 10pt;
                background-color: transparent;
                padding: 4px;
            }}
            QComboBox {{
                border: 1px solid {AppTheme.GRAY_300};
                border-radius: 4px;
                padding: 6px 8px;
                background-color: {AppTheme.BACKGROUND};
            }}
        """)

    def _on_search_changed(self):
        """Emit search changed signal."""
        text = self.search_input.text()
        column = self.column_combo.currentData() or "Global"
        self.searchChanged.emit(text, column)

    def update_columns(self, columns: List[str]):
        """Update available columns."""
        current = self.column_combo.currentData()
        self.column_combo.clear()
        self.column_combo.addItem("🌐 All Columns", "Global")
        for col in columns:
            self.column_combo.addItem(f"📍 {col}", col)

        # Restore selection if possible
        for i in range(self.column_combo.count()):
            if self.column_combo.itemData(i) == current:
                self.column_combo.setCurrentIndex(i)
                break
