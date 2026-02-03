"""
Tab-First Filter System - Create tabs, then apply filters to each tab independently.

Workflow:
1. Click "+ New Tab" button
2. Name it (e.g., "High Performers", "Engineering Review", "My Selections")
3. In that tab, apply filters specific to that view
4. Switch tabs - each has its own independent filters
5. Export, rename, or close tabs as needed
"""

from PyQt5.QtWidgets import (
    QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QDialog, QDialogButtonBox, QMenu, QToolButton,
    QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon
from typing import Dict, List
from styles import AppTheme


class TabFilterManager:
    """Manages filters per tab - each tab has its own filter set."""
    
    def __init__(self):
        self.tab_filters: Dict[int, List] = {}  # tab_index -> [filters]
    
    def add_filter_to_tab(self, tab_index: int, filter_rule):
        """Add a filter to a specific tab."""
        if tab_index not in self.tab_filters:
            self.tab_filters[tab_index] = []
        self.tab_filters[tab_index].append(filter_rule)
    
    def remove_filter_from_tab(self, tab_index: int, filter_rule):
        """Remove a filter from a specific tab."""
        if tab_index in self.tab_filters:
            if filter_rule in self.tab_filters[tab_index]:
                self.tab_filters[tab_index].remove(filter_rule)
    
    def get_filters_for_tab(self, tab_index: int) -> List:
        """Get all filters for a specific tab."""
        return self.tab_filters.get(tab_index, [])
    
    def clear_tab_filters(self, tab_index: int):
        """Clear all filters for a tab."""
        if tab_index in self.tab_filters:
            self.tab_filters[tab_index].clear()
    
    def remove_tab(self, tab_index: int):
        """Remove all filters when tab is closed."""
        if tab_index in self.tab_filters:
            del self.tab_filters[tab_index]
        
        # Reindex remaining tabs
        new_filters = {}
        for idx, filters in self.tab_filters.items():
            if idx > tab_index:
                new_filters[idx - 1] = filters
            else:
                new_filters[idx] = filters
        self.tab_filters = new_filters


class TabWithFilters(QWidget):
    """A tab that can have its own filters applied."""
    
    filterAdded = pyqtSignal(object)  # filter_rule
    filterRemoved = pyqtSignal(object)  # filter_rule
    
    def __init__(self, tab_name: str, table_view, parent=None):
        super().__init__(parent)
        self.tab_name = tab_name
        self.table_view = table_view
        self.filters = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup tab UI with filter panel."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Top bar: Tab info and filter controls
        top_bar = QFrame()
        top_bar.setFrameStyle(QFrame.StyledPanel)
        top_bar.setStyleSheet("""
            QFrame {
                background-color: #F9FAFB;
                border: 2px solid #D1D5DB;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        top_layout = QHBoxLayout(top_bar)
        
        # Tab info
        info_label = QLabel(f"View: {self.tab_name}")
        info_label.setStyleSheet(f"font-weight: 600; color: {AppTheme.TEXT}; font-size: 11pt;")
        top_layout.addWidget(info_label)
        
        # Filter count
        self.filter_count_label = QLabel("0 filters active")
        self.filter_count_label.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY}; font-size: 10pt;")
        top_layout.addWidget(self.filter_count_label)
        
        top_layout.addStretch()
        
        # Add filter button
        self.add_filter_btn = QPushButton("+ Add Filter to This Tab")
        self.add_filter_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
        """)
        top_layout.addWidget(self.add_filter_btn)
        
        # Clear filters button
        self.clear_filters_btn = QPushButton("Clear All Filters")
        self.clear_filters_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
            QPushButton:disabled {
                background-color: #D1D5DB;
                color: #6B7280;
            }
        """)
        self.clear_filters_btn.setEnabled(False)
        top_layout.addWidget(self.clear_filters_btn)
        
        layout.addWidget(top_bar)
        
        # Active filters display
        self.filters_frame = QFrame()
        self.filters_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 2px solid #D1D5DB;
                border-radius: 4px;
            }
        """)
        self.filters_layout = QHBoxLayout(self.filters_frame)
        self.filters_layout.setContentsMargins(8, 8, 8, 8)
        
        self.no_filters_label = QLabel("No filters applied to this tab")
        self.no_filters_label.setStyleSheet("color: #999999; font-style: italic;")
        self.filters_layout.addWidget(self.no_filters_label)
        self.filters_layout.addStretch()
        
        layout.addWidget(self.filters_frame)
        
        # Main table view
        layout.addWidget(self.table_view, 1)
    
    def add_filter(self, filter_rule):
        """Add a filter to this tab."""
        self.filters.append(filter_rule)
        self._update_filter_display()
        self.filterAdded.emit(filter_rule)
    
    def remove_filter(self, filter_rule):
        """Remove a filter from this tab."""
        if filter_rule in self.filters:
            self.filters.remove(filter_rule)
            self._update_filter_display()
            self.filterRemoved.emit(filter_rule)
    
    def clear_all_filters(self):
        """Clear all filters from this tab."""
        self.filters.clear()
        self._update_filter_display()
    
    def _update_filter_display(self):
        """Update the visual display of active filters."""
        # Clear existing filter chips
        while self.filters_layout.count() > 0:
            item = self.filters_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.filters:
            self.no_filters_label = QLabel("No filters applied to this tab")
            self.no_filters_label.setStyleSheet("color: #999999; font-style: italic;")
            self.filters_layout.addWidget(self.no_filters_label)
            self.filters_layout.addStretch()
            self.filter_count_label.setText("0 filters active")
            self.clear_filters_btn.setEnabled(False)
        else:
            # Add filter chips
            for filter_rule in self.filters:
                chip = self._create_filter_chip(filter_rule)
                self.filters_layout.addWidget(chip)
            
            self.filters_layout.addStretch()
            
            count = len(self.filters)
            self.filter_count_label.setText(f"{count} filter{'s' if count != 1 else ''} active")
            self.clear_filters_btn.setEnabled(True)
    
    def _create_filter_chip(self, filter_rule):
        """Create a visual chip for a filter."""
        chip = QFrame()
        chip.setStyleSheet("""
            QFrame {
                background-color: #DBEAFE;
                border: 2px solid #2563EB;
                border-radius: 6px;
                padding: 6px 10px;
            }
            QFrame:hover {
                background-color: #F3F4F6;
            }
        """)
        
        chip_layout = QHBoxLayout(chip)
        chip_layout.setContentsMargins(6, 4, 6, 4)
        chip_layout.setSpacing(8)
        
        # Filter text
        label = QLabel(str(filter_rule))
        label.setStyleSheet(f"background: transparent; border: none; color: {AppTheme.TEXT}; font-weight: 600;")
        chip_layout.addWidget(label)
        
        # Remove button
        remove_btn = QPushButton("X")
        remove_btn.setFixedSize(20, 20)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: #FFFFFF;
                border: none;
                font-size: 14px;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_filter(filter_rule))
        chip_layout.addWidget(remove_btn)
        
        return chip


