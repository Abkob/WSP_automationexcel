"""
Custom UI widgets - Clean design without emojis, high contrast.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QComboBox, QDoubleSpinBox, QSpinBox,
    QLineEdit, QDialog, QDialogButtonBox, QFormLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QCheckBox, QGroupBox, QRadioButton,
    QButtonGroup, QTextEdit, QDateEdit, QListWidget, QListWidgetItem,
    QSizePolicy, QApplication, QMenu, QSplitter, QToolButton, QStackedWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from styles import AppTheme
from models import FilterRule, NumericFilter, TextFilter, DateFilter
import pandas as pd
from typing import Optional, List
import datetime


class FilterChip(QFrame):
    """A visual chip representing an active filter - no emojis."""
    
    removeClicked = pyqtSignal(object)
    editClicked = pyqtSignal(object)
    openTabRequested = pyqtSignal(object)
    
    def __init__(self, filter_rule: FilterRule, parent=None):
        super().__init__(parent)
        self.filter_rule = filter_rule
        self._setup_ui()
    
    def _setup_ui(self):
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet(f"""
            FilterChip {{
                background-color: {AppTheme.PRIMARY_LIGHT};
                border: 2px solid {AppTheme.PRIMARY};
                border-radius: 8px;
                padding: 8px 12px;
            }}
            FilterChip:hover {{
                background-color: {AppTheme.PRIMARY};
                border-color: {AppTheme.PRIMARY_DARK};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)
        
        # Filter text
        filter_text = str(self.filter_rule)
        self.label = QLabel(filter_text)
        self.label.setStyleSheet("""
            background: transparent; 
            border: none;
            color: #111827;
            font-weight: 600;
        """)
        font = self.label.font()
        font.setPointSize(10)
        self.label.setFont(font)
        
        # Remove button - X instead of emoji
        self.remove_btn = QPushButton("X")
        self.remove_btn.setFixedSize(20, 20)
        self.remove_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.ERROR};
                color: #FFFFFF;
                border: none;
                font-size: 12px;
                font-weight: 700;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: #DC2626;
            }}
        """)
        self.remove_btn.clicked.connect(lambda: self.removeClicked.emit(self.filter_rule))
        
        layout.addWidget(self.label)
        layout.addWidget(self.remove_btn)
        
        self.setCursor(Qt.PointingHandCursor)
    
    def enterEvent(self, event):
        """Change label color on hover."""
        self.label.setStyleSheet("""
            background: transparent;
            border: none;
            color: #FFFFFF;
            font-weight: 600;
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Restore label color."""
        self.label.setStyleSheet("""
            background: transparent;
            border: none;
            color: #111827;
            font-weight: 600;
        """)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.editClicked.emit(self.filter_rule)
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {AppTheme.BACKGROUND};
                color: {AppTheme.TEXT};
                border: 2px solid {AppTheme.BORDER};
            }}
            QMenu::item:selected {{
                background-color: {AppTheme.PRIMARY};
                color: #FFFFFF;
            }}
        """)
        open_action = menu.addAction("Preview Tab")
        open_action.triggered.connect(lambda: self.openTabRequested.emit(self.filter_rule))
        menu.exec_(event.globalPos())


