"""
Table views and secondary windows - Clean UI without emojis.
"""

import os
from PyQt5.QtWidgets import (
    QTableView, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QComboBox, QLabel, QHeaderView, QMenu, QAction,
    QMessageBox, QInputDialog, QAbstractItemView, QPushButton, QListWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QFont, QColor
from models import DataFrameModel
from proxies import SmartSearchProxy
from styles import AppTheme
import pandas as pd


class StyledTableView(QTableView):
    """Enhanced table view with clean styling."""
    
    cellEditRequested = pyqtSignal(object)
    columnFilterRequested = pyqtSignal(str)
    columnFilterClearRequested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.allow_column_filters = True
        self._setup_ui()
        self._setup_context_menu()
    
    def _setup_ui(self):
        """Configure table appearance."""
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setAlternatingRowColors(True)
        self.setShowGrid(True)
        self.setGridStyle(Qt.SolidLine)
        
        # Headers
        self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionsMovable(True)
        self.verticalHeader().setDefaultSectionSize(32)
        
        self.setSortingEnabled(True)
        
        # High contrast styling
        self.setStyleSheet(f"""
            QTableView {{
                gridline-color: {AppTheme.GRAY_200};
                background-color: {AppTheme.BACKGROUND};
                selection-background-color: {AppTheme.PRIMARY};
                selection-color: #FFFFFF;
                color: {AppTheme.TEXT};
                border: 2px solid {AppTheme.BORDER};
            }}
            QTableView::item {{
                padding: 6px;
            }}
            QTableView::item:hover {{
                background-color: {AppTheme.GRAY_100};
            }}
            QHeaderView::section {{
                background-color: {AppTheme.GRAY_50};
                padding: 8px;
                border: 1px solid {AppTheme.BORDER};
                font-weight: 600;
                color: {AppTheme.TEXT};
            }}
            QHeaderView::section:hover {{
                background-color: {AppTheme.GRAY_100};
            }}
        """)
    
    def _setup_context_menu(self):
        """Setup context menus."""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_cell_context_menu)
        
        header = self.horizontalHeader()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self._show_header_context_menu)
    
    def _show_cell_context_menu(self, pos: QPoint):
        """Show context menu for table cells."""
        index = self.indexAt(pos)
        
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
        
        if index.isValid():
            edit_action = QAction("Edit Cell...", self)
            edit_action.triggered.connect(lambda: self.cellEditRequested.emit(index))
            menu.addAction(edit_action)
            
            menu.addSeparator()
            
            copy_value = QAction("Copy Value", self)
            copy_value.triggered.connect(lambda: self._copy_cell_value(index))
            menu.addAction(copy_value)
            
            copy_row = QAction("Copy Row", self)
            copy_row.triggered.connect(lambda: self._copy_row(index))
            menu.addAction(copy_row)
        
        if not menu.isEmpty():
            menu.exec_(self.viewport().mapToGlobal(pos))
    
    def _show_header_context_menu(self, pos: QPoint):
        """Show context menu for column headers."""
        header = self.horizontalHeader()
        logical_index = header.logicalIndexAt(pos)
        
        if logical_index < 0:
            return
        
        model = self.model()
        if model is None:
            return
        
        col_name = model.headerData(logical_index, Qt.Horizontal, Qt.DisplayRole)
        col_name = str(col_name).replace("[F] ", "")
        
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
        
        if self.allow_column_filters:
            add_filter = QAction(f"Add Filter to '{col_name}'", self)
            add_filter.triggered.connect(lambda: self.columnFilterRequested.emit(col_name))
            menu.addAction(add_filter)

            clear_filter = QAction(f"Remove Filters from '{col_name}'", self)
            clear_filter.triggered.connect(lambda: self.columnFilterClearRequested.emit(col_name))
            menu.addAction(clear_filter)
            menu.addSeparator()
        
        sort_asc = QAction("Sort Ascending", self)
        sort_asc.triggered.connect(lambda: self.sortByColumn(logical_index, Qt.AscendingOrder))
        menu.addAction(sort_asc)
        
        sort_desc = QAction("Sort Descending", self)
        sort_desc.triggered.connect(lambda: self.sortByColumn(logical_index, Qt.DescendingOrder))
        menu.addAction(sort_desc)
        
        menu.addSeparator()
        
        hide_col = QAction("Hide Column", self)
        hide_col.triggered.connect(lambda: self._hide_column(logical_index))
        menu.addAction(hide_col)

        hidden_columns = [i for i in range(model.columnCount()) if self.isColumnHidden(i)]
        if hidden_columns:
            menu.addSeparator()

            unhide_all = QAction("Unhide All Columns", self)
            unhide_all.triggered.connect(self._unhide_all_columns)
            menu.addAction(unhide_all)

            for hidden_idx in hidden_columns:
                hidden_name = model.headerData(hidden_idx, Qt.Horizontal, Qt.DisplayRole)
                hidden_name = str(hidden_name).replace("[F] ", "")
                unhide_one = QAction(f"Unhide '{hidden_name}'", self)
                unhide_one.triggered.connect(lambda checked=False, idx=hidden_idx: self._unhide_column(idx))
                menu.addAction(unhide_one)

        autosize = QAction("Auto-size Column", self)
        autosize.triggered.connect(lambda: self.resizeColumnToContents(logical_index))
        menu.addAction(autosize)
        
        menu.exec_(header.mapToGlobal(pos))
    
    def _copy_cell_value(self, index):
        """Copy cell value to clipboard."""
        from PyQt5.QtWidgets import QApplication
        value = index.data(Qt.DisplayRole)
        if value is not None:
            QApplication.clipboard().setText(str(value))
    
    def _copy_row(self, index):
        """Copy entire row to clipboard."""
        from PyQt5.QtWidgets import QApplication
        model = self.model()
        row = index.row()
        
        values = []
        for col in range(model.columnCount()):
            cell_index = model.index(row, col)
            value = cell_index.data(Qt.DisplayRole)
            values.append(str(value) if value is not None else "")
        
        QApplication.clipboard().setText("\t".join(values))
    
    def _hide_column(self, logical_index):
        """Hide a column."""
        self.setColumnHidden(logical_index, True)

    def _unhide_column(self, logical_index):
        """Unhide a specific column."""
        self.setColumnHidden(logical_index, False)

    def _unhide_all_columns(self):
        """Unhide all columns."""
        model = self.model()
        if model is None:
            return
        for col in range(model.columnCount()):
            self.setColumnHidden(col, False)


