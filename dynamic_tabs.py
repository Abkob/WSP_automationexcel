"""
Dynamic Tab System - Each filter gets its own tab!

Concept:
- "All Students" tab (always present)
- Each filter creates a new tab automatically
- Tab shows filter name (e.g., "GPA >= 3.5", "Status: Active")
- Can view multiple filter results simultaneously
- Close tab = remove filter
- Rename tabs for better organization
"""

from PyQt5.QtWidgets import (
    QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QDialog, QDialogButtonBox, QMenu
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from styles import AppTheme

class DynamicTabWidget(QTabWidget):
    """Tab widget where each tab represents a filter view."""
    
    tabRenamed = pyqtSignal(int, str)  # tab_index, new_name
    tabClosed = pyqtSignal(int)  # tab_index
    duplicateTabRequested = pyqtSignal(int)  # tab_index
    exportTabRequested = pyqtSignal(int)  # tab_index
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        
        # Custom close button behavior
        self.tabCloseRequested.connect(self._on_tab_close_requested)
        
        # Enable context menu on tabs
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_tab_context_menu)
        
        self._setup_style()
    
    def _setup_style(self):
        """Apply clean styling."""
        self.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 2px solid {AppTheme.BORDER};
                background-color: {AppTheme.BACKGROUND};
                border-radius: 6px;
            }}
            QTabBar::tab {{
                background-color: {AppTheme.GRAY_50};
                color: {AppTheme.TEXT_SECONDARY};
                border: 2px solid {AppTheme.BORDER};
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 10px 16px;
                margin-right: 2px;
                font-weight: 600;
                font-size: 10pt;
                min-width: 120px;
            }}
            QTabBar::tab:selected {{
                background-color: {AppTheme.BACKGROUND};
                color: {AppTheme.PRIMARY};
                border-bottom: 2px solid {AppTheme.BACKGROUND};
            }}
            QTabBar::tab:hover {{
                background-color: {AppTheme.GRAY_100};
            }}
            QTabBar::tab:!selected {{
                margin-top: 2px;
            }}
            QTabBar::close-button {{
                image: none;
                subcontrol-position: right;
                width: 16px;
                height: 16px;
            }}
            QTabBar::close-button:hover {{
                background-color: {AppTheme.ERROR};
                border-radius: 8px;
            }}
        """)
    
    def add_filter_tab(self, filter_rule, table_widget, insert_index: int = None, tab_name: str = None,
                       switch_to: bool = True):
        """Add a new tab for a filter."""
        # Create tab name from filter
        tab_name = tab_name or self._generate_tab_name(filter_rule)
        
        # Add the tab
        if insert_index is not None and 0 <= insert_index <= self.count():
            index = self.insertTab(insert_index, table_widget, tab_name)
        else:
            index = self.addTab(table_widget, tab_name)
        
        # Make "All Students" tab not closable
        if self.count() == 1:
            self.tabBar().setTabButton(0, self.tabBar().RightSide, None)
        
        # Switch to new tab if requested
        if switch_to:
            self.setCurrentIndex(index)
        
        return index
    
    def _generate_tab_name(self, filter_rule):
        """Generate a readable tab name from filter."""
        from models import NumericFilter, TextFilter, DateFilter
        
        if isinstance(filter_rule, NumericFilter):
            # "GPA >= 3.5"
            return f"{filter_rule.column} {filter_rule.operator} {filter_rule.value}"
        
        elif isinstance(filter_rule, TextFilter):
            # "Status: Active, Probation"
            tokens = ", ".join(filter_rule.tokens[:2])
            if len(filter_rule.tokens) > 2:
                tokens += "..."
            return f"{filter_rule.column}: {tokens}"
        
        elif isinstance(filter_rule, DateFilter):
            # "Date: 2025-01 to 2025-12"
            if filter_rule.start_date and filter_rule.end_date:
                return f"{filter_rule.column}: {filter_rule.start_date.strftime('%Y-%m')} to {filter_rule.end_date.strftime('%Y-%m')}"
            elif filter_rule.start_date:
                return f"{filter_rule.column}: After {filter_rule.start_date.strftime('%Y-%m-%d')}"
            elif filter_rule.end_date:
                return f"{filter_rule.column}: Before {filter_rule.end_date.strftime('%Y-%m-%d')}"
        
        return f"{filter_rule.column} Filter"
    
    def _on_tab_close_requested(self, index):
        """Handle tab close request."""
        # Don't close "All Students" tab or Filtered tab
        if index == 0:
            return

        widget = self.widget(index)
        tab_kind = getattr(widget, "tab_kind", None)
        if tab_kind == "filtered":
            return
        
        # Confirm close
        tab_name = self.tabText(index)
        from PyQt5.QtWidgets import QMessageBox
        
        if tab_kind == "rule":
            message = f"Remove the '{tab_name}' tab?\n\nThis will remove the associated rule."
        else:
            message = f"Close the '{tab_name}' tab?"
        
        reply = QMessageBox.question(
            self,
            "Close Tab",
            message,
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.tabClosed.emit(index)
    
    def _show_tab_context_menu(self, pos):
        """Show context menu on tab."""
        tab_bar = self.tabBar()
        local_pos = tab_bar.mapFrom(self, pos)
        index = tab_bar.tabAt(local_pos)
        if index >= 0:
            global_pos = tab_bar.mapToGlobal(local_pos)
            self._show_menu_for_tab(index, global_pos)
    
    def _show_menu_for_tab(self, index, global_pos):
        """Show context menu for specific tab."""
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
        
        widget = self.widget(index)
        tab_kind = getattr(widget, "tab_kind", None)

        # Rename action
        rename_action = menu.addAction("Rename Tab...")
        rename_action.triggered.connect(lambda: self._rename_tab(index))
        
        # Duplicate action (create another view)
        if index > 0 and tab_kind != "filtered":
            duplicate_action = menu.addAction("Duplicate View")
            duplicate_action.triggered.connect(lambda: self._duplicate_tab(index))
        
        menu.addSeparator()
        
        # Export this view
        export_action = menu.addAction("Export This View...")
        export_action.triggered.connect(lambda: self._export_tab(index))
        
        if index > 0 and tab_kind != "filtered":
            menu.addSeparator()

            # Close action
            close_action = menu.addAction("Close Tab")
            close_action.triggered.connect(lambda: self._on_tab_close_requested(index))
        
        # Show menu
        menu.exec_(global_pos)
    
    def _rename_tab(self, index):
        """Rename a tab."""
        current_name = self.tabText(index)
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Rename Tab")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        label = QLabel("Enter new tab name:")
        label.setStyleSheet(f"color: {AppTheme.TEXT}; font-weight: 600;")
        layout.addWidget(label)
        
        line_edit = QLineEdit()
        line_edit.setText(current_name)
        line_edit.selectAll()
        layout.addWidget(line_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_():
            new_name = line_edit.text().strip()
            if new_name:
                self.setTabText(index, new_name)
                self.tabRenamed.emit(index, new_name)
    
    def _duplicate_tab(self, index):
        """Signal to duplicate this tab's view."""
        self.duplicateTabRequested.emit(index)
    
    def _export_tab(self, index):
        """Signal to export this tab's data."""
        self.exportTabRequested.emit(index)