class FilterPanel(QWidget):
    """Left sidebar panel for filter management - clean text only."""
    
    filterAdded = pyqtSignal(object)
    filterRemoved = pyqtSignal(object)
    filterEdited = pyqtSignal(object, object)
    allFiltersCleared = pyqtSignal()
    filterModeChanged = pyqtSignal(str)
    ruleTabRequested = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(16)
        
        # Title - no emoji
        self.title_label = QLabel("Rules")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet(f"color: {AppTheme.TEXT};")
        layout.addWidget(self.title_label)

        self.subtitle_label = QLabel("Add rules to filter and highlight rows in the table below")
        self.subtitle_label.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY}; font-size: 9pt;")
        self.subtitle_label.setWordWrap(True)
        layout.addWidget(self.subtitle_label)

        mode_layout = QHBoxLayout()
        mode_label = QLabel("Combine:")
        mode_label.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY}; font-size: 9pt;")
        mode_layout.addWidget(mode_label)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Match ALL (AND)", "all")
        self.mode_combo.addItem("Match ANY (OR)", "any")
        self.mode_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 4px 8px;
                font-size: 9pt;
                color: {AppTheme.TEXT};
            }}
        """)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()

        layout.addLayout(mode_layout)
        
        # Active filters scroll area
        self.filters_scroll = QScrollArea()
        self.filters_scroll.setWidgetResizable(True)
        self.filters_scroll.setFrameStyle(QFrame.StyledPanel)
        self.filters_scroll.setMinimumHeight(200)
        self.filters_scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {AppTheme.BACKGROUND};
                border: 2px solid {AppTheme.BORDER};
            }}
        """)
        
        self.filters_container = QWidget()
        self.filters_layout = QVBoxLayout(self.filters_container)
        self.filters_layout.setAlignment(Qt.AlignTop)
        self.filters_layout.setSpacing(8)
        
        self.filters_scroll.setWidget(self.filters_container)
        layout.addWidget(self.filters_scroll)
        
        # No filters message
        self.no_filters_label = None
        self.filters_layout.addWidget(self._get_no_filters_label())
        
        # Buttons - text only
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)
        
        self.add_btn = QPushButton("Add Filter")
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.PRIMARY};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: 600;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.PRIMARY_DARK};
            }}
            QPushButton:pressed {{
                background-color: {AppTheme.PRIMARY_HOVER};
            }}
        """)
        self.add_btn.clicked.connect(self._on_add_filter)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.ERROR};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: 600;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: #DC2626;
            }}
            QPushButton:pressed {{
                background-color: #B91C1C;
            }}
            QPushButton:disabled {{
                background-color: {AppTheme.GRAY_300};
                color: {AppTheme.GRAY_500};
            }}
        """)
        self.clear_btn.clicked.connect(self._on_clear_all)
        self.clear_btn.setEnabled(False)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.clear_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
    
    def add_filter_chip(self, filter_rule: FilterRule):
        """Add a filter chip to the display."""
        label = self._get_no_filters_label()
        if label.parent():
            label.setParent(None)
        
        chip = FilterChip(filter_rule)
        chip.removeClicked.connect(self._on_remove_filter)
        chip.editClicked.connect(self._on_edit_filter)
        chip.openTabRequested.connect(self._on_open_rule_tab)
        self.filters_layout.addWidget(chip)
        
        self.clear_btn.setEnabled(True)
    
    def remove_filter_chip(self, filter_rule: FilterRule):
        """Remove a filter chip from the display."""
        for i in range(self.filters_layout.count()):
            widget = self.filters_layout.itemAt(i).widget()
            if isinstance(widget, FilterChip) and widget.filter_rule == filter_rule:
                widget.setParent(None)
                widget.deleteLater()
                break
        
        if self.filters_layout.count() == 0:
            self.filters_layout.addWidget(self._get_no_filters_label())
            self.clear_btn.setEnabled(False)
    
    def clear_all_chips(self):
        """Remove all filter chips."""
        label = self._get_no_filters_label()
        while self.filters_layout.count() > 0:
            widget = self.filters_layout.itemAt(0).widget()
            if widget:
                if widget is label:
                    widget.setParent(None)
                else:
                    widget.setParent(None)
                    widget.deleteLater()
        
        self.filters_layout.addWidget(self._get_no_filters_label())
        self.clear_btn.setEnabled(False)
    
    def _on_add_filter(self):
        pass

    def set_context(self, title: str, subtitle: str):
        if title:
            self.title_label.setText(title)
        if subtitle is not None:
            self.subtitle_label.setText(subtitle)

    def set_mode_enabled(self, enabled: bool):
        self.mode_combo.setEnabled(enabled)

    def _on_mode_changed(self):
        mode = self.mode_combo.currentData()
        if mode:
            self.filterModeChanged.emit(mode)
    
    def _on_remove_filter(self, filter_rule):
        self.filterRemoved.emit(filter_rule)
    
    def _on_edit_filter(self, filter_rule):
        self.filterEdited.emit(filter_rule, None)

    def _on_open_rule_tab(self, filter_rule):
        self.ruleTabRequested.emit(filter_rule)
    
    def _on_clear_all(self):
        self.allFiltersCleared.emit()

    def set_filter_mode(self, mode: str):
        idx = self.mode_combo.findData(mode)
        if idx >= 0:
            self.mode_combo.blockSignals(True)
            self.mode_combo.setCurrentIndex(idx)
            self.mode_combo.blockSignals(False)

    def get_filter_mode(self) -> str:
        return self.mode_combo.currentData() or "all"

    def _get_no_filters_label(self) -> QLabel:
        label = getattr(self, "no_filters_label", None)
        if label is not None:
            try:
                label.parent()
            except RuntimeError:
                label = None
        if label is None:
            label = QLabel("No filters yet")
            label.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY}; font-style: italic;")
            label.setAlignment(Qt.AlignCenter)
            self.no_filters_label = label
        return label