class SecondaryTableWindow(QMainWindow):
    """Secondary window for viewing data subsets."""
    
    def __init__(self, df: pd.DataFrame, title: str = "Data Subset", parent=None):
        super().__init__(parent)
        self.df = df
        self.setWindowTitle(title)
        self.resize(1100, 650)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI components."""
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Search bar
        search_layout = QHBoxLayout()
        
        search_label = QLabel("Search:")
        search_label.setStyleSheet(f"color: {AppTheme.TEXT}; font-weight: 600;")
        search_layout.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search across all columns...")
        self.search_edit.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_edit)
        
        search_layout.addWidget(QLabel("in:"))
        
        self.column_combo = QComboBox()
        self.column_combo.addItem("Global")
        if not self.df.empty:
            self.column_combo.addItems([str(c) for c in self.df.columns])
        self.column_combo.currentIndexChanged.connect(self._on_column_changed)
        search_layout.addWidget(self.column_combo)
        
        layout.addLayout(search_layout)
        
        # Table view
        self.table_view = StyledTableView()
        self.table_view.cellEditRequested.connect(self._on_edit_cell)
        
        # Model and proxy
        self.model = DataFrameModel(self.df)
        self.proxy = SmartSearchProxy()
        self.proxy.setSourceModel(self.model)
        self.table_view.setModel(self.proxy)
        
        layout.addWidget(self.table_view)
        
        # Status bar
        self.statusBar().showMessage(f"{len(self.df)} rows loaded")
        self.statusBar().setStyleSheet(f"""
            QStatusBar {{
                background-color: {AppTheme.GRAY_50};
                color: {AppTheme.TEXT};
                font-weight: 600;
                border-top: 2px solid {AppTheme.BORDER};
            }}
        """)
    
    def _on_search_changed(self, text):
        """Handle search text changes."""
        self.proxy.setSearchText(text)
        visible = self.proxy.get_visible_row_count()
        self.statusBar().showMessage(f"{visible} of {len(self.df)} rows visible")
    
    def _on_column_changed(self, index):
        """Handle column selection changes."""
        text = self.column_combo.currentText()
        if text == "Global":
            self.proxy.setSearchColumn(None)
        else:
            self.proxy.setSearchColumn(text)
        
        visible = self.proxy.get_visible_row_count()
        self.statusBar().showMessage(f"{visible} of {len(self.df)} rows visible")
    
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
            source_index = self.proxy.mapToSource(proxy_index)
            self.model.setData(source_index, new_value, Qt.EditRole)
            self.statusBar().showMessage("Cell updated", 3000)


class ArchiveBrowserDialog(QMainWindow):
    """Dialog for browsing archive history with enhanced features."""
    
    archiveSelected = pyqtSignal(str)
    
    def __init__(self, archives: list, parent=None):
        super().__init__(parent)
        self.archives = archives
        self.setWindowTitle("Archive Manager")
        self.resize(900, 700)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI components."""
        from utils import format_file_size
        
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title and info
        header_layout = QHBoxLayout()
        
        title = QLabel("Archive Manager")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {AppTheme.TEXT};")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Summary info
        total_size = sum(a['size'] for a in self.archives)
        info_label = QLabel(f"{len(self.archives)} archives | Total size: {format_file_size(total_size)}")
        info_label.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY}; font-size: 10pt;")
        header_layout.addWidget(info_label)
        
        layout.addLayout(header_layout)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        search_label = QLabel("Filter:")
        search_label.setStyleSheet(f"color: {AppTheme.TEXT}; font-weight: 600;")
        filter_layout.addWidget(search_label)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search by date or filename...")
        self.search_box.textChanged.connect(self._filter_archives)
        filter_layout.addWidget(self.search_box, 1)
        
        # Quick filter buttons
        today_btn = QPushButton("Today")
        today_btn.clicked.connect(lambda: self._quick_filter("today"))
        today_btn.setMaximumWidth(80)
        filter_layout.addWidget(today_btn)
        
        week_btn = QPushButton("This Week")
        week_btn.clicked.connect(lambda: self._quick_filter("week"))
        week_btn.setMaximumWidth(100)
        filter_layout.addWidget(week_btn)
        
        month_btn = QPushButton("This Month")
        month_btn.clicked.connect(lambda: self._quick_filter("month"))
        month_btn.setMaximumWidth(100)
        filter_layout.addWidget(month_btn)
        
        all_btn = QPushButton("All")
        all_btn.clicked.connect(lambda: self._quick_filter("all"))
        all_btn.setMaximumWidth(60)
        filter_layout.addWidget(all_btn)
        
        layout.addLayout(filter_layout)
        
        # List of archives
        self.archive_list = QListWidget()
        self.archive_list.setStyleSheet(f"""
            QListWidget {{
                border: 2px solid {AppTheme.BORDER};
                background-color: {AppTheme.BACKGROUND};
                color: {AppTheme.TEXT};
                font-family: 'Courier New', monospace;
                font-size: 10pt;
            }}
            QListWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {AppTheme.GRAY_200};
            }}
            QListWidget::item:selected {{
                background-color: {AppTheme.PRIMARY};
                color: #FFFFFF;
            }}
            QListWidget::item:hover {{
                background-color: {AppTheme.GRAY_100};
            }}
        """)
        
        self._populate_archive_list(self.archives)
        
        layout.addWidget(self.archive_list)
        
        # Details panel
        self.details_label = QLabel("Select an archive to view details")
        self.details_label.setStyleSheet(f"""
            QLabel {{
                padding: 12px;
                background-color: {AppTheme.GRAY_50};
                border: 2px solid {AppTheme.BORDER};
                border-radius: 4px;
                color: {AppTheme.TEXT};
            }}
        """)
        self.details_label.setWordWrap(True)
        layout.addWidget(self.details_label)
        
        self.archive_list.currentItemChanged.connect(self._on_selection_changed)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.open_btn = QPushButton("Open Archive")
        self.open_btn.setEnabled(False)
        self.open_btn.clicked.connect(self._on_open)
        self.open_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.PRIMARY};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.PRIMARY_DARK};
            }}
            QPushButton:disabled {{
                background-color: {AppTheme.GRAY_300};
                color: {AppTheme.GRAY_500};
            }}
        """)
        
        self.open_folder_btn = QPushButton("Open Folder")
        self.open_folder_btn.setEnabled(False)
        self.open_folder_btn.clicked.connect(self._on_open_folder)
        self.open_folder_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.SUCCESS};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: #0EA371;
            }}
            QPushButton:disabled {{
                background-color: {AppTheme.GRAY_300};
                color: {AppTheme.GRAY_500};
            }}
        """)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self._on_delete)
        self.delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.ERROR};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: #DC2626;
            }}
            QPushButton:disabled {{
                background-color: {AppTheme.GRAY_300};
                color: {AppTheme.GRAY_500};
            }}
        """)
        
        clean_old_btn = QPushButton("Clean Old Archives...")
        clean_old_btn.clicked.connect(self._on_clean_old)
        clean_old_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.WARNING};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: #D97706;
            }}
        """)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.GRAY_600};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 11pt;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.GRAY_700};
            }}
        """)
        
        button_layout.addWidget(self.open_btn)
        button_layout.addWidget(self.open_folder_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(clean_old_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _populate_archive_list(self, archives):
        """Populate the archive list."""
        from utils import format_file_size
        import datetime
        
        self.archive_list.clear()
        
        if not archives:
            item = QListWidgetItem("No archives found")
            item.setFlags(Qt.NoItemFlags)
            self.archive_list.addItem(item)
            return
        
        for archive in archives:
            timestamp = archive['timestamp']
            size = archive['size']
            filename = archive['filename']
            
            if timestamp:
                # Calculate how long ago
                now = datetime.datetime.now()
                delta = now - timestamp
                
                if delta.days == 0:
                    ago_str = "Today"
                elif delta.days == 1:
                    ago_str = "Yesterday"
                elif delta.days < 7:
                    ago_str = f"{delta.days} days ago"
                elif delta.days < 30:
                    weeks = delta.days // 7
                    ago_str = f"{weeks} week{'s' if weeks > 1 else ''} ago"
                else:
                    months = delta.days // 30
                    ago_str = f"{months} month{'s' if months > 1 else ''} ago"
                
                time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                item_text = f"{time_str}  |  {format_file_size(size):>10}  |  {ago_str:>15}"
            else:
                item_text = f"Unknown date  |  {format_file_size(size):>10}  |  {filename}"
            
            from PyQt5.QtWidgets import QListWidgetItem
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, archive)
            
            self.archive_list.addItem(item)
    
    def _filter_archives(self, text):
        """Filter archives based on search text."""
        text = text.lower()
        
        for i in range(self.archive_list.count()):
            item = self.archive_list.item(i)
            if not item.flags() & Qt.ItemIsEnabled:
                continue
            
            item_text = item.text().lower()
            archive = item.data(Qt.UserRole)
            
            if text in item_text or (archive and text in archive.get('filename', '').lower()):
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def _quick_filter(self, period):
        """Quick filter by time period."""
        import datetime
        
        now = datetime.datetime.now()
        
        if period == "all":
            self.search_box.clear()
            for i in range(self.archive_list.count()):
                item = self.archive_list.item(i)
                item.setHidden(False)
            return
        
        for i in range(self.archive_list.count()):
            item = self.archive_list.item(i)
            if not item.flags() & Qt.ItemIsEnabled:
                continue
            
            archive = item.data(Qt.UserRole)
            if not archive or not archive.get('timestamp'):
                item.setHidden(True)
                continue
            
            timestamp = archive['timestamp']
            delta = now - timestamp
            
            if period == "today":
                show = delta.days == 0
            elif period == "week":
                show = delta.days < 7
            elif period == "month":
                show = delta.days < 30
            else:
                show = True
            
            item.setHidden(not show)
    
    def _on_selection_changed(self, current, previous):
        """Handle archive selection changes."""
        from utils import format_file_size
        import os
        
        if current is None or not current.flags() & Qt.ItemIsEnabled:
            self.details_label.setText("Select an archive to view details")
            self.open_btn.setEnabled(False)
            self.open_folder_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            return
        
        archive = current.data(Qt.UserRole)
        
        if archive:
            timestamp = archive['timestamp']
            size = archive['size']
            filepath = archive['path']
            
            details = f"""<b>File:</b> {archive['filename']}<br>