class TabSuggestions:
    """Suggest useful tab configurations."""
    
    @staticmethod
    def get_preset_tabs():
        """Get common tab configurations."""
        return {
            "Admissions Workflow": [
                {"name": "All Applications", "filter": None},
                {"name": "High GPA (3.5+)", "filter": ("GPA", ">=", 3.5)},
                {"name": "Medium GPA (2.5-3.5)", "filter": ("GPA", "range", 2.5, 3.5)},
                {"name": "Low GPA (<2.5)", "filter": ("GPA", "<", 2.5)},
                {"name": "Active Status", "filter": ("Status", "contains", "Active")},
                {"name": "Scholarship Eligible", "filter": ("Scholarship", ">", 0)},
            ],
            
            "Department Review": [
                {"name": "All Departments", "filter": None},
                {"name": "Engineering", "filter": ("Department", "contains", "Engineering")},
                {"name": "Business", "filter": ("Department", "contains", "Business")},
                {"name": "Sciences", "filter": ("Department", "contains", "Science")},
                {"name": "Arts", "filter": ("Department", "contains", "Arts")},
            ],
            
            "Status Tracking": [
                {"name": "All Students", "filter": None},
                {"name": "Active", "filter": ("Status", "contains", "Active")},
                {"name": "Probation", "filter": ("Status", "contains", "Probation")},
                {"name": "Suspended", "filter": ("Status", "contains", "Suspended")},
                {"name": "Graduated", "filter": ("Status", "contains", "Graduate")},
            ],
            
            "Scholarship Review": [
                {"name": "All Students", "filter": None},
                {"name": "Full Scholarship (2000+)", "filter": ("Scholarship", ">=", 2000)},
                {"name": "Partial Scholarship (500-2000)", "filter": ("Scholarship", "range", 500, 2000)},
                {"name": "No Scholarship", "filter": ("Scholarship", "==", 0)},
            ],
            
            "Custom Workflow": [
                {"name": "All Students", "filter": None},
            ]
        }