class IndependentTabWidget(QTabWidget):
    """Tab widget where each tab has independent filters."""
    
    newTabRequested = pyqtSignal(str)  # tab_name
    tabRemoved = pyqtSignal(int)  # tab_index
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.tab_filter_manager = TabFilterManager()
        
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        
        self.tabCloseRequested.connect(self._on_close_tab)
        
        # Add "+ New Tab" button
        self.setCornerWidget(self._create_new_tab_button(), Qt.TopRightCorner)
        
        self._setup_style()
    
    def _setup_style(self):
        """Apply styling."""
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #D1D5DB;
                background-color: #FFFFFF;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #F9FAFB;
                color: #6B7280;
                border: 2px solid #D1D5DB;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 12px 20px;
                margin-right: 2px;
                font-weight: bold;
                font-size: 10pt;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: #2563EB;
                border-bottom: 3px solid #FFFFFF;
            }
            QTabBar::tab:hover {
                background-color: #F3F4F6;
            }
        """)
    
    def _create_new_tab_button(self):
        """Create the + New Tab button."""
        btn = QPushButton("+ New Tab")
        btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 10pt;
                margin: 4px;
            }
            QPushButton:hover {
                background-color: #0EA371;
            }
        """)
        btn.clicked.connect(self._on_new_tab_clicked)
        return btn
    
    def _on_new_tab_clicked(self):
        """Handle new tab button click."""
        dialog = NewTabDialog(self)
        
        if dialog.exec_():
            tab_name = dialog.get_tab_name()
            if tab_name:
                self.newTabRequested.emit(tab_name)
    
    def add_custom_tab(self, tab_name: str, tab_widget: TabWithFilters):
        """Add a new custom tab."""
        index = self.addTab(tab_widget, tab_name)
        
        # Don't allow closing the first tab
        if self.count() == 1:
            self.tabBar().setTabButton(0, self.tabBar().RightSide, None)
        
        self.setCurrentIndex(index)
        return index
    
    def _on_close_tab(self, index):
        """Handle tab close."""
        if index == 0:
            return  # Don't close first tab
        
        tab_name = self.tabText(index)
        
        reply = QMessageBox.question(
            self,
            "Close Tab",
            f"Close '{tab_name}' tab?\n\nThis will remove all filters applied to this tab.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            widget = self.widget(index)
            self.removeTab(index)
            widget.deleteLater()
            
            self.tab_filter_manager.remove_tab(index)
            self.tabRemoved.emit(index)


class NewTabDialog(QDialog):
    """Dialog to create a new tab."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Create New Tab")
        self.setMinimumWidth(450)
        
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
        title.setStyleSheet(f"color: {AppTheme.TEXT};")
        layout.addWidget(title)
        
        # Info
        info = QLabel("Give your tab a name. You can apply filters to it after creation.")
        info.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY};")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Name input
        name_label = QLabel("Tab Name:")
        name_label.setStyleSheet(f"color: {AppTheme.TEXT}; font-weight: 600;")
        layout.addWidget(name_label)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., High Performers, Engineering Review, My Selections")
        layout.addWidget(self.name_edit)
        
        # Quick presets
        preset_label = QLabel("Quick Presets:")
        preset_label.setStyleSheet(f"color: {AppTheme.TEXT}; font-weight: 600; margin-top: 10px;")
        layout.addWidget(preset_label)
        
        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(8)
        
        presets = [
            "High Performers",
            "Need Review", 
            "Accepted",
            "Rejected",
            "Waitlist",
            "My Selections"
        ]
        
        for preset in presets:
            btn = QPushButton(preset)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F9FAFB;
                    color: #111827;
                    border: 2px solid #D1D5DB;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #F3F4F6;
                    border-color: #2563EB;
                }
            """)
            btn.clicked.connect(lambda checked, p=preset: self.name_edit.setText(p))
            preset_layout.addWidget(btn)
        
        layout.addLayout(preset_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.name_edit.setFocus()
    
    def get_tab_name(self):
        """Get the entered tab name."""
        return self.name_edit.text().strip()


# Example integration in main_window.py:
"""
def _setup_ui(self):
    # Create independent tab widget
    self.tab_widget = IndependentTabWidget()
    self.tab_widget.newTabRequested.connect(self._on_create_new_tab)
    self.tab_widget.tabRemoved.connect(self._on_tab_removed)
    
    # Add initial "All Students" tab
    self._create_initial_tab()
    
    layout.addWidget(self.tab_widget)

def _create_initial_tab(self):
    # Create table for "All Students"
    table = StyledTableView()
    proxy = SmartSearchProxy()
    proxy.setSourceModel(self.model)
    table.setModel(proxy)
    
    # Wrap in TabWithFilters
    tab_widget = TabWithFilters("All Students", table)
    tab_widget.add_filter_btn.clicked.connect(lambda: self._add_filter_to_current_tab())
    tab_widget.clear_filters_btn.clicked.connect(lambda: self._clear_current_tab_filters())
    
    self.tab_widget.add_custom_tab("All Students", tab_widget)

def _on_create_new_tab(self, tab_name):
    # Create new table view
    table = StyledTableView()
    proxy = SmartSearchProxy()
    proxy.setSourceModel(self.model)
    table.setModel(proxy)
    
    # Wrap in TabWithFilters
    tab_widget = TabWithFilters(tab_name, table)
    tab_widget.add_filter_btn.clicked.connect(lambda: self._add_filter_to_current_tab())
    tab_widget.clear_filters_btn.clicked.connect(lambda: self._clear_current_tab_filters())
    
    # Add to tab widget
    self.tab_widget.add_custom_tab(tab_name, tab_widget)

def _add_filter_to_current_tab(self):
    # Get current tab
    current_tab = self.tab_widget.currentWidget()
    
    if isinstance(current_tab, TabWithFilters):
        # Show filter dialog
        dialog = FilterDialog(self.df, parent=self)
        
        if dialog.exec_():
            filter_rule = dialog.get_filter()
            if filter_rule:
                # Add filter to this specific tab
                current_tab.add_filter(filter_rule)
                
                # Apply filter to tab's proxy
                # (You'll need to implement proxy logic to handle tab-specific filters)

def _clear_current_tab_filters(self):
    current_tab = self.tab_widget.currentWidget()
    
    if isinstance(current_tab, TabWithFilters):
        current_tab.clear_all_filters()
"""
