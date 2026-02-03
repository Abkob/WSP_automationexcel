"""
Combined Filter System - Filters merge within same tab, optional copy to new tab.

Key Features:
1. Multiple filters on same tab = AND logic (all must match)
2. Each tab can have multiple filters that work together
3. When creating new tab, option to:
   - Start fresh (no filters)
   - Copy filters from current tab
   - Copy filters from any tab
4. Filters within a tab are COMBINED/MERGED
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QRadioButton, QButtonGroup, QComboBox,
    QGroupBox, QCheckBox, QDialogButtonBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from typing import List, Optional


class FilterCombinationMode:
    """Defines how filters work together in a tab."""
    
    AND = "and"  # All filters must match (default)
    OR = "or"    # Any filter can match
    
    @staticmethod
    def get_display_name(mode: str) -> str:
        if mode == FilterCombinationMode.AND:
            return "Match ALL filters (AND)"
        elif mode == FilterCombinationMode.OR:
            return "Match ANY filter (OR)"
        return "Unknown"


class NewTabWithOptionsDialog(QDialog):
    """Dialog to create new tab with options to copy filters."""
    
    def __init__(self, existing_tabs: List[dict], parent=None):
        """
        Args:
            existing_tabs: List of dicts with 'name' and 'filters' keys
        """
        super().__init__(parent)
        
        self.existing_tabs = existing_tabs
        self.result_name = None
        self.result_copy_from = None
        self.result_filters = []
        self.result_combination_mode = FilterCombinationMode.AND
        
        self.setWindowTitle("Create New Tab")
        self.setMinimumWidth(550)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("Create New Tab")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #000000;")
        layout.addWidget(title)
        
        # Tab name
        name_group = QGroupBox("Tab Name")
        name_group.setStyleSheet("QGroupBox { font-weight: bold; color: #000000; }")
        name_layout = QVBoxLayout(name_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., High Performers, Engineering Review, My Selections")
        name_layout.addWidget(self.name_edit)
        
        # Quick presets
        preset_label = QLabel("Quick Presets:")
        preset_label.setStyleSheet("color: #666666; font-weight: normal; font-size: 9pt;")
        name_layout.addWidget(preset_label)
        
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(6)
        
        presets = ["High Performers", "Need Review", "Accepted", "Rejected", "My Selections"]
        for preset in presets:
            btn = QPushButton(preset)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F8F8F8;
                    border: 2px solid #CCCCCC;
                    border-radius: 3px;
                    padding: 4px 8px;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #E6F2FF;
                    border-color: #0066CC;
                }
            """)
            btn.clicked.connect(lambda checked, p=preset: self.name_edit.setText(p))
            preset_layout.addWidget(btn)
        
        name_layout.addLayout(preset_layout)
        layout.addWidget(name_group)
        
        # Filter options
        filter_group = QGroupBox("Initial Filters")
        filter_group.setStyleSheet("QGroupBox { font-weight: bold; color: #000000; }")
        filter_layout = QVBoxLayout(filter_group)
        
        self.filter_button_group = QButtonGroup()
        
        # Option 1: Start fresh
        self.fresh_radio = QRadioButton("Start with no filters (empty tab)")
        self.fresh_radio.setStyleSheet("QRadioButton { color: #000000; font-weight: normal; }")
        self.fresh_radio.setChecked(True)
        self.filter_button_group.addButton(self.fresh_radio, 0)
        filter_layout.addWidget(self.fresh_radio)
        
        # Option 2: Copy from current tab
        if len(self.existing_tabs) > 0 and self.existing_tabs[0].get('filters'):
            current_tab = self.existing_tabs[0]
            filter_count = len(current_tab.get('filters', []))
            self.copy_current_radio = QRadioButton(
                f"Copy filters from current tab '{current_tab['name']}' ({filter_count} filters)"
            )
            self.copy_current_radio.setStyleSheet("QRadioButton { color: #000000; font-weight: normal; }")
            self.filter_button_group.addButton(self.copy_current_radio, 1)
            filter_layout.addWidget(self.copy_current_radio)
            
            # Show what filters will be copied
            if filter_count > 0:
                filters_preview = QLabel("  → " + ", ".join([str(f) for f in current_tab['filters'][:3]]))
                if filter_count > 3:
                    filters_preview.setText(filters_preview.text() + f" ... (+{filter_count - 3} more)")
                filters_preview.setStyleSheet("color: #666666; font-size: 9pt; margin-left: 20px;")
                filters_preview.setWordWrap(True)
                filter_layout.addWidget(filters_preview)
        
        # Option 3: Copy from another tab
        if len(self.existing_tabs) > 1:
            self.copy_other_radio = QRadioButton("Copy filters from another tab:")
            self.copy_other_radio.setStyleSheet("QRadioButton { color: #000000; font-weight: normal; }")
            self.filter_button_group.addButton(self.copy_other_radio, 2)
            filter_layout.addWidget(self.copy_other_radio)
            
            self.tab_combo = QComboBox()
            self.tab_combo.setEnabled(False)
            for tab in self.existing_tabs[1:]:  # Skip first (current)
                filter_count = len(tab.get('filters', []))
                self.tab_combo.addItem(f"{tab['name']} ({filter_count} filters)", tab)
            filter_layout.addWidget(self.tab_combo)
            
            self.copy_other_radio.toggled.connect(lambda checked: self.tab_combo.setEnabled(checked))
        
        layout.addWidget(filter_group)
        
        # Filter combination mode
        mode_group = QGroupBox("Filter Combination Mode (when multiple filters)")
        mode_group.setStyleSheet("QGroupBox { font-weight: bold; color: #000000; }")
        mode_layout = QVBoxLayout(mode_group)
        
        info_label = QLabel("When this tab has multiple filters, how should they work together?")
        info_label.setStyleSheet("color: #666666; font-size: 9pt; font-weight: normal;")
        info_label.setWordWrap(True)
        mode_layout.addWidget(info_label)
        
        self.mode_button_group = QButtonGroup()
        
        self.and_radio = QRadioButton("Match ALL filters (AND) - Student must satisfy ALL filters")
        self.and_radio.setStyleSheet("QRadioButton { color: #000000; font-weight: normal; }")
        self.and_radio.setChecked(True)
        self.mode_button_group.addButton(self.and_radio, 0)
        mode_layout.addWidget(self.and_radio)
        
        and_example = QLabel("  Example: GPA >= 3.5 AND Status = Active → Shows only students with BOTH")
        and_example.setStyleSheet("color: #0066CC; font-size: 9pt; margin-left: 20px;")
        and_example.setWordWrap(True)
        mode_layout.addWidget(and_example)
        
        self.or_radio = QRadioButton("Match ANY filter (OR) - Student needs ANY filter to match")
        self.or_radio.setStyleSheet("QRadioButton { color: #000000; font-weight: normal; }")
        self.mode_button_group.addButton(self.or_radio, 1)
        mode_layout.addWidget(self.or_radio)
        
        or_example = QLabel("  Example: GPA >= 3.5 OR Scholarship > 0 → Shows students with EITHER")
        or_example.setStyleSheet("color: #008000; font-size: 9pt; margin-left: 20px;")
        or_example.setWordWrap(True)
        mode_layout.addWidget(or_example)
        
        layout.addWidget(mode_group)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.name_edit.setFocus()
    
    def _on_accept(self):
        """Handle OK button."""
        name = self.name_edit.text().strip()
        
        if not name:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Missing Name", "Please enter a tab name.")
            return
        
        self.result_name = name
        
        # Determine filter combination mode
        if self.or_radio.isChecked():
            self.result_combination_mode = FilterCombinationMode.OR
        else:
            self.result_combination_mode = FilterCombinationMode.AND
        
        # Determine which filters to copy
        if hasattr(self, 'copy_current_radio') and self.copy_current_radio.isChecked():
            # Copy from current tab
            self.result_filters = self.existing_tabs[0].get('filters', [])[:]
        elif hasattr(self, 'copy_other_radio') and self.copy_other_radio.isChecked():
            # Copy from selected tab
            selected_tab = self.tab_combo.currentData()
            if selected_tab:
                self.result_filters = selected_tab.get('filters', [])[:]
        else:
            # Start fresh
            self.result_filters = []
        
        self.accept()
    
    def get_result(self) -> dict:
        """Get the dialog result."""
        return {
            'name': self.result_name,
            'filters': self.result_filters,
            'combination_mode': self.result_combination_mode
        }


