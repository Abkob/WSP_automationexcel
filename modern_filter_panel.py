"""
Modern Filter Panel - Clean, intuitive, fast
Streamlined for 2-3 click workflow
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QComboBox, QMenu
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from styles import AppTheme
from models import FilterRule, NumericFilter, TextFilter, DateFilter
from typing import List


class ModernFilterChip(QFrame):
    """Sleek filter chip with hover effects."""

    removeClicked = pyqtSignal(object)
    editClicked = pyqtSignal(object)
    tabRequested = pyqtSignal(object)

    def __init__(self, filter_rule: FilterRule, parent=None):
        super().__init__(parent)
        self.filter_rule = filter_rule
        self._hovered = False
        self._setup_ui()

    def _setup_ui(self):
        """Create modern chip design."""
        self.setFrameStyle(QFrame.NoFrame)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        # Rule icon based on type
        icon = self._get_rule_icon()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 12pt;")
        layout.addWidget(icon_label)

        # Rule text
        rule_text = str(self.filter_rule)
        self.text_label = QLabel(rule_text)
        self.text_label.setWordWrap(False)
        self.text_label.setStyleSheet(f"""
            color: {AppTheme.TEXT};
            font-weight: 600;
            font-size: 10pt;
            background: transparent;
            border: none;
        """)
        layout.addWidget(self.text_label, 1)

        # Remove button
        self.remove_btn = QPushButton("×")
        self.remove_btn.setFixedSize(24, 24)
        self.remove_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {AppTheme.TEXT_SECONDARY};
                border: none;
                font-size: 16pt;
                font-weight: bold;
                border-radius: 12px;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.ERROR};
                color: #FFFFFF;
            }}
        """)
        self.remove_btn.clicked.connect(lambda: self.removeClicked.emit(self.filter_rule))
        layout.addWidget(self.remove_btn)

        self._update_style(hovered=False)

    def _get_rule_icon(self) -> str:
        """Get icon emoji based on rule type."""
        if isinstance(self.filter_rule, NumericFilter):
            return "🔢"
        elif isinstance(self.filter_rule, TextFilter):
            return "📝"
        elif isinstance(self.filter_rule, DateFilter):
            return "📅"
        return "📌"

    def _update_style(self, hovered: bool):
        """Update style based on hover state."""
        if hovered:
            self.setStyleSheet(f"""
                ModernFilterChip {{
                    background-color: {AppTheme.PRIMARY};
                    border: 1px solid {AppTheme.PRIMARY_DARK};
                    border-radius: 6px;
                }}
            """)
            self.text_label.setStyleSheet(f"""
                color: #FFFFFF;
                font-weight: 600;
                font-size: 9pt;
                background: transparent;
                border: none;
            """)
        else:
            self.setStyleSheet(f"""
                ModernFilterChip {{
                    background-color: {AppTheme.PRIMARY_LIGHT};
                    border: 1px solid {AppTheme.PRIMARY};
                    border-radius: 6px;
                }}
            """)
            self.text_label.setStyleSheet(f"""
                color: {AppTheme.TEXT};
                font-weight: 500;
                font-size: 9pt;
                background: transparent;
                border: none;
            """)

    def enterEvent(self, event):
        """Handle mouse enter."""
        self._hovered = True
        self._update_style(hovered=True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave."""
        self._hovered = False
        self._update_style(hovered=False)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Handle click."""
        if event.button() == Qt.LeftButton:
            self.editClicked.emit(self.filter_rule)
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        """Show context menu."""
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {AppTheme.BACKGROUND};
                color: {AppTheme.TEXT};
                border: 2px solid {AppTheme.BORDER};
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 8px 20px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {AppTheme.PRIMARY};
                color: #FFFFFF;
            }}
        """)

        edit_action = menu.addAction("✏️ Edit Rule")
        edit_action.triggered.connect(lambda: self.editClicked.emit(self.filter_rule))

        tab_action = menu.addAction("📂 Open in New Tab")
        tab_action.triggered.connect(lambda: self.tabRequested.emit(self.filter_rule))

        menu.addSeparator()

        remove_action = menu.addAction("🗑️ Remove Rule")
        remove_action.triggered.connect(lambda: self.removeClicked.emit(self.filter_rule))

        menu.exec_(event.globalPos())


class ModernFilterPanel(QWidget):
    """Modern filter panel - clean, efficient, intuitive."""

    filterAdded = pyqtSignal(object)
    filterRemoved = pyqtSignal(object)
    filterEdited = pyqtSignal(object, object)
    allFiltersCleared = pyqtSignal()
    filterModeChanged = pyqtSignal(str)
    ruleTabRequested = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_filters: List[FilterRule] = []
        self._setup_ui()

    def _setup_ui(self):
        """Create modern filter panel."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setObjectName("FilterPanelHeader")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 16, 16, 12)
        header_layout.setSpacing(8)

        # Title
        title = QLabel("⚙️ Filter Rules")
        title.setStyleSheet(f"color: {AppTheme.TEXT}; font-size: 13pt; font-weight: 700;")
        header_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Apply rules to filter data")
        subtitle.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY}; font-size: 9pt;")
        subtitle.setWordWrap(True)
        header_layout.addWidget(subtitle)

        header.setStyleSheet(f"""
            #FilterPanelHeader {{
                background-color: {AppTheme.PRIMARY_LIGHT};
                border-bottom: 2px solid {AppTheme.PRIMARY};
            }}
        """)
        layout.addWidget(header)

        # Control bar
        control_bar = QFrame()
        control_layout = QHBoxLayout(control_bar)
        control_layout.setContentsMargins(12, 10, 12, 10)
        control_layout.setSpacing(8)

        # Add filter button - prominent
        self.add_btn = QPushButton("➕ Add Rule")
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {AppTheme.PRIMARY};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: 700;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.PRIMARY_DARK};
            }}
            QPushButton:pressed {{
                background-color: {AppTheme.PRIMARY_HOVER};
            }}
        """)
        control_layout.addWidget(self.add_btn, 1)

        # Clear all button - secondary
        self.clear_btn = QPushButton("✕")
        self.clear_btn.setFixedWidth(40)
        self.clear_btn.setToolTip("Clear all filters")
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {AppTheme.ERROR};
                border: 2px solid {AppTheme.ERROR};
                border-radius: 6px;
                padding: 8px;
                font-weight: 700;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.ERROR};
                color: #FFFFFF;
            }}
        """)
        self.clear_btn.clicked.connect(self.allFiltersCleared.emit)
        control_layout.addWidget(self.clear_btn)

        control_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {AppTheme.SURFACE};
                border-bottom: 1px solid {AppTheme.BORDER};
            }}
        """)
        layout.addWidget(control_bar)

        # Mode selector
        mode_bar = QFrame()
        mode_layout = QHBoxLayout(mode_bar)
        mode_layout.setContentsMargins(12, 8, 12, 8)
        mode_layout.setSpacing(8)

        mode_label = QLabel("Combine:")
        mode_label.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY}; font-size: 9pt; font-weight: 600;")
        mode_layout.addWidget(mode_label)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("ALL (AND)", "all")
        self.mode_combo.addItem("ANY (OR)", "any")
        self.mode_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 6px 10px;
                font-size: 9pt;
                font-weight: 600;
                color: {AppTheme.TEXT};
                background-color: {AppTheme.BACKGROUND};
                border: 1px solid {AppTheme.BORDER};
                border-radius: 4px;
            }}
        """)
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self.mode_combo, 1)

        mode_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {AppTheme.BACKGROUND};
                border-bottom: 1px solid {AppTheme.BORDER};
            }}
        """)
        layout.addWidget(mode_bar)

        # Filters scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {AppTheme.BACKGROUND};
                border: none;
            }}
        """)

        self.filters_container = QWidget()
        self.filters_layout = QVBoxLayout(self.filters_container)
        self.filters_layout.setContentsMargins(12, 12, 12, 12)
        self.filters_layout.setSpacing(8)
        self.filters_layout.setAlignment(Qt.AlignTop)

        # Empty state
        self.empty_label = QLabel("No active filters\n\nClick '➕ Add Rule' to start")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet(f"""
            color: {AppTheme.TEXT_SECONDARY};
            font-size: 10pt;
            padding: 40px 20px;
        """)
        self.filters_layout.addWidget(self.empty_label)

        self.scroll_area.setWidget(self.filters_container)
        layout.addWidget(self.scroll_area, 1)

        # Stats footer
        self.stats_label = QLabel("0 rules active")
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setStyleSheet(f"""
            background-color: {AppTheme.SURFACE};
            color: {AppTheme.TEXT_SECONDARY};
            font-size: 9pt;
            font-weight: 600;
            padding: 10px;
            border-top: 2px solid {AppTheme.BORDER};
        """)
        layout.addWidget(self.stats_label)

    def add_filter(self, filter_rule: FilterRule):
        """Add a filter chip."""
        if self.empty_label.isVisible():
            self.empty_label.hide()

        chip = ModernFilterChip(filter_rule)
        chip.removeClicked.connect(self._on_remove_filter)
        chip.editClicked.connect(self._on_edit_filter)
        chip.tabRequested.connect(self.ruleTabRequested.emit)

        self.filters_layout.addWidget(chip)
        self.active_filters.append(filter_rule)
        self._update_stats()

    def remove_filter(self, filter_rule: FilterRule):
        """Remove a filter chip."""
        for i in range(self.filters_layout.count()):
            widget = self.filters_layout.itemAt(i).widget()
            if isinstance(widget, ModernFilterChip) and widget.filter_rule == filter_rule:
                widget.deleteLater()
                self.active_filters.remove(filter_rule)
                break

        if not self.active_filters:
            self.empty_label.show()

        self._update_stats()

    def clear_all_filters(self):
        """Clear all filter chips."""
        while self.filters_layout.count() > 0:
            item = self.filters_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.active_filters.clear()
        self.empty_label.show()
        self._update_stats()

    def _on_remove_filter(self, filter_rule):
        """Handle remove filter signal."""
        self.remove_filter(filter_rule)
        self.filterRemoved.emit(filter_rule)

    def _on_edit_filter(self, filter_rule):
        """Handle edit filter signal."""
        self.filterEdited.emit(filter_rule, filter_rule)

    def _on_mode_changed(self):
        """Handle mode change."""
        mode = self.mode_combo.currentData()
        self.filterModeChanged.emit(mode)

    def _update_stats(self):
        """Update statistics display."""
        count = len(self.active_filters)
        if count == 0:
            self.stats_label.setText("No rules active")
        elif count == 1:
            self.stats_label.setText("1 rule active")
        else:
            self.stats_label.setText(f"{count} rules active")

    def get_current_mode(self) -> str:
        """Get current filter mode."""
        return self.mode_combo.currentData() or "all"

    def get_filter_mode(self) -> str:
        """Get current filter mode (alias for compatibility)."""
        return self.get_current_mode()

    def set_mode(self, mode: str):
        """Set filter mode."""
        for i in range(self.mode_combo.count()):
            if self.mode_combo.itemData(i) == mode:
                self.mode_combo.setCurrentIndex(i)
                break

    def set_filter_mode(self, mode: str):
        """Set filter mode (alias for compatibility)."""
        self.set_mode(mode)

    def clear_all_chips(self):
        """Clear all filter chips (alias for compatibility)."""
        self.clear_all_filters()