class FilterDialog(QDialog):
    """Dialog for creating/editing filters - clean UI."""
    
    def __init__(self, df: pd.DataFrame, existing_filter: Optional[FilterRule] = None, 
                 parent=None):
        super().__init__(parent)
        self.df = df
        self.existing_filter = existing_filter
        self.result_filter = None
        
        self.setWindowTitle("Add Filter" if existing_filter is None else "Edit Filter")
        self.setMinimumWidth(900)
        self.setMinimumHeight(600)
        self.resize(1100, 700)
        self.setSizeGripEnabled(True)
        
        self._setup_ui()
        
        if existing_filter:
            self._load_existing_filter()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {AppTheme.BACKGROUND};
            }}
            QFrame#Panel {{
                background-color: transparent;
            }}
            QFrame#Card {{
                background-color: {AppTheme.SURFACE};
                border: 1px solid {AppTheme.BORDER};
                border-radius: 8px;
            }}
            QLabel#SectionTitle {{
                color: {AppTheme.TEXT};
                font-weight: 700;
                font-size: 10pt;
            }}
            QToolButton#TypeToggle {{
                padding: 6px 10px;
                border: 1px solid {AppTheme.BORDER};
                border-radius: 6px;
                background-color: {AppTheme.BACKGROUND};
                color: {AppTheme.TEXT};
                font-weight: 600;
            }}
            QToolButton#TypeToggle:checked {{
                background-color: {AppTheme.PRIMARY};
                color: #FFFFFF;
                border-color: {AppTheme.PRIMARY};
            }}
            QToolButton#TypeToggle:disabled {{
                color: {AppTheme.TEXT_SECONDARY};
            }}
            QTableWidget {{
                background-color: {AppTheme.BACKGROUND};
                alternate-background-color: {AppTheme.GRAY_50};
                color: {AppTheme.TEXT};
                gridline-color: {AppTheme.GRAY_300};
                border: 1px solid {AppTheme.GRAY_300};
                border-radius: 4px;
                selection-background-color: {AppTheme.PRIMARY_LIGHT};
                selection-color: {AppTheme.TEXT};
            }}
            QHeaderView::section {{
                background-color: {AppTheme.SURFACE};
                color: {AppTheme.TEXT};
                font-weight: 600;
                font-size: 9pt;
                border: none;
                border-bottom: 2px solid {AppTheme.PRIMARY};
                border-right: 1px solid {AppTheme.GRAY_300};
                padding: 8px;
            }}
            QHeaderView::section:last {{
                border-right: none;
            }}
        """)

        header = QFrame()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(8, 4, 8, 4)
        header_layout.setSpacing(4)

        title_text = "Create Filter" if self.existing_filter is None else "Edit Filter"
        title = QLabel(title_text)
        title_font = QFont(QApplication.font())
        title_font.setPointSize(max(12, title_font.pointSize() + 3))
        title_font.setWeight(QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {AppTheme.TEXT};")
        header_layout.addWidget(title)

        subtitle = QLabel("Build a rule and preview matching rows in real time.")
        subtitle.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY}; font-size: 9pt;")
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)

        layout.addWidget(header)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(6)
        layout.addWidget(splitter, 1)

        # Left panel - configuration
        left_panel = QFrame()
        left_panel.setObjectName("Panel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        column_card = QFrame()
        column_card.setObjectName("Card")
        column_layout = QFormLayout(column_card)
        column_layout.setContentsMargins(12, 12, 12, 12)
        column_layout.setSpacing(8)

        self.column_combo = QComboBox()
        self.column_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px;
                font-size: 10pt;
                color: {AppTheme.TEXT};
            }}
        """)
        if not self.df.empty:
            self.column_combo.addItems([str(c) for c in self.df.columns])
        self.column_combo.currentTextChanged.connect(self._on_column_changed)
        column_layout.addRow("Column:", self.column_combo)
        left_layout.addWidget(column_card)

        type_card = QFrame()
        type_card.setObjectName("Card")
        type_layout = QVBoxLayout(type_card)
        type_layout.setContentsMargins(12, 12, 12, 12)
        type_layout.setSpacing(10)

        type_title = QLabel("Filter Type")
        type_title.setObjectName("SectionTitle")
        type_layout.addWidget(type_title)

        type_buttons = QHBoxLayout()
        type_buttons.setSpacing(6)

        self.type_button_group = QButtonGroup()

        self.numeric_radio = QToolButton()
        self.numeric_radio.setText("Numeric")
        self.numeric_radio.setCheckable(True)
        self.numeric_radio.setObjectName("TypeToggle")
        self.type_button_group.addButton(self.numeric_radio, 0)
        self.numeric_radio.toggled.connect(self._on_type_changed)

        self.text_radio = QToolButton()
        self.text_radio.setText("Text")
        self.text_radio.setCheckable(True)
        self.text_radio.setObjectName("TypeToggle")
        self.type_button_group.addButton(self.text_radio, 1)
        self.text_radio.toggled.connect(self._on_type_changed)

        self.date_radio = QToolButton()
        self.date_radio.setText("Date")
        self.date_radio.setCheckable(True)
        self.date_radio.setObjectName("TypeToggle")
        self.type_button_group.addButton(self.date_radio, 2)
        self.date_radio.toggled.connect(self._on_type_changed)

        type_buttons.addWidget(self.numeric_radio)
        type_buttons.addWidget(self.text_radio)
        type_buttons.addWidget(self.date_radio)
        type_buttons.addStretch()
        type_layout.addLayout(type_buttons)

        self.type_stack = QStackedWidget()

        # Numeric filter options
        self.numeric_widget = QWidget()
        numeric_layout = QFormLayout(self.numeric_widget)
        numeric_layout.setContentsMargins(0, 0, 0, 0)
        numeric_layout.setSpacing(6)

        self.operator_combo = QComboBox()
        self.operator_combo.addItems(NumericFilter.OPERATORS)
        self.operator_combo.currentTextChanged.connect(self._update_preview)

        self.value_spin = QDoubleSpinBox()
        self.value_spin.setRange(-1e12, 1e12)
        self.value_spin.setDecimals(4)
        self.value_spin.valueChanged.connect(self._update_preview)

        numeric_layout.addRow("Operator:", self.operator_combo)
        numeric_layout.addRow("Value:", self.value_spin)

        # Text filter options
        self.text_widget = QWidget()
        text_layout = QFormLayout(self.text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(6)

        self.tokens_edit = QLineEdit()
        self.tokens_edit.setPlaceholderText("Comma-separated tokens (e.g., CSE, probation)")
        self.tokens_edit.textChanged.connect(self._update_preview)

        self.case_sensitive_check = QCheckBox("Case sensitive")
        self.case_sensitive_check.setStyleSheet(f"QCheckBox {{ color: {AppTheme.TEXT}; }}")
        self.case_sensitive_check.stateChanged.connect(self._update_preview)

        text_layout.addRow("Tokens:", self.tokens_edit)
        text_layout.addRow("", self.case_sensitive_check)

        # Date filter options
        self.date_widget = QWidget()
        date_layout = QFormLayout(self.date_widget)
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_layout.setSpacing(6)

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        self.start_date_edit.dateChanged.connect(self._update_preview)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.dateChanged.connect(self._update_preview)

        self.use_start_check = QCheckBox("From:")
        self.use_start_check.setChecked(True)
        self.use_start_check.setStyleSheet(f"QCheckBox {{ color: {AppTheme.TEXT}; }}")
        self.use_start_check.stateChanged.connect(self._update_preview)

        self.use_end_check = QCheckBox("To:")
        self.use_end_check.setChecked(True)
        self.use_end_check.setStyleSheet(f"QCheckBox {{ color: {AppTheme.TEXT}; }}")
        self.use_end_check.stateChanged.connect(self._update_preview)

        start_layout = QHBoxLayout()
        start_layout.addWidget(self.use_start_check)
        start_layout.addWidget(self.start_date_edit)

        end_layout = QHBoxLayout()
        end_layout.addWidget(self.use_end_check)
        end_layout.addWidget(self.end_date_edit)

        date_layout.addRow(start_layout)
        date_layout.addRow(end_layout)

        self.type_stack.addWidget(self.numeric_widget)
        self.type_stack.addWidget(self.text_widget)
        self.type_stack.addWidget(self.date_widget)

        type_layout.addWidget(self.type_stack)
        left_layout.addWidget(type_card, 1)

        summary_card = QFrame()
        summary_card.setObjectName("Card")
        summary_layout = QVBoxLayout(summary_card)
        summary_layout.setContentsMargins(12, 12, 12, 12)
        summary_layout.setSpacing(6)

        summary_title = QLabel("Summary")
        summary_title.setObjectName("SectionTitle")
        summary_layout.addWidget(summary_title)

        self.summary_label = QLabel("Set a column and filter values to preview the rule.")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY};")
        summary_layout.addWidget(self.summary_label)

        left_layout.addWidget(summary_card)
        left_layout.addStretch()

        splitter.addWidget(left_panel)

        # Right panel - preview
        preview_panel = QFrame()
        preview_panel.setObjectName("Panel")
        preview_layout = QVBoxLayout(preview_panel)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(8)

        preview_header = QHBoxLayout()
        preview_title = QLabel("Preview")
        preview_title.setObjectName("SectionTitle")
        preview_header.addWidget(preview_title)
        preview_header.addStretch()

        self.preview_count_label = QLabel("0 rows match")
        self.preview_count_label.setStyleSheet(f"color: {AppTheme.PRIMARY}; font-weight: 600; font-size: 10pt;")
        preview_header.addWidget(self.preview_count_label)
        preview_layout.addLayout(preview_header)

        preview_controls = QHBoxLayout()
        rows_label = QLabel("Rows:")
        rows_label.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY}; font-size: 9pt;")
        preview_controls.addWidget(rows_label)

        self.preview_limit_spin = QSpinBox()
        self.preview_limit_spin.setRange(1, 200)
        self.preview_limit_spin.setValue(10)
        self.preview_limit_spin.setFixedWidth(70)
        self.preview_limit_spin.valueChanged.connect(self._update_preview)
        preview_controls.addWidget(self.preview_limit_spin)
        preview_controls.addStretch()
        preview_layout.addLayout(preview_controls)

        self.preview_table = QTableWidget()
        self.preview_table.setMinimumHeight(260)
        self.preview_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.preview_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setSortingEnabled(True)
        self.preview_table.setWordWrap(False)
        self.preview_table.verticalHeader().setVisible(False)
        preview_layout.addWidget(self.preview_table, 1)

        splitter.addWidget(preview_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([360, 640])

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Initial preview
        self.numeric_radio.setChecked(True)
        self._on_type_changed()
        self._update_preview()

    def _on_column_changed(self):
        """Update available options when column changes."""
        column = self.column_combo.currentText()
        if not column or self.df.empty:
            return
        
        col_data = self.df[column]
        
        if pd.api.types.is_numeric_dtype(col_data.dtype):
            self.numeric_radio.setChecked(True)
            try:
                median_val = col_data.median()
                if not pd.isna(median_val):
                    self.value_spin.setValue(median_val)
            except Exception:
                pass
        
        elif pd.api.types.is_datetime64_any_dtype(col_data.dtype):
            self.date_radio.setChecked(True)
        
        else:
            self.text_radio.setChecked(True)
        
        self._update_preview()
    
    def _on_type_changed(self):
        """Show/hide appropriate widgets when filter type changes."""
        if not hasattr(self, "type_stack"):
            return

        if self.numeric_radio.isChecked():
            self.type_stack.setCurrentWidget(self.numeric_widget)
        elif self.text_radio.isChecked():
            self.type_stack.setCurrentWidget(self.text_widget)
        elif self.date_radio.isChecked():
            self.type_stack.setCurrentWidget(self.date_widget)
        
        self._update_preview()
    
    def _update_preview(self):
        """Update the preview table with matching rows."""
        if not hasattr(self, "preview_table") or not hasattr(self, "preview_count_label"):
            return

        if self.df.empty:
            self.preview_table.setRowCount(0)
            self.preview_table.setColumnCount(0)
            self.preview_count_label.setText("No data loaded")
            if hasattr(self, "summary_label"):
                self.summary_label.setText("Load data to preview matching rows.")
            return
        
        try:
            temp_filter = self._create_filter()
            if temp_filter is None:
                if hasattr(self, "summary_label"):
                    self.summary_label.setText("Complete the fields to build a rule.")
                self.preview_table.setRowCount(0)
                self.preview_table.setColumnCount(0)
                self.preview_count_label.setText("0 rows match")
                return
        except Exception:
            return

        if hasattr(self, "summary_label"):
            self.summary_label.setText(str(temp_filter))
        
        column = self.column_combo.currentText()
        if column not in self.df.columns:
            return
        column_idx = self.df.columns.get_loc(column)
        
        matching_rows = []
        for row_pos in range(len(self.df)):
            try:
                value = self.df.iat[row_pos, column_idx]
            except Exception:
                continue
            if temp_filter.matches(value):
                matching_rows.append(row_pos)
        
        count = len(matching_rows)
        self.preview_count_label.setText(f"{count} row{'s' if count != 1 else ''} match")
        
        limit = 10
        if hasattr(self, "preview_limit_spin"):
            try:
                limit = max(1, int(self.preview_limit_spin.value()))
            except Exception:
                limit = 10
        preview_rows = matching_rows[:limit]
        self.preview_table.clear()
        
        if preview_rows:
            self.preview_table.setSortingEnabled(False)
            self.preview_table.setRowCount(len(preview_rows))
            self.preview_table.setColumnCount(len(self.df.columns))
            self.preview_table.setHorizontalHeaderLabels([str(c) for c in self.df.columns])
            
            for table_row, df_idx in enumerate(preview_rows):
                for col_idx, col_name in enumerate(self.df.columns):
                    try:
                        value = self.df.iat[df_idx, col_idx]
                    except Exception:
                        value = ""
                    item = QTableWidgetItem(str(value))
                    
                    if col_name == column:
                        # Subtle blue highlight for matching column
                        item.setBackground(QColor(219, 234, 254))  # Light blue
                    
                    self.preview_table.setItem(table_row, col_idx, item)
            
            self.preview_table.resizeColumnsToContents()
            self.preview_table.horizontalHeader().setStretchLastSection(True)
            self.preview_table.setSortingEnabled(True)
        else:
            self.preview_table.setRowCount(0)
            self.preview_table.setColumnCount(0)
    
    def _create_filter(self) -> Optional[FilterRule]:
        """Create a FilterRule from current dialog settings."""
        column = self.column_combo.currentText()
        if not column:
            return None
        
        if self.numeric_radio.isChecked():
            operator = self.operator_combo.currentText()
            value = self.value_spin.value()
            return NumericFilter(column, operator, value)
        
        elif self.text_radio.isChecked():
            tokens_text = self.tokens_edit.text().strip()
            if not tokens_text:
                return None
            tokens = [t.strip() for t in tokens_text.split(',')]
            case_sensitive = self.case_sensitive_check.isChecked()
            return TextFilter(column, tokens, case_sensitive)
        
        elif self.date_radio.isChecked():
            start_date = None
            end_date = None
            
            if self.use_start_check.isChecked():
                qdate = self.start_date_edit.date()
                start_date = datetime.date(qdate.year(), qdate.month(), qdate.day())
            
            if self.use_end_check.isChecked():
                qdate = self.end_date_edit.date()
                end_date = datetime.date(qdate.year(), qdate.month(), qdate.day())
            
            if start_date is None and end_date is None:
                return None
            
            return DateFilter(column, start_date, end_date)
        
        return None
    
    def _load_existing_filter(self):
        """Load an existing filter into the dialog."""
        col_idx = self.column_combo.findText(self.existing_filter.column)
        if col_idx >= 0:
            self.column_combo.setCurrentIndex(col_idx)
        
        if isinstance(self.existing_filter, NumericFilter):
            self.numeric_radio.setChecked(True)
            op_idx = self.operator_combo.findText(self.existing_filter.operator)
            if op_idx >= 0:
                self.operator_combo.setCurrentIndex(op_idx)
            self.value_spin.setValue(self.existing_filter.value)
        
        elif isinstance(self.existing_filter, TextFilter):
            self.text_radio.setChecked(True)
            self.tokens_edit.setText(', '.join(self.existing_filter.tokens))
            self.case_sensitive_check.setChecked(self.existing_filter.case_sensitive)
        
        elif isinstance(self.existing_filter, DateFilter):
            self.date_radio.setChecked(True)
            
            if self.existing_filter.start_date:
                self.use_start_check.setChecked(True)
                qdate = QDate(
                    self.existing_filter.start_date.year,
                    self.existing_filter.start_date.month,
                    self.existing_filter.start_date.day
                )
                self.start_date_edit.setDate(qdate)
            else:
                self.use_start_check.setChecked(False)
            
            if self.existing_filter.end_date:
                self.use_end_check.setChecked(True)
                qdate = QDate(
                    self.existing_filter.end_date.year,
                    self.existing_filter.end_date.month,
                    self.existing_filter.end_date.day
                )
                self.end_date_edit.setDate(qdate)
            else:
                self.use_end_check.setChecked(False)
    
    def _on_accept(self):
        """Validate and accept the dialog."""
        from PyQt5.QtWidgets import QMessageBox
        
        self.result_filter = self._create_filter()
        
        if self.result_filter is None:
            QMessageBox.warning(
                self,
                "Invalid Filter",
                "Please configure the filter settings correctly."
            )
            return
        
        self.accept()
    
    def get_filter(self) -> Optional[FilterRule]:
        """Get the created/edited filter."""
        return self.result_filter