class TabFilterPanel(QGroupBox):
    """Panel showing filters for a specific tab with combination mode."""
    
    filterAdded = pyqtSignal(object)
    filterRemoved = pyqtSignal(object)
    combinationModeChanged = pyqtSignal(str)
    
    def __init__(self, tab_name: str, parent=None):
        super().__init__(f"Filters for: {tab_name}", parent)
        
        self.tab_name = tab_name
        self.filters = []
        self.combination_mode = FilterCombinationMode.AND
        
        self.setStyleSheet("QGroupBox { font-weight: bold; color: #000000; }")
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Top controls
        controls_layout = QHBoxLayout()
        
        # Add filter button
        self.add_btn = QPushButton("+ Add Filter")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #0066CC;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0052A3;
            }
        """)
        controls_layout.addWidget(self.add_btn)
        
        # Combination mode toggle
        self.mode_label = QLabel("Combine with:")
        self.mode_label.setStyleSheet("color: #000000; font-weight: normal;")
        controls_layout.addWidget(self.mode_label)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("AND (all must match)", FilterCombinationMode.AND)
        self.mode_combo.addItem("OR (any can match)", FilterCombinationMode.OR)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        controls_layout.addWidget(self.mode_combo)
        
        controls_layout.addStretch()
        
        # Clear all button
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #CC0000;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #990000;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)
        self.clear_btn.setEnabled(False)
        controls_layout.addWidget(self.clear_btn)
        
        layout.addLayout(controls_layout)
        
        # Filter list
        self.filter_list_widget = QListWidget()
        self.filter_list_widget.setStyleSheet("""
            QListWidget {
                background-color: #FFFFFF;
                border: 2px solid #CCCCCC;
                border-radius: 4px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #EEEEEE;
            }
            QListWidget::item:hover {
                background-color: #E6F2FF;
            }
        """)
        self.filter_list_widget.setMaximumHeight(150)
        layout.addWidget(self.filter_list_widget)
        
        self._update_display()
    
    def add_filter(self, filter_rule):
        """Add a filter to this tab."""
        self.filters.append(filter_rule)
        self._update_display()
        self.filterAdded.emit(filter_rule)
    
    def remove_filter(self, filter_rule):
        """Remove a filter."""
        if filter_rule in self.filters:
            self.filters.remove(filter_rule)
            self._update_display()
            self.filterRemoved.emit(filter_rule)
    
    def clear_all_filters(self):
        """Clear all filters."""
        self.filters.clear()
        self._update_display()
    
    def set_filters(self, filters: List):
        """Set filters (for copying from another tab)."""
        self.filters = filters[:]
        self._update_display()
    
    def set_combination_mode(self, mode: str):
        """Set combination mode."""
        self.combination_mode = mode
        index = 0 if mode == FilterCombinationMode.AND else 1
        self.mode_combo.setCurrentIndex(index)
    
    def _on_mode_changed(self, index):
        """Handle combination mode change."""
        self.combination_mode = self.mode_combo.currentData()
        self.combinationModeChanged.emit(self.combination_mode)
        self._update_display()
    
    def _update_display(self):
        """Update the filter list display."""
        self.filter_list_widget.clear()
        
        if not self.filters:
            item = QListWidgetItem("No filters applied")
            item.setFlags(Qt.NoItemFlags)
            item.setForeground(QColor("#999999"))
            self.filter_list_widget.addItem(item)
            self.clear_btn.setEnabled(False)
        else:
            for i, filter_rule in enumerate(self.filters):
                # Create item with AND/OR connector
                if i > 0:
                    connector_text = " AND " if self.combination_mode == FilterCombinationMode.AND else " OR "
                    connector_item = QListWidgetItem(connector_text)
                    connector_item.setFlags(Qt.NoItemFlags)
                    connector_item.setForeground(QColor("#0066CC" if self.combination_mode == FilterCombinationMode.AND else "#008000"))
                    connector_item.setFont(QFont("Arial", 9, QFont.Bold))
                    self.filter_list_widget.addItem(connector_item)
                
                item = QListWidgetItem(f"  {str(filter_rule)}")
                item.setData(Qt.UserRole, filter_rule)
                self.filter_list_widget.addItem(item)
            
            self.clear_btn.setEnabled(True)
            
            # Update title with count
            count = len(self.filters)
            mode_text = "AND" if self.combination_mode == FilterCombinationMode.AND else "OR"
            self.setTitle(f"Filters for: {self.tab_name} ({count} filters, {mode_text} mode)")


# Example usage in main_window.py:
"""
def _on_new_tab_clicked(self):
    # Gather existing tabs info
    existing_tabs = []
    for i in range(self.tab_widget.count()):
        tab_widget = self.tab_widget.widget(i)
        if hasattr(tab_widget, 'filter_panel'):
            existing_tabs.append({
                'name': self.tab_widget.tabText(i),
                'filters': tab_widget.filter_panel.filters[:]
            })
    
    # Show dialog
    dialog = NewTabWithOptionsDialog(existing_tabs, self)
    
    if dialog.exec_():
        result = dialog.get_result()
        
        # Create new tab
        new_tab = self._create_tab_with_filters(
            result['name'],
            result['filters'],
            result['combination_mode']
        )
        
        self.tab_widget.addTab(new_tab, result['name'])

def _create_tab_with_filters(self, name, initial_filters, combination_mode):
    # Create tab widget
    tab = QWidget()
    layout = QVBoxLayout(tab)
    
    # Add filter panel
    filter_panel = TabFilterPanel(name)
    filter_panel.set_filters(initial_filters)
    filter_panel.set_combination_mode(combination_mode)
    filter_panel.add_btn.clicked.connect(lambda: self._add_filter_to_tab(tab))
    filter_panel.clear_btn.clicked.connect(filter_panel.clear_all_filters)
    
    layout.addWidget(filter_panel)
    
    # Add table view
    table = StyledTableView()
    proxy = SmartSearchProxy()
    proxy.setSourceModel(self.model)
    table.setModel(proxy)
    
    layout.addWidget(table)
    
    # Store reference
    tab.filter_panel = filter_panel
    tab.table = table
    tab.proxy = proxy
    
    return tab
"""
