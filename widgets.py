"""
Custom UI widgets - Clean design without emojis, high contrast.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QComboBox, QDoubleSpinBox, QSpinBox,
    QLineEdit, QDialog, QDialogButtonBox, QFormLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QCheckBox, QGroupBox, QRadioButton,
    QButtonGroup, QTextEdit, QDateEdit, QListWidget, QListWidgetItem,
    QSizePolicy, QApplication, QMenu
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
        open_action = menu.addAction("Open Rule Tab")
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
        self.setMinimumWidth(600)
        self.setMinimumHeight(650)
        
        self._setup_ui()
        
        if existing_filter:
            self._load_existing_filter()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Form for filter configuration
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        
        # Column selection
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
        form_layout.addRow("Column:", self.column_combo)
        
        # Filter type selection
        type_group = QGroupBox("Filter Type")
        type_group.setStyleSheet(f"QGroupBox {{ font-weight: 600; color: {AppTheme.TEXT}; }}")
        type_layout = QVBoxLayout(type_group)
        
        self.type_button_group = QButtonGroup()
        self.numeric_radio = QRadioButton("Numeric Threshold")
        self.text_radio = QRadioButton("Text Contains")
        self.date_radio = QRadioButton("Date Range")
        
        # Style radio buttons
        radio_style = f"QRadioButton {{ color: {AppTheme.TEXT}; font-size: 10pt; }}"
        self.numeric_radio.setStyleSheet(radio_style)
        self.text_radio.setStyleSheet(radio_style)
        self.date_radio.setStyleSheet(radio_style)
        
        self.type_button_group.addButton(self.numeric_radio, 0)
        self.type_button_group.addButton(self.text_radio, 1)
        self.type_button_group.addButton(self.date_radio, 2)
        
        self.numeric_radio.setChecked(True)
        self.numeric_radio.toggled.connect(self._on_type_changed)
        self.text_radio.toggled.connect(self._on_type_changed)
        self.date_radio.toggled.connect(self._on_type_changed)
        
        type_layout.addWidget(self.numeric_radio)
        type_layout.addWidget(self.text_radio)
        type_layout.addWidget(self.date_radio)
        
        form_layout.addRow(type_group)
        
        # Numeric filter options
        self.numeric_widget = QWidget()
        numeric_layout = QFormLayout(self.numeric_widget)
        numeric_layout.setContentsMargins(0, 0, 0, 0)
        
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
        
        self.tokens_edit = QLineEdit()
        self.tokens_edit.setPlaceholderText("Comma-separated tokens (e.g., CSE, probation, MEPI)")
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
        
        # Add filter type widgets to form
        form_layout.addRow(self.numeric_widget)
        form_layout.addRow(self.text_widget)
        form_layout.addRow(self.date_widget)
        
        # Initially hide text and date widgets
        self.text_widget.hide()
        self.date_widget.hide()
        
        layout.addLayout(form_layout)
        
        # Preview section
        preview_label = QLabel("Preview:")
        preview_label.setStyleSheet(f"font-weight: 600; margin-top: 10px; color: {AppTheme.TEXT}; font-size: 11pt;")
        layout.addWidget(preview_label)
        
        self.preview_count_label = QLabel("0 rows match")
        self.preview_count_label.setStyleSheet(f"color: {AppTheme.PRIMARY}; font-weight: 600; font-size: 10pt;")
        layout.addWidget(self.preview_count_label)
        
        self.preview_table = QTableWidget()
        self.preview_table.setMaximumHeight(200)
        self.preview_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.preview_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setStyleSheet(f"""
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
            QTableWidget::item {{
                padding: 4px 8px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: {AppTheme.PRIMARY_LIGHT};
                color: {AppTheme.TEXT};
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
        layout.addWidget(self.preview_table)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Initial preview
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
        if self.numeric_radio.isChecked():
            self.numeric_widget.show()
            self.text_widget.hide()
            self.date_widget.hide()
        elif self.text_radio.isChecked():
            self.numeric_widget.hide()
            self.text_widget.show()
            self.date_widget.hide()
        elif self.date_radio.isChecked():
            self.numeric_widget.hide()
            self.text_widget.hide()
            self.date_widget.show()
        
        self._update_preview()
    
    def _update_preview(self):
        """Update the preview table with matching rows."""
        if self.df.empty:
            return
        
        try:
            temp_filter = self._create_filter()
            if temp_filter is None:
                return
        except Exception:
            return
        
        column = self.column_combo.currentText()
        if column not in self.df.columns:
            return
        
        matching_rows = []
        for idx, row in self.df.iterrows():
            if temp_filter.matches(row[column]):
                matching_rows.append(idx)
        
        count = len(matching_rows)
        self.preview_count_label.setText(f"{count} row{'s' if count != 1 else ''} match")
        
        preview_rows = matching_rows[:10]
        self.preview_table.clear()
        
        if preview_rows:
            self.preview_table.setRowCount(len(preview_rows))
            self.preview_table.setColumnCount(len(self.df.columns))
            self.preview_table.setHorizontalHeaderLabels([str(c) for c in self.df.columns])
            
            for table_row, df_idx in enumerate(preview_rows):
                for col_idx, col_name in enumerate(self.df.columns):
                    value = self.df.iloc[df_idx][col_name]
                    item = QTableWidgetItem(str(value))
                    
                    if col_name == column:
                        # Subtle blue highlight for matching column
                        item.setBackground(QColor(219, 234, 254))  # Light blue
                    
                    self.preview_table.setItem(table_row, col_idx, item)
            
            self.preview_table.resizeColumnsToContents()
            self.preview_table.horizontalHeader().setStretchLastSection(True)
    
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
