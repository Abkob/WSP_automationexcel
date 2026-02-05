"""
Main Application Window - FULLY INTEGRATED
Implements complete design document with:
- Reactive Observer Pattern
- Dynamic Filter-Based Tabs  
- Enhanced Column Navigator
- Smart Merge Dialog
- State Persistence
- All Features Working
"""

import os
import sys
import json
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QSplitter,
    QLineEdit, QComboBox, QLabel, QAction, QMenu, QToolButton,
    QMessageBox, QInputDialog, QFileDialog, QStatusBar,
    QApplication, QDialog, QDialogButtonBox, QRadioButton, QAbstractItemView
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence
import pandas as pd
import numpy as np
from typing import Optional, Dict, List

from models import DataFrameModel, FilterManager, NumericFilter, TextFilter, DateFilter, FilterRule
from proxies import SmartSearchProxy                     
from views import StyledTableView, SecondaryTableWindow, ArchiveBrowserDialog
from widgets import FilterPanel, FilterDialog
from enhanced_column_navigator import EnhancedColumnNavigator
from dynamic_tabs import DynamicTabWidget
from independent_tab_system import NewTabDialog
from presets import SavePresetDialog, LoadPresetDialog
from utils import (
    load_dataframe_from_file, add_date_column, merge_dataframes,
    export_to_excel_formatted, create_archive_snapshot, get_archive_list,
    DATE_COL_NAME, save_filters_to_file, load_filters_from_file,
    get_last_loaded_file, save_last_loaded_file
)
from styles import AppTheme
from modern_ui import ModernActionBar, CompactHeader, ModernSearchBar
from modern_filter_panel import ModernFilterPanel


class MergeDialog(QDialog):
    """Smart dialog for handling data merge/replace operations."""
    
    def __init__(self, existing_count: int, new_count: int, filepath: str, parent=None):
        super().__init__(parent)
        self.existing_count = existing_count
        self.new_count = new_count
        self.filepath = filepath
        self.result_action = None
        
        self.setWindowTitle("Data Already Loaded")
        self.setMinimumWidth(550)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("<b>You have data already loaded</b>")
        title.setStyleSheet("font-size: 13pt; color: #111827;")
        layout.addWidget(title)
        
        # Info
        info = QLabel(f"""
            <p style='color: #6B7280;'>
            Current data: <b>{self.existing_count:,}</b> students<br>
            New file: <b>{self.new_count:,}</b> students<br>
            File: <i>{os.path.basename(self.filepath)}</i>
            </p>
        """)
        layout.addWidget(info)
        
        # Separator
        separator = QLabel()
        separator.setStyleSheet("border-bottom: 2px solid #E5E7EB;")
        separator.setFixedHeight(1)
        layout.addWidget(separator)
        
        # Options label
        options_label = QLabel("<b>What would you like to do?</b>")
        options_label.setStyleSheet("font-size: 11pt; color: #111827;")
        layout.addWidget(options_label)
        
        # Option 1: Merge
        self.merge_radio = QRadioButton()
        self.merge_radio.setChecked(True)
        merge_layout = QVBoxLayout()
        merge_title = QLabel("<b>MERGE</b> - Combine datasets")
        merge_title.setStyleSheet("color: #111827; font-size: 11pt;")
        merge_desc = QLabel(f"Add new students and update duplicates<br><span style='color: #6B7280;'>-> Results in approximately {self.existing_count + self.new_count:,} students</span>")
        merge_desc.setStyleSheet("color: #374151;")
        merge_layout.addWidget(merge_title)
        merge_layout.addWidget(merge_desc)
        
        merge_widget = QWidget()
        merge_widget_layout = QHBoxLayout(merge_widget)
        merge_widget_layout.setContentsMargins(0, 0, 0, 0)
        merge_widget_layout.addWidget(self.merge_radio)
        merge_widget_layout.addLayout(merge_layout)
        merge_widget_layout.addStretch()
        
        merge_container = QWidget()
        merge_container.setStyleSheet("""
            QWidget {
                background-color: #F3F4F6;
                border: 2px solid #D1D5DB;
                border-radius: 8px;
                padding: 12px;
            }
            QWidget:hover {
                background-color: #E5E7EB;
            }
        """)
        merge_container_layout = QVBoxLayout(merge_container)
        merge_container_layout.setContentsMargins(12, 12, 12, 12)
        merge_container_layout.addWidget(merge_widget)
        layout.addWidget(merge_container)
        
        # Option 2: Replace
        self.replace_radio = QRadioButton()
        replace_layout = QVBoxLayout()
        replace_title = QLabel("<b>REPLACE</b> - Start fresh")
        replace_title.setStyleSheet("color: #111827; font-size: 11pt;")
        replace_desc = QLabel(f"Clear existing data and load new file<br><span style='color: #6B7280;'>-> Results in {self.new_count:,} students</span>")
        replace_desc.setStyleSheet("color: #374151;")
        replace_layout.addWidget(replace_title)
        replace_layout.addWidget(replace_desc)
        
        replace_widget = QWidget()
        replace_widget_layout = QHBoxLayout(replace_widget)
        replace_widget_layout.setContentsMargins(0, 0, 0, 0)
        replace_widget_layout.addWidget(self.replace_radio)
        replace_widget_layout.addLayout(replace_layout)
        replace_widget_layout.addStretch()
        
        replace_container = QWidget()
        replace_container.setStyleSheet("""
            QWidget {
                background-color: #F3F4F6;
                border: 2px solid #D1D5DB;
                border-radius: 8px;
                padding: 12px;
            }
            QWidget:hover {
                background-color: #E5E7EB;
            }
        """)
        replace_container_layout = QVBoxLayout(replace_container)
        replace_container_layout.setContentsMargins(12, 12, 12, 12)
        replace_container_layout.addWidget(replace_widget)
        layout.addWidget(replace_container)
        
        # Option 3: New Tab
        self.new_tab_radio = QRadioButton()
        newtab_layout = QVBoxLayout()
        newtab_title = QLabel("<b>ADD AS NEW TAB</b> - Keep both")
        newtab_title.setStyleSheet("color: #111827; font-size: 11pt;")
        newtab_desc = QLabel("Keep both datasets in separate tabs<br><span style='color: #6B7280;'>-> Compare datasets side-by-side</span>")
        newtab_desc.setStyleSheet("color: #374151;")
        newtab_layout.addWidget(newtab_title)
        newtab_layout.addWidget(newtab_desc)
        
        newtab_widget = QWidget()
        newtab_widget_layout = QHBoxLayout(newtab_widget)
        newtab_widget_layout.setContentsMargins(0, 0, 0, 0)
        newtab_widget_layout.addWidget(self.new_tab_radio)
        newtab_widget_layout.addLayout(newtab_layout)
        newtab_widget_layout.addStretch()
        
        newtab_container = QWidget()
        newtab_container.setStyleSheet("""
            QWidget {
                background-color: #F3F4F6;
                border: 2px solid #D1D5DB;
                border-radius: 8px;
                padding: 12px;
            }
            QWidget:hover {
                background-color: #E5E7EB;
            }
        """)
        newtab_container_layout = QVBoxLayout(newtab_container)
        newtab_container_layout.setContentsMargins(12, 12, 12, 12)
        newtab_container_layout.addWidget(newtab_widget)
        layout.addWidget(newtab_container)
        
        layout.addSpacing(8)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _on_accept(self):
        """Handle OK button."""
        if self.merge_radio.isChecked():
            self.result_action = 'merge'
        elif self.replace_radio.isChecked():
            self.result_action = 'replace'
        elif self.new_tab_radio.isChecked():
            self.result_action = 'new_tab'
        self.accept()
    
    def get_action(self) -> Optional[str]:
        """Get the selected action."""
        return self.result_action