<b>Date:</b> {timestamp.strftime("%Y-%m-%d %H:%M:%S") if timestamp else "Unknown"}<br>
<b>Size:</b> {format_file_size(size)}<br>
<b>Path:</b> {filepath}<br>"""
            
            self.details_label.setText(details)
            self.open_btn.setEnabled(True)
            self.open_folder_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
    
    def _on_open(self):
        """Handle open button click."""
        current = self.archive_list.currentItem()
        if current:
            archive = current.data(Qt.UserRole)
            if archive:
                self.archiveSelected.emit(archive['path'])
                self.close()
    
    def _on_open_folder(self):
        """Open the archives folder in file explorer."""
        import subprocess
        import platform
        
        archives_dir = os.path.join(os.getcwd(), "archives")
        
        if platform.system() == "Windows":
            os.startfile(archives_dir)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", archives_dir])
        else:  # Linux
            subprocess.run(["xdg-open", archives_dir])
    
    def _on_delete(self):
        """Delete selected archive."""
        current = self.archive_list.currentItem()
        if not current:
            return
        
        archive = current.data(Qt.UserRole)
        
        if not archive:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete this archive?\n\n{archive['filename']}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                os.remove(archive['path'])
                self.archives.remove(archive)
                self._populate_archive_list(self.archives)
                QMessageBox.information(self, "Deleted", "Archive deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete archive:\n{str(e)}")
    
    def _on_clean_old(self):
        """Clean old archives based on user criteria."""
        if not self.archives:
            QMessageBox.information(self, "No Archives", "No archives to clean.")
            return
        
        from PyQt5.QtWidgets import QInputDialog
        
        options = [
            "Older than 30 days",
            "Older than 60 days",
            "Older than 90 days",
            "Keep only last 10",
            "Keep only last 20",
            "Keep only last 50"
        ]
        
        choice, ok = QInputDialog.getItem(
            self,
            "Clean Old Archives",
            "Select cleanup criteria:",
            options,
            0,
            False
        )
        
        if not ok:
            return
        
        import datetime
        now = datetime.datetime.now()
        to_delete = []
        
        if "days" in choice:
            days = int(choice.split()[2])
            for archive in self.archives:
                if archive.get('timestamp'):
                    if (now - archive['timestamp']).days > days:
                        to_delete.append(archive)
        
        elif "Keep only last" in choice:
            keep_count = int(choice.split()[-1])
            if len(self.archives) > keep_count:
                # Sort by timestamp, newest first
                sorted_archives = sorted(
                    self.archives,
                    key=lambda x: x.get('timestamp') or datetime.datetime.min,
                    reverse=True
                )
                to_delete = sorted_archives[keep_count:]
        
        if not to_delete:
            QMessageBox.information(self, "Nothing to Delete", "No archives match the criteria.")
            return
        
        total_size = sum(a['size'] for a in to_delete)
        from utils import format_file_size
        
        reply = QMessageBox.question(
            self,
            "Confirm Cleanup",
            f"This will delete {len(to_delete)} archive(s) and free up {format_file_size(total_size)}.\n\nContinue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            deleted_count = 0
            for archive in to_delete:
                try:
                    os.remove(archive['path'])
                    self.archives.remove(archive)
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {archive['filename']}: {e}")
            
            self._populate_archive_list(self.archives)
            QMessageBox.information(
                self,
                "Cleanup Complete",
                f"Deleted {deleted_count} archive(s)."
            )