class PresetTabDialog(QDialog):
    """Dialog to select preset tab configurations."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Load Preset Tab Layout")
        self.setMinimumSize(600, 400)
        
        self.selected_preset = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Choose a Preset Tab Layout")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {AppTheme.TEXT};")
        layout.addWidget(title)
        
        info = QLabel("Preset layouts create multiple tabs for common workflows.")
        info.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY};")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Preset buttons
        from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout as QVBox
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBox(scroll_widget)
        
        presets = TabSuggestions.get_preset_tabs()
        
        for preset_name, tabs in presets.items():
            btn = QPushButton(f"{preset_name} ({len(tabs)} tabs)")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F9FAFB;
                    color: #111827;
                    border: 2px solid #D1D5DB;
                    border-radius: 4px;
                    padding: 12px;
                    text-align: left;
                    font-size: 11pt;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #F3F4F6;
                    border-color: #2563EB;
                }
            """)
            btn.clicked.connect(lambda checked, p=preset_name: self._select_preset(p))
            scroll_layout.addWidget(btn)
            
            # Show tab names
            tab_names = ", ".join([t["name"] for t in tabs[:3]])
            if len(tabs) > 3:
                tab_names += "..."
            
            desc = QLabel(f"  Tabs: {tab_names}")
            desc.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY}; padding-left: 20px;")
            scroll_layout.addWidget(desc)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Cancel)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _select_preset(self, preset_name):
        """Select a preset."""
        self.selected_preset = preset_name
        self.accept()
    
    def get_selected_preset(self):
        """Get the selected preset configuration."""
        if self.selected_preset:
            return TabSuggestions.get_preset_tabs()[self.selected_preset]
        return None


# Example usage in main window:
"""
# In main_window.py:

def _setup_ui(self):
    # Create dynamic tab widget
    self.tab_widget = DynamicTabWidget()
    self.tab_widget.tabClosed.connect(self._on_tab_closed)
    self.tab_widget.tabRenamed.connect(self._on_tab_renamed)
    
    # Add "All Students" tab
    self.table_all = StyledTableView()
    self.tab_widget.addTab(self.table_all, "All Students")
    
    # Add to layout
    layout.addWidget(self.tab_widget)

def _on_add_filter(self):
    # When user adds a filter, create a new tab
    dialog = FilterDialog(self.df, parent=self)
    
    if dialog.exec_():
        filter_rule = dialog.get_filter()
        if filter_rule:
            # Create new table view for this filter
            new_table = StyledTableView()
            new_proxy = SmartSearchProxy()
            new_proxy.setSourceModel(self.model)
            
            # Set this proxy to show only rows matching this filter
            new_proxy.setFilterForSpecificFilter(filter_rule)
            new_table.setModel(new_proxy)
            
            # Add tab
            self.tab_widget.add_filter_tab(filter_rule, new_table)
            
            # Store filter reference
            self.filter_tabs[tab_index] = filter_rule

def _on_tab_closed(self, index):
    # Remove the tab and its filter
    widget = self.tab_widget.widget(index)
    self.tab_widget.removeTab(index)
    widget.deleteLater()
    
    # Remove from tracking
    if index in self.filter_tabs:
        del self.filter_tabs[index]

def _on_load_preset_tabs(self):
    # Show preset dialog
    dialog = PresetTabDialog(self)
    
    if dialog.exec_():
        preset_tabs = dialog.get_selected_preset()
        
        # Clear existing tabs (except All)
        while self.tab_widget.count() > 1:
            self.tab_widget.removeTab(1)
        
        # Create tabs from preset
        for tab_config in preset_tabs[1:]:  # Skip first (All)
            # Create filter from config
            filter_rule = self._create_filter_from_config(tab_config["filter"])
            
            if filter_rule:
                # Create table and add tab
                new_table = StyledTableView()
                new_proxy = SmartSearchProxy()
                new_proxy.setSourceModel(self.model)
                new_table.setModel(new_proxy)
                
                index = self.tab_widget.addTab(new_table, tab_config["name"])
"""