class MainWindow(QMainWindow):
    """Main application window with full design document implementation."""

    def __init__(self):
        import logging
        self.logger = logging.getLogger('StudentManager.MainWindow')
        self.logger.info("Initializing MainWindow...")

        try:
            super().__init__()

            self.logger.debug("Setting window properties...")
            self.setWindowTitle("Student Admissions Manager")
            self.resize(1600, 1000)
            logo_icon_path = AppTheme.asset_path("logo.png")
            if os.path.exists(logo_icon_path):
                self.setWindowIcon(QIcon(logo_icon_path))

            # Data
            self.logger.debug("Initializing data structures...")
            self.df = pd.DataFrame()
            self.current_file_path = None
            self.child_windows = []
            self._extra_models: List[DataFrameModel] = []
            self._filtered_tab_show_matches = True

            # Setup
            self.logger.info("Setting up models...")
            self._setup_models()

            self.logger.info("Setting up UI...")
            self._setup_ui()

            self.logger.info("Setting up menus...")
            self._setup_menus()

            self.logger.info("Setting up connections...")
            self._setup_connections()

            self.logger.info("Setting up observers...")
            self._setup_observers()

            self.logger.info("Setting up drag & drop...")
            self._setup_drag_drop()

            # Apply theme
            self.logger.debug("Applying stylesheet...")
            self.setStyleSheet(AppTheme.get_stylesheet())

            # Load state
            self.logger.info("Loading saved state...")
            self._load_saved_state()

            # Auto-load last file
            self.logger.debug("Scheduling auto-load...")
            QTimer.singleShot(100, self._autoload_last_file)

            # Initial state
            self.logger.info("Updating initial UI state...")
            self._update_ui_state()

            self.logger.info("MainWindow initialization complete!")

        except Exception as e:
            self.logger.critical(f"FATAL: Error during MainWindow.__init__: {e}", exc_info=True)
            raise
    
    def _setup_models(self):
        """Initialize data models with reactive architecture."""
        self.model = DataFrameModel(self.df)
    
    def _setup_observers(self):
        """Setup reactive observers for auto-updates."""
        # Observe data changes
        self.model.add_observer(self._on_data_changed)
    
    def _on_data_changed(self, event: str, data: dict):
        """React to data changes - Observer callback."""
        if event == 'data_loaded':
            self._sync_active_tab_context()
            self._apply_pending_filters()
            self._rebuild_all_rule_tabs()
            self._refresh_rule_state()
    
    def _setup_ui(self):
        """Setup the modern UI layout - streamlined and professional."""
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === MODERN COMPACT HEADER ===
        self.header = CompactHeader()
        main_layout.addWidget(self.header)

        # === CONTENT SPLITTER ===
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setChildrenCollapsible(False)
        content_splitter.setHandleWidth(6)
        self.content_splitter = content_splitter

        # === LEFT: MODERN FILTER PANEL ===
        self.filter_panel = ModernFilterPanel()
        self.filter_panel.setMinimumWidth(260)
        self.filter_panel.setMaximumWidth(16777215)
        self._filter_panel_min_width = 260
        self._filter_panel_max_width = 520
        self._filter_panel_collapsed = False
        self._filter_panel_user_collapsed = False
        self._filter_panel_auto_collapsed = False
        self._filter_panel_sizes = None
        self.filter_panel.setStyleSheet(f"""
            ModernFilterPanel {{
                background-color: {AppTheme.BACKGROUND};
                border-right: 1px solid {AppTheme.GRAY_200};
            }}
        """)
        content_splitter.addWidget(self.filter_panel)
        self.filter_panel.widthSuggested.connect(self._on_filter_panel_width_suggested)

        # === CENTER: MAIN CONTENT ===
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)

        # === MODERN ACTION BAR ===
        self.action_bar = ModernActionBar()
        content_layout.addWidget(self.action_bar)

        # === MODERN SEARCH BAR ===
        self.search_bar = ModernSearchBar()
        content_layout.addWidget(self.search_bar)

        # === TAB WIDGET - Clean and subtle ===
        self.tab_widget = DynamicTabWidget()
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {AppTheme.GRAY_200};
                background-color: {AppTheme.BACKGROUND};
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background-color: {AppTheme.GRAY_100};
                color: {AppTheme.TEXT_SECONDARY};
                border: 1px solid {AppTheme.GRAY_300};
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 7px 14px;
                margin-right: 2px;
                font-weight: 600;
                font-size: 9pt;
                min-width: 100px;
            }}
            QTabBar::tab:selected {{
                background-color: {AppTheme.BACKGROUND};
                color: {AppTheme.PRIMARY};
                font-weight: 700;
                border: 1px solid {AppTheme.GRAY_300};
                border-top: 2px solid {AppTheme.PRIMARY};
                border-bottom: 1px solid {AppTheme.BACKGROUND};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {AppTheme.PRIMARY_LIGHT};
                color: {AppTheme.TEXT};
            }}
        """)
        # Create "All Students" base tab (always present)
        
        # Create "All Students" base tab (always present)
        self.table_all = StyledTableView()
        self.proxy_all = SmartSearchProxy()
        self.proxy_all.setSourceModel(self.model)
        self.proxy_all.setFilterMode("all")
        self.table_all.setModel(self.proxy_all)
        self.table_all.tab_kind = "base"
        self.table_all.tab_filters = []
        self.table_all.tab_filter_mode = "all"
        self.tab_widget.addTab(self.table_all, "All Students")

        # Make "All Students" tab not closable
        self.tab_widget.tabBar().setTabButton(0, self.tab_widget.tabBar().RightSide, None)

        content_layout.addWidget(self.tab_widget, 1)

        # Enhanced Column Navigator (compact slider)
        self.column_navigator = EnhancedColumnNavigator()
        self.column_navigator.setMaximumHeight(90)
        content_layout.addWidget(self.column_navigator)

        content_splitter.addWidget(content_widget)
        content_splitter.setStretchFactor(1, 1)
        content_splitter.setSizes([280, 1320])
        
        main_layout.addWidget(content_splitter, 1)
        
        # Status bar (messages only)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # === COMPATIBILITY: Create aliases for old UI components ===
        # Old code expects self.search_edit and self.search_column_combo
        # Redirect to modern search bar components
        self.search_edit = self.search_bar.search_input
        self.search_column_combo = self.search_bar.column_combo

    def _setup_menus(self):
        """Setup menu bar."""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("File")
        
        load_action = QAction("Load File...", self)
        load_action.setShortcut(QKeySequence.Open)
        load_action.triggered.connect(self._on_load_file)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("Save Current View...", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self._on_save_current)
        file_menu.addAction(save_action)
        
        export_menu = file_menu.addMenu("Export")
        
        export_all = QAction("Export All Data...", self)
        export_all.triggered.connect(lambda: self._on_export(mode="all"))
        export_menu.addAction(export_all)
        
        export_filtered = QAction("Export Current Tab...", self)
        export_filtered.triggered.connect(lambda: self._on_export(mode="current_tab"))
        export_menu.addAction(export_filtered)
        
        export_highlighted = QAction("Export Filtered Only...", self)
        export_highlighted.triggered.connect(lambda: self._on_export(mode="highlighted"))
        export_menu.addAction(export_highlighted)
        
        file_menu.addSeparator()
        
        browse_archives = QAction("Browse Archives...", self)
        browse_archives.triggered.connect(self._on_browse_archives)
        file_menu.addAction(browse_archives)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Rules Menu
        filters_menu = menubar.addMenu("Rules")
        
        add_filter_action = QAction("Add Filter...", self)
        add_filter_action.setShortcut("Ctrl+F")
        add_filter_action.triggered.connect(self._on_add_filter)
        filters_menu.addAction(add_filter_action)
        self.add_filter_action = add_filter_action
        
        filters_menu.addSeparator()
        
        clear_filters_action = QAction("Clear All Filters", self)
        clear_filters_action.setShortcut("Ctrl+Shift+F")
        clear_filters_action.triggered.connect(self._on_clear_all_filters)
        filters_menu.addAction(clear_filters_action)
        self.clear_filters_action = clear_filters_action
        
        filters_menu.addSeparator()
        
        save_preset_action = QAction("Save Filter Preset...", self)
        save_preset_action.triggered.connect(self._on_save_preset)
        filters_menu.addAction(save_preset_action)
        self.save_preset_action = save_preset_action
        
        load_preset_action = QAction("Load Filter Preset...", self)
        load_preset_action.triggered.connect(self._on_load_preset)
        filters_menu.addAction(load_preset_action)
        self.load_preset_action = load_preset_action

        if hasattr(self, "filters_menu") and self.filters_menu is not None:
            self.filters_menu.clear()
            self.filters_menu.addAction(self.add_filter_action)
            self.filters_menu.addAction(self.clear_filters_action)
            self.filters_menu.addSeparator()
            self.filters_menu.addAction(self.save_preset_action)
            self.filters_menu.addAction(self.load_preset_action)
        
        # Tabs Menu (NEW)
        tabs_menu = menubar.addMenu("Tabs")
        
        new_tab_action = QAction("New Custom Tab...", self)
        new_tab_action.setShortcut("Ctrl+T")
        new_tab_action.triggered.connect(self._on_new_custom_tab)
        tabs_menu.addAction(new_tab_action)
        
        tabs_menu.addSeparator()
        
        close_tab_action = QAction("Close Current Tab", self)
        close_tab_action.setShortcut("Ctrl+W")
        close_tab_action.triggered.connect(self._on_close_current_tab)
        tabs_menu.addAction(close_tab_action)
        
        close_all_tabs_action = QAction("Close All Rule Tabs", self)
        close_all_tabs_action.triggered.connect(self._close_all_filter_tabs)
        tabs_menu.addAction(close_all_tabs_action)

        tabs_menu.addSeparator()

        filtered_mode_action = QAction("Filtered Tab Shows Matching Rows", self)
        filtered_mode_action.setCheckable(True)
        filtered_mode_action.setChecked(getattr(self, "_filtered_tab_show_matches", True))
        filtered_mode_action.toggled.connect(self._on_filtered_tab_mode_toggled)
        tabs_menu.addAction(filtered_mode_action)
        self.filtered_tab_mode_action = filtered_mode_action
        
        # Tools Menu
        tools_menu = menubar.addMenu("Tools")
        
        move_highlighted = QAction("Move Filtered to New Window", self)
        move_highlighted.triggered.connect(self._on_move_highlighted)
        tools_menu.addAction(move_highlighted)
        
        copy_highlighted = QAction("Copy Filtered to New Window", self)
        copy_highlighted.triggered.connect(self._on_copy_highlighted)
        tools_menu.addAction(copy_highlighted)
        
        # Help Menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
        
        shortcuts_action = QAction("Keyboard Shortcuts", self)
        shortcuts_action.triggered.connect(self._on_shortcuts)
        help_menu.addAction(shortcuts_action)
    
    def _setup_connections(self):
        """Connect signals and slots for modern UI."""
        # === MODERN ACTION BAR ===
        self.action_bar.loadRequested.connect(self._on_load_file)
        self.action_bar.saveRequested.connect(self._on_save_current)
        self.action_bar.exportRequested.connect(self._on_export_mode)
        self.action_bar.archivesRequested.connect(self._on_browse_archives)
        self.action_bar.newTabRequested.connect(self._on_new_custom_tab)
        self.action_bar.shortcutsRequested.connect(self._on_shortcuts)

        # === MODERN SEARCH BAR ===
        self.search_bar.searchChanged.connect(self._on_modern_search_changed)

        # === MODERN FILTER PANEL ===
        self.filter_panel.filterAdded.connect(self._on_filter_added)
        self.filter_panel.filterRemoved.connect(self._on_filter_removed)
        self.filter_panel.filterEdited.connect(self._on_filter_edited)
        self.filter_panel.allFiltersCleared.connect(self._on_clear_all_filters)
        self.filter_panel.filterModeChanged.connect(self._on_filter_mode_changed)
        self.filter_panel.ruleTabRequested.connect(self._on_open_rule_tab)
        self.filter_panel.collapseToggled.connect(self._on_filter_panel_collapse_toggled)
        self.filter_panel.add_btn.clicked.connect(self._on_add_filter)

        # === TABLE VIEW ===
        self._wire_table_view(self.table_all, allow_filters=True)

        # === COLUMN NAVIGATOR ===
        self.column_navigator.columnSelected.connect(self._on_column_selected)

        # === TAB WIDGET ===
        self.tab_widget.tabRenamed.connect(self._on_tab_renamed)
        self.tab_widget.tabClosed.connect(self._on_tab_closed_signal)
        self.tab_widget.duplicateTabRequested.connect(self._on_duplicate_tab)
        self.tab_widget.exportTabRequested.connect(self._on_export_tab)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.tab_widget.tabBar().tabMoved.connect(lambda _from, _to: self._save_state())
    
    def _setup_drag_drop(self):
        """Enable drag and drop."""
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                filepath = url.toLocalFile()
                if filepath.lower().endswith(('.xlsx', '.xls', '.csv', '.tsv', '.json')):
                    event.acceptProposedAction()
                    return
        event.ignore()
    
    def dropEvent(self, event):
        """Handle drop event."""
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            if filepath.lower().endswith(('.xlsx', '.xls', '.csv', '.tsv', '.json')):
                self.load_file(filepath)
                break
    
    def load_file(self, filepath: str, sheet_name: Optional[str] = None):
        """Load a data file with smart merge handling."""
        try:
            new_df, needs_sheet, sheets = load_dataframe_from_file(filepath, sheet_name)
            
            if needs_sheet:
                sheet, ok = QInputDialog.getItem(
                    self,
                    "Select Sheet",
                    "This file has multiple sheets. Choose one to load:",
                    sheets,
                    0,
                    False
                )
                if not ok:
                    return
                self.load_file(filepath, sheet)
                return
            
            new_df = add_date_column(new_df)
            
            # Check if data already exists
            if not self.df.empty:
                dialog = MergeDialog(len(self.df), len(new_df), filepath, self)
                
                if dialog.exec_() != QDialog.Accepted:
                    return
                
                action = dialog.get_action()
                
                if action == 'merge':
                    merged, success, message = merge_dataframes(self.df, new_df)
                    
                    if not success:
                        QMessageBox.warning(self, "Column Mismatch", message)
                        return
                    
                    self.df = merged
                    self.model.set_dataframe(self.df)
                    self.current_file_path = filepath
                    self.status_bar.showMessage(f"Merged {len(new_df)} new records", 5000)
                
                elif action == 'replace':
                    self.df = new_df
                    self.model.set_dataframe(self.df)
                    self.current_file_path = filepath
                    self.status_bar.showMessage(f"Replaced with {len(new_df)} records", 5000)
                
                elif action == 'new_tab':
                    tab_name = os.path.basename(filepath)
                    self._create_file_tab(new_df, filepath, tab_name=tab_name)
                    self.status_bar.showMessage(f"Added {len(new_df)} records in new tab", 5000)
                    self._save_state()
                    return
            
            else:
                self.df = new_df
                self.current_file_path = filepath
                self.model.set_dataframe(self.df)
            
            # Save as last file
            save_last_loaded_file(filepath)
            
            # Create archive
            archive_path = create_archive_snapshot(self.df, self.model.filter_manager)
            
            filename = os.path.basename(filepath)
            self.status_bar.showMessage(f"Loaded {filename} - Archive: {os.path.basename(archive_path)}", 5000)
            self._save_state()
            
        except Exception as e:
            QMessageBox.critical(self, "Error Loading File", f"Failed to load file:\n\n{str(e)}")
    
    def _on_load_file(self):
        """Handle load file action."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open Data File",
            "",
            "Data Files (*.xlsx *.xls *.csv *.tsv *.json);;Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;TSV Files (*.tsv);;JSON Files (*.json)"
        )
        
        if filepath:
            self.load_file(filepath)
    
    def _on_save_current(self):
        """Save current view to file."""
        current_proxy = self._get_current_proxy()
        if current_proxy is None:
            QMessageBox.information(self, "No Data", "No data to save.")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Data",
            "data.xlsx",
            "Excel Files (*.xlsx);;CSV Files (*.csv);;TSV Files (*.tsv);;JSON Files (*.json)"
        )
        
        if filepath:
            try:
                export_df = self._dataframe_for_proxy(current_proxy)
                
                if filepath.endswith('.csv'):
                    export_df.to_csv(filepath, index=False)
                elif filepath.endswith('.tsv'):
                    export_df.to_csv(filepath, sep='\t', index=False)
                elif filepath.endswith('.json'):
                    export_df.to_json(filepath, orient='records')
                else:
                    current_widget = self._get_current_tab_widget()
                    filter_manager, filter_mode = self._get_tab_filter_context(current_widget)
                    mask_override = self._export_mask_override_for_proxy(current_proxy)
                    export_to_excel_formatted(
                        export_df,
                        filepath,
                        filter_manager,
                        split_sheets=True,
                        filter_mode=filter_mode,
                        mask_override=mask_override
                    )
                
                self.status_bar.showMessage(f"Saved to {os.path.basename(filepath)}", 3000)
            
            except Exception as e:
                QMessageBox.critical(self, "Error Saving", f"Failed to save file:\n\n{str(e)}")
    
    def _on_export(self, mode: str):
        """Export data based on mode."""
        current_proxy = self._get_current_proxy()
        if current_proxy is None:
            QMessageBox.information(self, "No Data", "No data to export.")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data",
            f"export_{mode}.xlsx",
            "Excel Files (*.xlsx);;CSV Files (*.csv);;TSV Files (*.tsv);;JSON Files (*.json)"
        )
        
        if not filepath:
            return
        
        try:
            if mode == "all":
                export_df = self._dataframe_for_proxy(current_proxy, full_source=True)
            elif mode == "current_tab":
                export_df = self._dataframe_for_proxy(current_proxy)
            elif mode == "highlighted":
                mask = self._compute_highlight_mask()
                current_model = self._get_current_model() or self.model
                df = current_model.dataframe() if current_model is not None else self.df
                export_df = df[mask]
            else:
                return
            
            if filepath.endswith('.csv'):
                export_df.to_csv(filepath, index=False)
            elif filepath.endswith('.tsv'):
                export_df.to_csv(filepath, sep='\t', index=False)
            elif filepath.endswith('.json'):
                export_df.to_json(filepath, orient='records')
            else:
                current_widget = self._get_current_tab_widget()
                filter_manager, filter_mode = self._get_tab_filter_context(current_widget)
                mask_override = self._export_mask_override_for_proxy(current_proxy)
                export_to_excel_formatted(
                    export_df,
                    filepath,
                    filter_manager,
                    split_sheets=False,
                    filter_mode=filter_mode,
                    mask_override=mask_override
                )
            
            self.status_bar.showMessage(f"Exported to {os.path.basename(filepath)}", 3000)
        
        except Exception as e:
            QMessageBox.critical(self, "Error Exporting", f"Failed to export:\n\n{str(e)}")
    
    def _on_browse_archives(self):
        """Open archive browser."""
        archives = get_archive_list()
        
        if not archives:
            QMessageBox.information(self, "No Archives", "No archive files found.")
            return
        
        browser = ArchiveBrowserDialog(archives, self)
        browser.archiveSelected.connect(self._on_archive_selected)
        browser.show()
    
    def _on_archive_selected(self, filepath: str):
        """Load selected archive."""
        try:
            df = pd.read_excel(filepath, sheet_name="ALL")
            
            self.df = df
            self.model.set_dataframe(self.df)
            self.current_file_path = filepath
            
            self.status_bar.showMessage(f"Loaded archive: {os.path.basename(filepath)}", 5000)
            self._save_state()
        
        except Exception as e:
            QMessageBox.critical(self, "Error Loading Archive", f"Failed to load archive:\n\n{str(e)}")
    
    def _on_add_filter(self):
        """Open dialog to add a new filter."""
        current_model = self._get_current_model() or self.model
        if current_model is None or current_model.rowCount() == 0:
            QMessageBox.information(self, "No Data", "Load data first before adding filters.")
            return

        dialog = FilterDialog(current_model.dataframe(), parent=self)

        if dialog.exec_():
            filter_rule = dialog.get_filter()
            if not filter_rule:
                return

            current_widget = self._get_current_tab_widget()
            if current_widget is None:
                return

            if getattr(current_widget, "tab_kind", None) == "base":
                self._create_filter_tab(
                    [filter_rule],
                    filter_mode=self.filter_panel.get_filter_mode(),
                    switch_to=False
                )
                self._refresh_rule_state()
                self._sync_filter_panel_for_tab(self._get_current_tab_widget())
            else:
                self._add_filter_to_tab(current_widget, filter_rule)
    
    def _on_add_filter_for_column(self, column_name: str):
        """Open dialog to add filter for specific column."""
        current_model = self._get_current_model() or self.model
        if current_model is None or current_model.rowCount() == 0:
            return

        dialog = FilterDialog(current_model.dataframe(), parent=self)
        
        idx = dialog.column_combo.findText(column_name)
        if idx >= 0:
            dialog.column_combo.setCurrentIndex(idx)
        
        if dialog.exec_():
            filter_rule = dialog.get_filter()
            if not filter_rule:
                return

            current_widget = self._get_current_tab_widget()
            if current_widget is None:
                return

            if getattr(current_widget, "tab_kind", None) == "base":
                self._create_filter_tab(
                    [filter_rule],
                    filter_mode=self.filter_panel.get_filter_mode(),
                    switch_to=False
                )
                self._refresh_rule_state()
                self._sync_filter_panel_for_tab(self._get_current_tab_widget())
            else:
                self._add_filter_to_tab(current_widget, filter_rule)

    def _on_clear_filters_for_column(self, column_name: str):
        """Remove all filters for a column in the active context."""
        if not column_name:
            return

        current_widget = self._get_current_tab_widget()
        if current_widget is None:
            return

        removed_count = 0
        tab_kind = getattr(current_widget, "tab_kind", None)

        if tab_kind in ["base", "filtered"]:
            # On the main/filtered views, column filters are defined by rule tabs.
            for _, rule_widget in list(self._iter_rule_tabs()):
                filters, _ = self._ensure_tab_filter_state(rule_widget)
                matching = [f for f in list(filters) if getattr(f, "column", None) == column_name]
                for filter_rule in matching:
                    self._remove_filter_from_tab(rule_widget, filter_rule)
                    removed_count += 1

            # Keep behavior consistent if base tab has direct filters.
            base_filters, _ = self._ensure_tab_filter_state(self.table_all)
            base_matching = [f for f in list(base_filters) if getattr(f, "column", None) == column_name]
            for filter_rule in base_matching:
                self._remove_filter_from_tab(self.table_all, filter_rule)
                removed_count += 1
        else:
            filters, _ = self._ensure_tab_filter_state(current_widget)
            matching = [f for f in list(filters) if getattr(f, "column", None) == column_name]
            for filter_rule in matching:
                self._remove_filter_from_tab(current_widget, filter_rule)
                removed_count += 1

        if removed_count == 0:
            QMessageBox.information(self, "No Filters", f"No filters found for column '{column_name}'.")
            return

        plural = "s" if removed_count != 1 else ""
        self.status_bar.showMessage(f"Removed {removed_count} filter{plural} from '{column_name}'", 3000)
    
    def _on_filter_added(self, filter_rule):
        """Handle filter added signal from panel."""
        current_widget = self._get_current_tab_widget()
        if current_widget is None:
            return
        # NEW BEHAVIOR: Don't auto-create tabs, apply to current tab instead
        self._add_filter_to_tab(current_widget, filter_rule)
    
    def _on_filter_removed(self, filter_rule):
        """Handle filter removed signal from panel."""
        current_widget = self._get_current_tab_widget()
        if current_widget is None:
            return
        if getattr(current_widget, "tab_kind", None) == "base":
            rule_widget = self._find_rule_tab_for_filter(filter_rule)
            if rule_widget is not None:
                self._remove_filter_from_tab(rule_widget, filter_rule)
                self._sync_filter_panel_for_tab(current_widget)
                return
        self._remove_filter_from_tab(current_widget, filter_rule)

    def _on_filter_edited(self, filter_rule, _new_filter):
        """Edit an existing filter."""
        current_model = self._get_current_model() or self.model
        if current_model is None or current_model.rowCount() == 0:
            return

        dialog = FilterDialog(current_model.dataframe(), existing_filter=filter_rule, parent=self)

        if dialog.exec_():
            new_filter = dialog.get_filter()
            if new_filter and new_filter != filter_rule:
                current_widget = self._get_current_tab_widget()
                if current_widget is None:
                    return
                target_widget = current_widget
                if getattr(current_widget, "tab_kind", None) == "base":
                    rule_widget = self._find_rule_tab_for_filter(filter_rule)
                    if rule_widget is not None:
                        target_widget = rule_widget

                filters, mode = self._ensure_tab_filter_state(target_widget)
                for i, existing in enumerate(filters):
                    if existing == filter_rule:
                        filters[i] = new_filter
                        break
                target_widget.tab_filters = filters
                if getattr(target_widget, "tab_kind", None) == "rule":
                    self._rebuild_rule_tab(target_widget)
                    self._refresh_rule_state()
                else:
                    self._apply_tab_filters(target_widget)
                self._sync_filter_panel_for_tab(current_widget)
                self._update_column_navigator()
                self._update_ui_state()
                self._save_state()
    
    def _on_clear_all_filters(self):
        """Clear all active filters."""
        current_widget = self._get_current_tab_widget()
        if current_widget is None:
            return
        if getattr(current_widget, "tab_kind", None) == "base":
            self._close_all_filter_tabs()
            return
        self._clear_filters_for_tab(current_widget)

    def _on_open_rule_tab(self, filter_rule):
        """Open a dedicated tab for a specific filter rule (right-click menu)."""
        if filter_rule is None:
            return
        # Show existing preview tab or create it if missing
        existing_widget = self._find_rule_tab_for_filter(filter_rule)
        if existing_widget is not None:
            self._show_rule_tab(existing_widget)
            return
        self._create_filter_tab([filter_rule], filter_mode="all", switch_to=True)

    def _create_filter_tab(self, filter_rules, insert_index: Optional[int] = None,
                           tab_name: Optional[str] = None, filter_mode: str = "all",
                           switch_to: bool = True, save_state: bool = True,
                           refresh_rules: bool = True):
        """Create a new tab for one or more filters."""
        if not filter_rules:
            return None
        if not isinstance(filter_rules, list):
            filter_rules = [filter_rules]
        primary_rule = filter_rules[0]

        # Create table view
        table_view = StyledTableView()
        
        # Create snapshot for this rule
        base_df = self.model.dataframe()
        mask = self._build_mask_for_filters(base_df, filter_rules, filter_mode)
        snapshot_df = base_df[mask].copy() if not base_df.empty else base_df.copy()

        # Create proxy for snapshot model
        proxy = SmartSearchProxy()
        proxy.setSourceModel(DataFrameModel(snapshot_df))
        proxy.setExtraFilters([])
        proxy.setExtraFilterMode("all")
        proxy.setFilterMode("all")
        
        # Apply current search
        proxy.setSearchText(self.search_edit.text())
        search_col = self.search_column_combo.currentText()
        if search_col != "Global" and self._model_has_column(proxy.sourceModel(), search_col):
            proxy.setSearchColumn(search_col)
        else:
            proxy.setSearchColumn(None)
        
        table_view.setModel(proxy)
        self._wire_table_view(table_view, allow_filters=True)
        table_view.tab_filters = list(filter_rules)
        table_view.tab_filter_mode = filter_mode
        table_view.tab_kind = "rule"
        
        # Add tab
        index = self.tab_widget.add_filter_tab(
            primary_rule,
            table_view,
            insert_index=insert_index,
            tab_name=tab_name,
            switch_to=switch_to
        )
        if switch_to:
            self._show_rule_tab(table_view)
            self._sync_filter_panel_for_tab(table_view)
        else:
            self._hide_rule_tab(table_view)
        self._update_column_navigator()
        self._update_ui_state()
        if refresh_rules:
            self._refresh_rule_state()
        if save_state:
            self._save_state()
        return index
    
    def _close_all_filter_tabs(self):
        """Close all rule tabs except 'All Students'."""
        # Remove only rule tabs, keep base and custom/file tabs.
        for i in range(self.tab_widget.count() - 1, 0, -1):
            widget = self.tab_widget.widget(i)
            if getattr(widget, "tab_kind", None) == "rule":
                self.tab_widget.removeTab(i)
                widget.deleteLater()
        self._sync_active_tab_context()
        self._refresh_rule_state()
        self._save_state()
    
    def _on_tab_closed_signal(self, index):
        """Handle tab close signal."""
        if index == 0:
            return

        widget = self.tab_widget.widget(index)
        tab_kind = getattr(widget, "tab_kind", None)

        if tab_kind == "filtered":
            return
        if tab_kind == "rule":
            if widget:
                self._hide_rule_tab(widget)
            self._save_state()
        else:
            # Custom/file snapshot tabs use independent models; drop references on close.
            proxy = widget.model() if widget else None
            source_model = proxy.sourceModel() if proxy and hasattr(proxy, "sourceModel") else None
            if source_model in self._extra_models:
                self._extra_models.remove(source_model)
            self.tab_widget.removeTab(index)
            if widget:
                widget.deleteLater()
            self._save_state()
    
    def _on_tab_renamed(self, index, new_name):
        """Handle tab rename."""
        self._save_state()

    def _on_duplicate_tab(self, index):
        """Duplicate a tab as an independent snapshot (rule highlights still apply)."""
        proxy = self._get_tab_proxy(index)
        if proxy is None:
            return

        current_name = self._strip_tab_count(self.tab_widget.tabText(index))
        new_name = f"{current_name} Copy"

        new_index = self._create_custom_tab(new_name, source_proxy=proxy)
        if new_index is not None:
            self.tab_widget.setCurrentIndex(new_index)
            self.status_bar.showMessage("Created independent snapshot copy", 3000)
            self._save_state()

    def _on_export_tab(self, index):
        """Export data for a specific tab."""
        if index < 0 or index >= self.tab_widget.count():
            return
        self.tab_widget.setCurrentIndex(index)
        self._on_export(mode="current_tab")
    
    def _on_new_custom_tab(self):
        """Create a new independent snapshot tab."""
        dialog = NewTabDialog(self)
        if dialog.exec_():
            name = dialog.get_tab_name()
            if name:
                index = self._create_custom_tab(name)
                if index is not None:
                    self.tab_widget.setCurrentIndex(index)
                    self.status_bar.showMessage("Created independent snapshot tab", 3000)
                    self._save_state()
    
    def _on_close_current_tab(self):
        """Close current tab."""
        current_idx = self.tab_widget.currentIndex()
        if current_idx > 0:  # Can't close "All Students"
            self._on_tab_closed_signal(current_idx)
    
    def _on_save_preset(self):
        """Save current filters as a preset."""
        current_widget = self._get_current_tab_widget()
        if current_widget is None:
            return
        filters, _ = self._ensure_tab_filter_state(current_widget)
        if not filters:
            QMessageBox.information(self, "No Filters", "Add some filters before saving a preset.")
            return
        
        dialog = SavePresetDialog(filters, self)
        dialog.exec_()
    
    def _on_load_preset(self):
        """Load a filter preset."""
        dialog = LoadPresetDialog(self)
        
        def on_preset_selected(preset):
            current_widget = self._get_current_tab_widget()
            if current_widget is None:
                return

            if getattr(current_widget, "tab_kind", None) == "base":
                self._create_filter_tab(
                    list(preset.filters),
                    tab_name=preset.name,
                    filter_mode="all",
                    switch_to=False
                )
            else:
                self._clear_filters_for_tab(current_widget)
                for filter_rule in preset.filters:
                    self._add_filter_to_tab(current_widget, filter_rule)

            QMessageBox.information(self, "Preset Loaded", f"Loaded preset '{preset.name}' with {len(preset.filters)} filters.")
        
        dialog.presetSelected.connect(on_preset_selected)
        dialog.exec_()
    
    def _on_search_text_changed(self, text):
        """Handle search text changes (legacy)."""
        self._apply_search_to_all_tabs()

    def _on_search_column_changed(self, text):
        """Handle search column changes (legacy)."""
        self._apply_search_to_all_tabs()

    def _on_modern_search_changed(self, text: str, column: str):
        """Handle modern search bar changes."""
        # Apply to all tab proxies
        for index, widget, proxy in self._iter_tab_proxies():
            if isinstance(proxy, SmartSearchProxy):
                if column == "Global":
                    proxy.setGlobalSearchTerm(text)
                else:
                    proxy.setColumnSearchTerm(column, text)
        self._update_ui_state()

    def _on_export_mode(self, mode: str):
        """Handle export mode from modern action bar."""
        if mode == "all":
            self._on_export(mode="all")
        elif mode == "current":
            self._on_export(mode="current_tab")
        elif mode == "filtered":
            self._on_export(mode="highlighted")

    def _on_quick_filter(self, column: str, operator: str, value):
        """Handle quick filter button click - instant 1-click filtering."""
        from models import NumericFilter, TextFilter

        # Create appropriate filter
        if operator == "range":
            # value is tuple (min, max)
            filter_rule = NumericFilter(column, ">=", value[0])
            # For now, just use >=, we'd need compound filter support for full range
        elif operator in [">=", "<=", "<", ">", "=="]:
            filter_rule = NumericFilter(column, operator, value)
        elif operator == "contains":
            filter_rule = TextFilter(column, [value])
        else:
            return

        # Add filter to current tab
        current_widget = self._get_current_tab_widget()
        if current_widget:
            self._add_filter_to_tab(current_widget, filter_rule)
            # Also add to filter panel display
            self.filter_panel.add_filter(filter_rule)

        self.status_bar.showMessage(f"Quick filter applied: {filter_rule}", 3000)

    def _on_filter_mode_changed(self, mode):
        """Handle per-tab filter mode (AND/OR) changes."""
        current_widget = self._get_current_tab_widget()
        if current_widget is None:
            return
        self._set_tab_filter_mode(current_widget, mode)
    
    def _on_edit_cell(self, proxy_index):
        """Handle cell edit request."""
        old_value = proxy_index.data(Qt.DisplayRole)
        
        new_value, ok = QInputDialog.getText(
            self,
            "Edit Cell",
            "Enter new value:",
            text=str(old_value) if old_value is not None else ""
        )
        
        if ok:
            proxy_model = proxy_index.model()
            source_index = proxy_model.mapToSource(proxy_index)
            source_model = proxy_model.sourceModel() if hasattr(proxy_model, "sourceModel") else self.model
            source_model.setData(source_index, new_value, role=Qt.EditRole)
            self._refresh_all_views()
            self.status_bar.showMessage("Cell updated", 2000)
    
    def _on_column_selected(self, col_idx):
        """Handle column selection from navigator."""
        current_idx = self.tab_widget.currentIndex()
        widget = self.tab_widget.widget(current_idx)
        if isinstance(widget, StyledTableView):
            table = widget
        else:
            table = widget.findChild(StyledTableView) if widget else None
            if not table:
                return
        
        table.scrollTo(
            table.model().index(0, col_idx),
            QAbstractItemView.PositionAtCenter
        )
        table.selectColumn(col_idx)
    
    def _on_tab_changed(self, index):
        """Handle tab change."""
        self._sync_active_tab_context()
    
    def _on_move_highlighted(self):
        """Move highlighted rows to new window."""
        current_proxy = self._get_current_proxy()
        if not self._proxy_is_main_model(current_proxy):
            QMessageBox.information(self, "Not Available", "This action is only available for the main dataset.")
            return
        mask = self._compute_highlight_mask()
        
        if not mask.any():
            QMessageBox.information(self, "No Filtered Rows", "No filtered rows to move.")
            return
        
        highlighted_df = self.df[mask].copy()
        remaining_df = self.df[~mask].copy()
        
        self.df = remaining_df
        self.model.set_dataframe(self.df)
        
        window = SecondaryTableWindow(highlighted_df, "Filtered Rows (Moved)", self)
        self.child_windows.append(window)
        window.show()
        
        self.status_bar.showMessage(f"Moved {len(highlighted_df)} rows to new window", 3000)
    
    def _on_copy_highlighted(self):
        """Copy highlighted rows to new window."""
        current_proxy = self._get_current_proxy()
        if not self._proxy_is_main_model(current_proxy):
            QMessageBox.information(self, "Not Available", "This action is only available for the main dataset.")
            return
        mask = self._compute_highlight_mask()
        
        if not mask.any():
            QMessageBox.information(self, "No Filtered Rows", "No filtered rows to copy.")
            return
        
        highlighted_df = self.df[mask].copy()
        
        window = SecondaryTableWindow(highlighted_df, "Filtered Rows (Copy)", self)
        self.child_windows.append(window)
        window.show()
        
        self.status_bar.showMessage(f"Copied {len(highlighted_df)} rows to new window", 3000)
    
    def _on_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Student Admissions Manager",
            "<h3>Student Admissions Manager v2.0</h3>"
            "<p><b>Professional-Grade Admissions Management</b></p>"
            "<p>Built with PyQt5 and pandas</p>"
            "<br>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Reactive observer-pattern architecture</li>"
            "<li>Rule-based tabs and highlights</li>"
            "<li>Enhanced column navigation</li>"
            "<li>Smart data merging</li>"
            "<li>Multiple file format support</li>"
            "<li>Filter presets</li>"
            "<li>Automatic archiving</li>"
            "<li>Professional high-contrast UI</li>"
            "</ul>"
        )
    
    def _on_shortcuts(self):
        """Show keyboard shortcuts."""
        shortcuts = """
        <h3>Keyboard Shortcuts</h3>
        <table style='border-collapse: collapse;'>
            <tr><td style='padding: 4px;'><b>Ctrl+O</b></td><td style='padding: 4px;'>Open file</td></tr>
            <tr><td style='padding: 4px;'><b>Ctrl+S</b></td><td style='padding: 4px;'>Save current view</td></tr>
            <tr><td style='padding: 4px;'><b>Ctrl+F</b></td><td style='padding: 4px;'>Create rule / add filter</td></tr>
            <tr><td style='padding: 4px;'><b>Ctrl+Shift+F</b></td><td style='padding: 4px;'>Clear all filters (or rules on main tab)</td></tr>
            <tr><td style='padding: 4px;'><b>Ctrl+T</b></td><td style='padding: 4px;'>New tab</td></tr>
            <tr><td style='padding: 4px;'><b>Ctrl+W</b></td><td style='padding: 4px;'>Close tab</td></tr>
            <tr><td style='padding: 4px;'><b>Ctrl+Q</b></td><td style='padding: 4px;'>Quit</td></tr>
        </table>
        """
        QMessageBox.information(self, "Keyboard Shortcuts", shortcuts)

    def _iter_tab_proxies(self):
        """Yield (index, widget, proxy) for each tab with a proxy model."""
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if widget is None:
                continue
            proxy = widget.model() if hasattr(widget, "model") else None
            if isinstance(proxy, SmartSearchProxy):
                yield i, widget, proxy

    def _get_tab_proxy(self, index: int) -> Optional[SmartSearchProxy]:
        widget = self.tab_widget.widget(index)
        if widget is None:
            return None
        proxy = widget.model() if hasattr(widget, "model") else None
        return proxy if isinstance(proxy, SmartSearchProxy) else None

    def _get_current_proxy(self) -> Optional[SmartSearchProxy]:
        return self._get_tab_proxy(self.tab_widget.currentIndex())

    def _get_current_model(self) -> Optional[DataFrameModel]:
        proxy = self._get_current_proxy()
        if proxy is None:
            return None
        return proxy.sourceModel() if hasattr(proxy, "sourceModel") else None

    def _get_current_tab_widget(self):
        return self.tab_widget.widget(self.tab_widget.currentIndex())

    def _set_tab_visible(self, index: int, visible: bool):
        tab_bar = self.tab_widget.tabBar()
        if hasattr(tab_bar, "setTabVisible"):
            tab_bar.setTabVisible(index, visible)
        else:
            tab_bar.setTabEnabled(index, visible)

    def _show_rule_tab(self, widget):
        index = self.tab_widget.indexOf(widget)
        if index < 0:
            return
        self._set_tab_visible(index, True)
        self.tab_widget.setCurrentIndex(index)

    def _hide_rule_tab(self, widget):
        index = self.tab_widget.indexOf(widget)
        if index < 0:
            return
        self._set_tab_visible(index, False)
        if self.tab_widget.currentIndex() == index:
            self.tab_widget.setCurrentIndex(0)

    def _iter_rule_tabs(self):
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if getattr(widget, "tab_kind", None) == "rule":
                yield i, widget

    def _get_rule_definitions(self):
        rules = []
        for _, widget in self._iter_rule_tabs():
            filters, mode = self._ensure_tab_filter_state(widget)
            if filters:
                rules.append((filters, mode))
        return rules

    def _find_rule_tab_for_filter(self, filter_rule):
        """Return the rule tab widget that owns the given filter rule."""
        for _, widget in self._iter_rule_tabs():
            filters, _ = self._ensure_tab_filter_state(widget)
            if filter_rule in filters:
                return widget
        return None

    def _get_active_rule_filters(self):
        """Return rule filters whose rule tabs have at least one matching row."""
        active_filters: List[FilterRule] = []
        for _, widget in self._iter_rule_tabs():
            filters, _ = self._ensure_tab_filter_state(widget)
            if not filters:
                continue
            proxy = widget.model() if hasattr(widget, "model") else None
            source_model = proxy.sourceModel() if proxy and hasattr(proxy, "sourceModel") else None
            try:
                row_count = source_model.rowCount() if source_model is not None else 0
            except Exception:
                row_count = 0
            if row_count > 0:
                active_filters.extend(filters)
        return active_filters

    def _row_matches_filters(self, row, filters, mode: str) -> bool:
        if not filters:
            return False

        applicable = []
        for filter_rule in filters:
            col = getattr(filter_rule, "column", None)
            if col is None:
                continue
            if col in row.index:
                applicable.append(filter_rule)

        if not applicable:
            return False

        if mode == "any":
            for filter_rule in applicable:
                col = filter_rule.column
                try:
                    if filter_rule.matches(row[col]):
                        return True
                except Exception:
                    continue
            return False

        # Default AND
        for filter_rule in applicable:
            col = filter_rule.column
            try:
                if not filter_rule.matches(row[col]):
                    return False
            except Exception:
                return False
        return True

    def _build_mask_for_filters(self, df: pd.DataFrame, filters, mode: str) -> np.ndarray:
        if df is None or df.empty or not filters:
            return np.array([False] * (len(df) if df is not None else 0), dtype=bool)
        mask = []
        for _, row in df.iterrows():
            mask.append(self._row_matches_filters(row, filters, mode))
        return np.array(mask, dtype=bool)

    def _build_union_rule_mask(self, df: pd.DataFrame) -> np.ndarray:
        if df is None or df.empty:
            return np.array([], dtype=bool)
        rules = self._get_rule_definitions()
        if not rules:
            return np.array([False] * len(df), dtype=bool)

        union_mask = np.array([False] * len(df), dtype=bool)
        for filters, mode in rules:
            rule_mask = self._build_mask_for_filters(df, filters, mode)
            union_mask = np.logical_or(union_mask, rule_mask)
        return union_mask

    def _set_proxy_source_dataframe(self, proxy: SmartSearchProxy, df: pd.DataFrame):
        """Update a proxy's source data without swapping model objects when possible."""
        if not isinstance(proxy, SmartSearchProxy):
            return
        source_model = proxy.sourceModel()
        if isinstance(source_model, DataFrameModel):
            source_model.set_dataframe(df)
        else:
            proxy.setSourceModel(DataFrameModel(df))

    def _apply_tab_highlights(self, widget):
        """Apply tab-specific filter highlights to custom/file tabs."""
        if widget is None:
            return
        tab_kind = getattr(widget, "tab_kind", None)
        if tab_kind not in ["custom", "file"]:
            return
        proxy = widget.model() if hasattr(widget, "model") else None
        source_model = proxy.sourceModel() if proxy and hasattr(proxy, "sourceModel") else None
        if not isinstance(source_model, DataFrameModel):
            return
        df = source_model.dataframe()
        if df is None or df.empty:
            source_model.set_highlight_mask(None)
            source_model.filter_manager.clear_all()
            return

        filters, mode = self._ensure_tab_filter_state(widget)
        if not filters:
            source_model.set_highlight_mask(None)
            source_model.filter_manager.clear_all()
            return

        applicable = [f for f in filters if getattr(f, "column", None) in df.columns]
        if not applicable:
            source_model.set_highlight_mask(None)
            source_model.filter_manager.clear_all()
            return

        mask = self._build_mask_for_filters(df, applicable, mode)
        source_model.set_highlight_mask(mask)
        source_model.filter_manager.clear_all()
        for filter_rule in applicable:
            source_model.filter_manager.add_filter(filter_rule)

    def _refresh_rule_state(self):
        """Recompute main-tab highlights and filtered tab based on rules."""
        df = self.model.dataframe()
        if df.empty:
            self.model.set_highlight_mask(None)
            self.model.filter_manager.clear_all()
            self._rebuild_unmatched_tab(np.array([], dtype=bool))
            self._refresh_all_views()
            return

        union_mask = self._build_union_rule_mask(df)
        self.model.set_highlight_mask(union_mask)

        # Update main filter_manager with all rule filters (cell-level highlights only).
        self.model.filter_manager.clear_all()
        for filters, _ in self._get_rule_definitions():
            for filter_rule in filters:
                self.model.filter_manager.add_filter(filter_rule)

        self._rebuild_unmatched_tab(union_mask)
        self._refresh_all_views()
        self._update_ui_state()

    def _rebuild_rule_tab(self, widget):
        if widget is None:
            return
        filters, mode = self._ensure_tab_filter_state(widget)
        base_df = self.model.dataframe()
        mask = self._build_mask_for_filters(base_df, filters, mode)
        snapshot_df = base_df[mask].copy() if not base_df.empty else base_df.copy()

        proxy = widget.model() if hasattr(widget, "model") else None
        if not isinstance(proxy, SmartSearchProxy):
            return

        self._set_proxy_source_dataframe(proxy, snapshot_df)
        proxy.setExtraFilters([])

        # Preserve current search settings
        proxy.setSearchText(self.search_edit.text())
        search_col = self.search_column_combo.currentText()
        source_model = proxy.sourceModel()
        if search_col != "Global" and self._model_has_column(source_model, search_col):
            proxy.setSearchColumn(search_col)
        else:
            proxy.setSearchColumn(None)

        if widget is self._get_current_tab_widget():
            self._update_search_columns(source_model)
            self._update_column_navigator(source_model)
            self._update_ui_state()

    def _rebuild_all_rule_tabs(self):
        for _, widget in self._iter_rule_tabs():
            self._rebuild_rule_tab(widget)

    def _on_filtered_tab_mode_toggled(self, checked: bool):
        """Toggle whether the filtered tab shows matching or non-matching rows."""
        self._filtered_tab_show_matches = bool(checked)
        mode_text = "matching" if self._filtered_tab_show_matches else "non-matching"
        self.status_bar.showMessage(f"Filtered tab now shows {mode_text} rows", 3000)
        self._refresh_rule_state()
        self._sync_active_tab_context()
        self._save_state()

    def _ensure_filtered_tab(self):
        """Ensure the Filtered tab exists."""
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if getattr(widget, "tab_kind", None) == "filtered":
                return i, widget

        table_view = StyledTableView()
        proxy = SmartSearchProxy()
        proxy.setSourceModel(DataFrameModel(pd.DataFrame()))
        proxy.setFilterMode("all")
        table_view.setModel(proxy)
        self._wire_table_view(table_view, allow_filters=False)
        table_view.tab_kind = "filtered"
        table_view.tab_filters = []
        table_view.tab_filter_mode = "all"

        insert_index = 1 if self.tab_widget.count() > 1 else self.tab_widget.count()
        index = self.tab_widget.insertTab(insert_index, table_view, "Filtered")
        self.tab_widget.tabBar().setTabButton(index, self.tab_widget.tabBar().RightSide, None)
        return index, table_view

    def _ensure_unmatched_tab(self):
        """Legacy method - redirects to filtered tab."""
        return self._ensure_filtered_tab()

    def _rebuild_filtered_tab(self, union_mask: np.ndarray):
        """Rebuild the Filtered tab with matching or non-matching rows."""
        index, widget = self._ensure_filtered_tab()
        df = self.model.dataframe()
        if df.empty:
            snapshot_df = df.copy()
        else:
            if union_mask is None or len(union_mask) != len(df):
                snapshot_df = df.iloc[0:0].copy()
            else:
                target_mask = union_mask if self._filtered_tab_show_matches else np.logical_not(union_mask)
                snapshot_df = df[target_mask].copy() if target_mask.any() else df.iloc[0:0].copy()

        proxy = widget.model() if hasattr(widget, "model") else None
        if isinstance(proxy, SmartSearchProxy):
            self._set_proxy_source_dataframe(proxy, snapshot_df)
            proxy.setExtraFilters([])
            proxy.setSearchText(self.search_edit.text())
            search_col = self.search_column_combo.currentText()
            source_model = proxy.sourceModel()
            if search_col != "Global" and self._model_has_column(source_model, search_col):
                proxy.setSearchColumn(search_col)
            else:
                proxy.setSearchColumn(None)
            if widget is self._get_current_tab_widget():
                self._update_search_columns(source_model)
                self._update_column_navigator(source_model)
                self._update_ui_state()

        # Update tab tooltip with count
        count = len(snapshot_df)
        detail = "matching active rules" if self._filtered_tab_show_matches else "not matching active rules"
        self.tab_widget.setTabToolTip(index, f"{count} rows {detail}")

    def _rebuild_unmatched_tab(self, union_mask: np.ndarray):
        """Legacy method - redirects to filtered tab."""
        self._rebuild_filtered_tab(union_mask)
    def _ensure_tab_filter_state(self, widget):
        if widget is None:
            return [], "all"
        if not hasattr(widget, "tab_filters"):
            widget.tab_filters = []
        if not hasattr(widget, "tab_filter_mode"):
            widget.tab_filter_mode = "all"
        return widget.tab_filters, widget.tab_filter_mode

    def _apply_tab_filters(self, widget):
        if widget is None:
            return
        tab_kind = getattr(widget, "tab_kind", None)

        # For base tab, apply filters and update Filtered tab
        if tab_kind == "base":
            proxy = widget.model() if hasattr(widget, "model") else None
            if isinstance(proxy, SmartSearchProxy):
                filters, mode = self._ensure_tab_filter_state(widget)
                proxy.setExtraFilters(filters)
                proxy.setExtraFilterMode(mode)
                # Update the Filtered tab with matching rows
                if filters:
                    self._refresh_rule_state()
            return

        if tab_kind in ["rule", "filtered"]:
            return

        proxy = widget.model() if hasattr(widget, "model") else None
        if isinstance(proxy, SmartSearchProxy):
            filters, mode = self._ensure_tab_filter_state(widget)
            proxy.setExtraFilters(filters)
            proxy.setExtraFilterMode(mode)
        self._apply_tab_highlights(widget)

    def _sync_filter_panel_for_tab(self, widget):
        self.filter_panel.clear_all_chips()
        if widget is None:
            return

        tab_kind = getattr(widget, "tab_kind", None)
        if tab_kind == "base":
            base_filters, mode = self._ensure_tab_filter_state(widget)
            display_filters = list(base_filters)
            for _, rule_widget in self._iter_rule_tabs():
                rule_filters, _ = self._ensure_tab_filter_state(rule_widget)
                for filter_rule in rule_filters:
                    if filter_rule not in display_filters:
                        display_filters.append(filter_rule)
            for filter_rule in display_filters:
                self.filter_panel.add_filter_chip(filter_rule)
            self.filter_panel.set_filter_mode(mode)
            return

        filters, mode = self._ensure_tab_filter_state(widget)
        for filter_rule in filters:
            self.filter_panel.add_filter_chip(filter_rule)
        self.filter_panel.set_filter_mode(mode)

    def _add_filter_to_tab(self, widget, filter_rule):
        if widget is None or filter_rule is None:
            return
        filters, mode = self._ensure_tab_filter_state(widget)
        if filter_rule in filters:
            return
        filters.append(filter_rule)
        widget.tab_filters = filters
        if getattr(widget, "tab_kind", None) == "rule":
            self._rebuild_rule_tab(widget)
            self._refresh_rule_state()
        else:
            self._apply_tab_filters(widget)
        if widget is self._get_current_tab_widget():
            self._sync_filter_panel_for_tab(widget)
        self._update_column_navigator()
        self._update_ui_state()
        self._save_state()

    def _remove_filter_from_tab(self, widget, filter_rule):
        if widget is None or filter_rule is None:
            return
        filters, mode = self._ensure_tab_filter_state(widget)
        new_filters = [f for f in filters if f != filter_rule]
        widget.tab_filters = new_filters
        if getattr(widget, "tab_kind", None) == "rule":
            if not new_filters:
                index = self.tab_widget.indexOf(widget)
                if index > 0:
                    self.tab_widget.removeTab(index)
                    widget.deleteLater()
                self._refresh_rule_state()
                self._sync_active_tab_context()
                self._save_state()
                return
            self._rebuild_rule_tab(widget)
            self._refresh_rule_state()
        else:
            self._apply_tab_filters(widget)
        if widget is self._get_current_tab_widget():
            self._sync_filter_panel_for_tab(widget)
        self._update_column_navigator()
        self._update_ui_state()
        self._save_state()

    def _clear_filters_for_tab(self, widget):
        if widget is None:
            return
        widget.tab_filters = []
        if getattr(widget, "tab_kind", None) == "rule":
            index = self.tab_widget.indexOf(widget)
            if index > 0:
                self.tab_widget.removeTab(index)
                widget.deleteLater()
            self._refresh_rule_state()
            self._sync_active_tab_context()
            self._save_state()
            return
        else:
            self._apply_tab_filters(widget)
        if widget is self._get_current_tab_widget():
            self._sync_filter_panel_for_tab(widget)
        self._update_column_navigator()
        self._update_ui_state()
        self._save_state()

    def _set_tab_filter_mode(self, widget, mode: str):
        if widget is None:
            return
        if mode not in ["all", "any"]:
            mode = "all"
        widget.tab_filter_mode = mode
        if getattr(widget, "tab_kind", None) == "rule":
            self._rebuild_rule_tab(widget)
            self._refresh_rule_state()
        else:
            self._apply_tab_filters(widget)
        if widget is self._get_current_tab_widget():
            self._sync_filter_panel_for_tab(widget)
        self._update_column_navigator()
        self._update_ui_state()
        self._save_state()

    def _get_tab_filter_context(self, widget):
        """Return (FilterManager, mode) for the given tab."""
        filter_manager = FilterManager()
        if widget is None:
            return filter_manager, "all"

        tab_kind = getattr(widget, "tab_kind", None)
        if tab_kind in ["base", "filtered"]:
            for filters, _ in self._get_rule_definitions():
                for filter_rule in filters:
                    filter_manager.add_filter(filter_rule)
            return filter_manager, "any"

        filters, mode = self._ensure_tab_filter_state(widget)
        for filter_rule in filters:
            filter_manager.add_filter(filter_rule)
        return filter_manager, mode

    def _proxy_is_main_model(self, proxy: Optional[SmartSearchProxy]) -> bool:
        if proxy is None:
            return False
        return proxy.sourceModel() is self.model

    def _model_has_column(self, model: Optional[DataFrameModel], column: str) -> bool:
        if model is None:
            return False
        try:
            return column in model.dataframe().columns
        except Exception:
            return False

    def _strip_tab_count(self, text: str) -> str:
        if not text:
            return ""
        if "(" in text and text.rstrip().endswith(")"):
            base = text[:text.rfind("(")].strip()
            return base if base else text
        return text

    def _wire_table_view(self, table_view: StyledTableView, allow_filters: bool = True):
        table_view.cellEditRequested.connect(self._on_edit_cell)
        table_view.allow_column_filters = allow_filters
        if allow_filters:
            table_view.columnFilterRequested.connect(self._on_add_filter_for_column)
            table_view.columnFilterClearRequested.connect(self._on_clear_filters_for_column)

    def _dataframe_for_proxy(self, proxy: SmartSearchProxy, full_source: bool = False) -> pd.DataFrame:
        source_model = proxy.sourceModel()
        if source_model is None:
            return pd.DataFrame()
        df = source_model.dataframe()
        if full_source:
            return df
        visible_indices = [
            proxy.mapToSource(proxy.index(row, 0)).row()
            for row in range(proxy.rowCount())
        ]
        return df.iloc[visible_indices] if visible_indices else df.iloc[0:0]

    def _visible_source_rows(self, proxy: Optional[SmartSearchProxy]) -> List[int]:
        if proxy is None:
            return []
        rows = []
        try:
            for row in range(proxy.rowCount()):
                rows.append(proxy.mapToSource(proxy.index(row, 0)).row())
        except Exception:
            return []
        return rows

    def _export_mask_override_for_proxy(self, proxy: Optional[SmartSearchProxy]) -> Optional[np.ndarray]:
        current_widget = self._get_current_tab_widget()
        if current_widget is None or getattr(current_widget, "tab_kind", None) != "base":
            return None

        base_df = self.model.dataframe()
        union_mask = self._build_union_rule_mask(base_df)
        if proxy is None:
            return union_mask

        rows = self._visible_source_rows(proxy)
        if rows:
            try:
                return union_mask[rows]
            except Exception:
                return union_mask
        return union_mask

    def _set_filter_ui_enabled(self, enabled: bool):
        self.filter_panel.setEnabled(enabled)
        for action in [
            getattr(self, "add_filter_action", None),
            getattr(self, "clear_filters_action", None),
            getattr(self, "save_preset_action", None),
            getattr(self, "load_preset_action", None),
        ]:
            if action is not None:
                action.setEnabled(enabled)
        for button in [
            getattr(self, "filters_btn", None),
        ]:
            if button is not None:
                button.setEnabled(enabled)

    def _set_filter_panel_collapsed(self, collapsed: bool):
        if collapsed == getattr(self, "_filter_panel_collapsed", False):
            return
        self._filter_panel_collapsed = collapsed

        if not hasattr(self, "filter_panel") or not hasattr(self, "content_splitter"):
            return

        self.filter_panel.set_collapsed(collapsed)

        if collapsed:
            self._filter_panel_sizes = self.content_splitter.sizes()
            self.filter_panel.setMinimumWidth(50)
            self.filter_panel.setMaximumWidth(50)
            total = sum(self.content_splitter.sizes()) or self.width()
            self.content_splitter.setSizes([50, max(1, total - 50)])
        else:
            self.filter_panel.setMinimumWidth(self._filter_panel_min_width)
            self.filter_panel.setMaximumWidth(16777215)
            sizes = self._filter_panel_sizes
            if sizes and len(sizes) >= 2:
                self.content_splitter.setSizes(sizes)
            else:
                total = sum(self.content_splitter.sizes()) or self.width()
                left = self._filter_panel_min_width
                self.content_splitter.setSizes([left, max(1, total - left)])

    def _on_filter_panel_collapse_toggled(self, collapsed: bool):
        current_widget = self._get_current_tab_widget()
        tab_kind = getattr(current_widget, "tab_kind", None) if current_widget is not None else None

        if tab_kind == "filtered":
            # Allow temporary expand/collapse on the filtered tab, but keep
            # auto-collapse behavior when returning to non-filtered tabs.
            self._set_filter_panel_collapsed(collapsed)
            self._filter_panel_auto_collapsed = True
            return

        self._filter_panel_user_collapsed = collapsed
        self._filter_panel_auto_collapsed = False
        self._set_filter_panel_collapsed(collapsed)

    def _sync_active_tab_context(self):
        """Update UI elements based on the active tab's model."""
        current_model = self._get_current_model() or self.model
        current_widget = self._get_current_tab_widget()
        tab_kind = getattr(current_widget, "tab_kind", None) if current_widget is not None else None

        if tab_kind == "filtered":
            self._filter_panel_auto_collapsed = True
            self._set_filter_panel_collapsed(True)
        elif getattr(self, "_filter_panel_auto_collapsed", False):
            self._filter_panel_auto_collapsed = False
            self._set_filter_panel_collapsed(getattr(self, "_filter_panel_user_collapsed", False))

        filters_enabled = current_widget is not None and tab_kind != "filtered"
        self._set_filter_ui_enabled(filters_enabled)
        self._sync_filter_panel_for_tab(current_widget if filters_enabled else None)

        if current_widget is not None:
            # Default: show action/mode controls for non-filtered tabs
            self.filter_panel.set_action_controls_visible(True)
            self.filter_panel.set_mode_visible(True)
            self.filter_panel.set_collapse_available(True)
            if tab_kind == "base":
                self.filter_panel.set_context("Rules", "Add a filter to create a rule tab")
                self.filter_panel.set_mode_enabled(True)
                self.filter_panel.add_btn.setText("Create Rule")
            elif tab_kind == "rule":
                self.filter_panel.set_context("Rule Filters", "Define what this rule captures")
                self.filter_panel.set_mode_enabled(True)
                self.filter_panel.add_btn.setText("Add Filter")
            elif tab_kind == "custom":
                self.filter_panel.set_context("Tab Filters", "Filters apply only to this custom tab")
                self.filter_panel.set_mode_enabled(True)
                self.filter_panel.add_btn.setText("Add Filter")
            elif tab_kind == "file":
                self.filter_panel.set_context("Tab Filters", "Filters apply only to this file tab")
                self.filter_panel.set_mode_enabled(True)
                self.filter_panel.add_btn.setText("Add Filter")
            elif tab_kind == "filtered":
                filtered_subtitle = (
                    "Rows matching active rules"
                    if self._filtered_tab_show_matches
                    else "Rows not matching active rules"
                )
                self.filter_panel.set_context("Filtered", filtered_subtitle)
                self.filter_panel.set_mode_enabled(False)
                self.filter_panel.add_btn.setText("Add Filter")
                self.filter_panel.set_action_controls_visible(False)
                self.filter_panel.set_mode_visible(False)
                self.filter_panel.set_collapse_available(True)

            if getattr(self, "_filter_panel_collapsed", False):
                self.filter_panel.set_collapsed(True)
        self._update_search_columns(current_model)
        self._apply_search_to_all_tabs()
        self._update_column_navigator(current_model)
        self._update_ui_state()

    def _apply_search_to_all_tabs(self):
        """Apply current search settings to all proxies safely."""
        text = self.search_edit.text()
        selected = self.search_column_combo.currentText()
        column = None if selected == "Global" else selected
        
        for _, _, proxy in self._iter_tab_proxies():
            proxy.setSearchText(text)
            if column is None:
                proxy.setSearchColumn(None)
            else:
                if self._model_has_column(proxy.sourceModel(), column):
                    proxy.setSearchColumn(column)
                else:
                    proxy.setSearchColumn(None)
        
        self._update_tab_counts()
        self._update_ui_state()

    def _on_filter_panel_width_suggested(self, suggested_width: int):
        if getattr(self, "_filter_panel_collapsed", False):
            return
        if getattr(self, "_filter_panel_user_collapsed", False):
            return
        suggested = max(self._filter_panel_min_width, min(suggested_width, self._filter_panel_max_width))
        self._filter_panel_min_width = suggested
        total = sum(self.content_splitter.sizes()) or self.width()
        if total <= 0:
            return
        self.content_splitter.setSizes([suggested, max(1, total - suggested)])

    def _create_custom_tab(self, name: str, insert_index: Optional[int] = None,
                           source_proxy: Optional[SmartSearchProxy] = None) -> Optional[int]:
        if not name:
            return None

        # New custom tabs are independent snapshots of the current view.
        source_proxy = source_proxy or self._get_current_proxy()
        if source_proxy is not None:
            snapshot_df = self._dataframe_for_proxy(source_proxy).copy().reset_index(drop=True)
        else:
            snapshot_df = self.model.dataframe().copy().reset_index(drop=True)

        table_view = StyledTableView()
        new_model = DataFrameModel(snapshot_df)
        proxy = SmartSearchProxy()
        proxy.setSourceModel(new_model)
        proxy.setFilterMode("all")

        table_view.setModel(proxy)
        self._wire_table_view(table_view, allow_filters=True)
        table_view.tab_kind = "custom"
        table_view.tab_filters = []
        table_view.tab_filter_mode = "all"

        self._extra_models.append(new_model)
        
        if insert_index is not None and 0 <= insert_index <= self.tab_widget.count():
            return self.tab_widget.insertTab(insert_index, table_view, name)
        return self.tab_widget.addTab(table_view, name)

    def _create_file_tab(self, df: pd.DataFrame, filepath: str, tab_name: Optional[str] = None,
                         insert_index: Optional[int] = None) -> Optional[int]:
        if df is None or df.empty:
            return None
        
        table_view = StyledTableView()
        new_model = DataFrameModel(df)
        new_proxy = SmartSearchProxy()
        new_proxy.setSourceModel(new_model)
        new_proxy.setFilterMode("all")
        
        # Apply current search settings
        new_proxy.setSearchText(self.search_edit.text())
        search_col = self.search_column_combo.currentText()
        if search_col != "Global" and self._model_has_column(new_model, search_col):
            new_proxy.setSearchColumn(search_col)
        
        table_view.setModel(new_proxy)
        self._wire_table_view(table_view, allow_filters=False)
        table_view.tab_kind = "file"
        table_view.file_path = filepath
        table_view.tab_filters = []
        table_view.tab_filter_mode = "all"
        
        self._extra_models.append(new_model)
        
        tab_label = tab_name or os.path.basename(filepath)
        if insert_index is not None and 0 <= insert_index <= self.tab_widget.count():
            return self.tab_widget.insertTab(insert_index, table_view, tab_label)
        return self.tab_widget.addTab(table_view, tab_label)

    def _create_file_tab_from_path(self, filepath: str, tab_name: Optional[str] = None,
                                   insert_index: Optional[int] = None) -> Optional[int]:
        if not filepath or not os.path.exists(filepath):
            return None
        
        try:
            df, needs_sheet, sheets = load_dataframe_from_file(filepath)
            if needs_sheet and sheets:
                df, _, _ = load_dataframe_from_file(filepath, sheet_name=sheets[0])
            df = add_date_column(df)
            return self._create_file_tab(df, filepath, tab_name=tab_name, insert_index=insert_index)
        except Exception as e:
            print(f"Error restoring file tab {filepath}: {e}")
            return None

    def _filter_from_dict(self, filter_data: dict) -> Optional[FilterRule]:
        filter_type = filter_data.get('type')
        if filter_type == 'numeric':
            return NumericFilter.from_dict(filter_data)
        if filter_type == 'text':
            return TextFilter.from_dict(filter_data)
        if filter_type == 'date':
            return DateFilter.from_dict(filter_data)
        return None

    def _restore_tabs_from_state(self):
        """Restore tabs from saved state."""
        tabs = getattr(self, "_pending_tabs", [])
        if not tabs:
            return
        
        # Reset to base tab only
        for i in range(self.tab_widget.count() - 1, 0, -1):
            widget = self.tab_widget.widget(i)
            self.tab_widget.removeTab(i)
            if widget:
                widget.deleteLater()
        
        # Reset filters for base tab
        base_widget = self.tab_widget.widget(0)
        if base_widget:
            base_widget.tab_filters = []
            base_widget.tab_filter_mode = "all"
        self.filter_panel.clear_all_chips()
        
        insert_index = 1
        
        # Set base tab name if present
        if tabs and tabs[0].get("type") == "base":
            base_name = tabs[0].get("name") or "All Students"
            self.tab_widget.setTabText(0, base_name)
            tabs_iter = tabs[1:]
        else:
            tabs_iter = tabs
        
        for entry in tabs_iter:
            tab_type = entry.get("type")
            tab_name = entry.get("name") or "Tab"
            filter_mode = entry.get("filter_mode") or "all"

            filters = []
            filters_data = entry.get("filters")
            if not filters_data and entry.get("filter"):
                filters_data = [entry.get("filter")]
            if filters_data:
                for filter_data in filters_data:
                    filter_rule = self._filter_from_dict(filter_data or {})
                    if not filter_rule:
                        continue
                    filters.append(filter_rule)
            
            if tab_type in ["rule", "filter"]:
                filtered = [f for f in filters if self._model_has_column(self.model, f.column)]
                if filtered:
                    self._create_filter_tab(
                        filtered,
                        insert_index=insert_index,
                        tab_name=tab_name,
                        filter_mode=filter_mode,
                        switch_to=False,
                        save_state=False,
                        refresh_rules=False
                    )
                    insert_index += 1
            
            elif tab_type == "custom":
                new_index = self._create_custom_tab(tab_name, insert_index=insert_index)
                if new_index is not None:
                    widget = self.tab_widget.widget(new_index)
                    filtered = [f for f in filters if self._model_has_column(self.model, f.column)]
                    if widget is not None and filtered:
                        widget.tab_filters = filtered
                        widget.tab_filter_mode = filter_mode
                        self._apply_tab_filters(widget)
                    insert_index += 1
            
            elif tab_type == "file":
                file_path = entry.get("file_path")
                new_index = self._create_file_tab_from_path(file_path, tab_name=tab_name, insert_index=insert_index)
                if new_index is not None:
                    widget = self.tab_widget.widget(new_index)
                    if widget is not None and filters:
                        proxy = widget.model() if hasattr(widget, "model") else None
                        source_model = proxy.sourceModel() if proxy and hasattr(proxy, "sourceModel") else None
                        if source_model is not None:
                            filtered = [f for f in filters if self._model_has_column(source_model, f.column)]
                        else:
                            filtered = filters
                        widget.tab_filters = filtered
                        widget.tab_filter_mode = filter_mode
                        self._apply_tab_filters(widget)
                    insert_index += 1

        self._pending_tabs = []
        self._sync_active_tab_context()
        self._refresh_rule_state()
        self._save_state()
    
    def _update_search_columns(self, model: Optional[DataFrameModel] = None):
        """Update search column combo boxes based on active model."""
        active_model = model or self._get_current_model() or self.model

        columns = []
        if active_model is not None and active_model.rowCount() >= 0:
            try:
                columns = [str(c) for c in active_model.dataframe().columns]
            except Exception:
                columns = []

        # Update modern search bar
        if hasattr(self, 'search_bar'):
            self.search_bar.update_columns(columns)
    
    def _update_column_navigator(self, model: Optional[DataFrameModel] = None):
        """Update column navigator - Reactive."""
        active_model = model or self._get_current_model() or self.model
        
        if active_model is None or active_model.rowCount() == 0:
            self.column_navigator.set_columns([], {}, set())
            return
        
        try:
            columns = [str(c) for c in active_model.dataframe().columns]
        except Exception:
            columns = []
        
        column_types = {}
        for col in columns:
            column_types[col] = active_model.get_column_dtype(col)
        
        filtered_columns = set()
        current_widget = self._get_current_tab_widget()
        tab_kind = getattr(current_widget, "tab_kind", None) if current_widget is not None else None
        if tab_kind in ["base", "filtered"]:
            for filters, _ in self._get_rule_definitions():
                for filter_rule in filters:
                    filtered_columns.add(filter_rule.column)
        elif current_widget is not None:
            filters, _ = self._ensure_tab_filter_state(current_widget)
            for filter_rule in filters:
                filtered_columns.add(filter_rule.column)
        
        self.column_navigator.set_columns(columns, column_types, filtered_columns)
    
    def _update_ui_state(self):
        """Update modern UI elements based on current state."""
        current_proxy = self._get_current_proxy()
        current_model = self._get_current_model() or self.model
        total_rows = current_model.rowCount() if current_model else 0
        visible_rows = current_proxy.rowCount() if current_proxy else total_rows

        # Update modern header
        self.header.update_row_count(visible_rows, total_rows)

        # Update filter count in header
        current_widget = self._get_current_tab_widget()
        tab_kind = getattr(current_widget, "tab_kind", None) if current_widget is not None else None
        if tab_kind in ["base", "filtered"]:
            rule_count = len(self._get_rule_definitions())
            self.header.update_filter_count(rule_count)
        else:
            filters, _ = self._ensure_tab_filter_state(current_widget)
            self.header.update_filter_count(len(filters))

        # Update file name in header
        current_widget = self.tab_widget.widget(self.tab_widget.currentIndex())
        file_path = getattr(current_widget, "file_path", None)
        if file_path:
            self.header.update_file_name(os.path.basename(file_path))
        elif self.current_file_path:
            self.header.update_file_name(os.path.basename(self.current_file_path))
        else:
            self.header.update_file_name("No file")

        self._update_tab_counts()
    
    def _update_tab_counts(self):
        """Update tab tooltips with row counts (NOT in tab name)."""
        for index, widget, proxy in self._iter_tab_proxies():
            count = proxy.get_visible_row_count()
            current_text = self._strip_tab_count(self.tab_widget.tabText(index))
            # Don't add count to tab name - just update tooltip
            self.tab_widget.setTabText(index, current_text)
            self.tab_widget.setTabToolTip(index, f"{count:,} rows")
    
    def _compute_highlight_mask(self):
        """Compute boolean mask of filtered (matched) rows."""
        current_widget = self._get_current_tab_widget()
        tab_kind = getattr(current_widget, "tab_kind", None) if current_widget is not None else None

        if tab_kind == "base":
            df = self.model.dataframe()
            return self._build_union_rule_mask(df)

        current_model = self._get_current_model() or self.model
        if current_model is None:
            return np.array([], dtype=bool)
        df = current_model.dataframe()
        if df.empty:
            return np.array([], dtype=bool)

        if tab_kind == "filtered":
            return np.array([False] * len(df), dtype=bool)

        filters, mode = self._ensure_tab_filter_state(current_widget)
        return self._build_mask_for_filters(df, filters, mode)
    
    def _refresh_all_views(self):
        """Refresh all proxy filters."""
        for _, _, proxy in self._iter_tab_proxies():
            proxy.invalidateFilter()
        
        if not self.df.empty:
            top_left = self.model.index(0, 0)
            bottom_right = self.model.index(
                self.model.rowCount() - 1,
                self.model.columnCount() - 1
            )
            self.model.dataChanged.emit(top_left, bottom_right, [Qt.BackgroundRole, Qt.ForegroundRole])
    
    def _save_state(self):
        """Save application state to disk."""
        if not hasattr(self, 'model'):
            return
        
        state = {
            'last_file': self.current_file_path,
            'filtered_tab_mode': 'matched' if self._filtered_tab_show_matches else 'unmatched',
            'tabs': []
        }
        
        # Save tab names
        for i in range(self.tab_widget.count()):
            tab_text = self._strip_tab_count(self.tab_widget.tabText(i))
            widget = self.tab_widget.widget(i)

            if getattr(widget, "tab_kind", None) == "filtered":
                continue

            entry = {'name': tab_text}
            filters = list(getattr(widget, "tab_filters", [])) if widget is not None else []
            entry['filters'] = [f.to_dict() for f in filters]
            entry['filter_mode'] = getattr(widget, "tab_filter_mode", "all")
            
            if i == 0:
                entry['type'] = 'base'
            elif getattr(widget, "tab_kind", None) == "rule":
                entry['type'] = 'rule'
            elif getattr(widget, "tab_kind", None) == "file" and getattr(widget, "file_path", None):
                entry['type'] = 'file'
                entry['file_path'] = widget.file_path
            else:
                entry['type'] = 'custom'
            
            state['tabs'].append(entry)
        
        try:
            with open('app_state.json', 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Error saving state: {e}")
    
    def _load_saved_state(self):
        """Load saved application state."""
        if not os.path.exists('app_state.json'):
            return
        
        try:
            with open('app_state.json', 'r') as f:
                state = json.load(f)

            filtered_mode = state.get('filtered_tab_mode', 'matched')
            self._filtered_tab_show_matches = (filtered_mode != 'unmatched')
            mode_action = getattr(self, "filtered_tab_mode_action", None)
            if mode_action is not None:
                mode_action.blockSignals(True)
                mode_action.setChecked(self._filtered_tab_show_matches)
                mode_action.blockSignals(False)
            
            # Legacy filters (pre per-tab)
            self._pending_filters = []
            for filter_data in state.get('filters', []):
                filter_rule = self._filter_from_dict(filter_data)
                if filter_rule:
                    self._pending_filters.append(filter_rule)

            # Load tabs
            tabs_data = state.get('tabs', [])
            if tabs_data and isinstance(tabs_data[0], dict):
                self._pending_tabs = tabs_data
            else:
                # Legacy format: list of tab names
                self._pending_tabs = []
                if tabs_data and isinstance(tabs_data[0], str):
                    self._pending_base_tab_name = tabs_data[0]

        
        except Exception as e:
            print(f"Error loading state: {e}")
    
    def _autoload_last_file(self):
        """Auto-load the last opened file on startup."""
        last_file = get_last_loaded_file()
        
        if last_file and os.path.exists(last_file):
            self.status_bar.showMessage(f"Auto-loading: {os.path.basename(last_file)}", 3000)
            self.load_file(last_file)
        elif last_file:
            self.status_bar.showMessage("Last file no longer exists", 3000)
    
    def _apply_pending_filters(self):
        """Apply pending filters after file is loaded."""
        if self.df.empty:
            return
        
        # Restore tabs if present in state
        if getattr(self, "_pending_tabs", []):
            self._restore_tabs_from_state()
            return
        
        if getattr(self, "_pending_base_tab_name", None):
            self.tab_widget.setTabText(0, self._pending_base_tab_name)
            self._pending_base_tab_name = None
        
        if not hasattr(self, '_pending_filters') or not self._pending_filters:
            return
        
        available_columns = set(str(c) for c in self.df.columns)

        legacy_filters = []
        for filter_rule in self._pending_filters:
            if filter_rule.column in available_columns:
                legacy_filters.append(filter_rule)

        if legacy_filters:
            self._create_filter_tab(
                legacy_filters,
                insert_index=1,
                tab_name="Restored Rules",
                filter_mode="all",
                switch_to=False,
                save_state=False,
                refresh_rules=False
            )

        self._pending_filters = []
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save state
        self._save_state()
        
        # Create final snapshot
        if not self.df.empty:
            try:
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                
                os.makedirs("archives", exist_ok=True)
                snapshot_path = os.path.join("archives", f"snapshot_{timestamp}.xlsx")
                
                export_to_excel_formatted(
                    self.df,
                    snapshot_path,
                    self.model.filter_manager,
                    split_sheets=True
                )
            except Exception as e:
                print(f"Error saving final snapshot: {e}")
        
        event.accept()
