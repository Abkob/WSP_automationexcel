"""
Modern filter panel components.
"""

import os
from typing import List

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from models import DateFilter, FilterRule, NumericFilter, TextFilter
from styles import AppTheme


def _load_panel_logo() -> QPixmap:
    """Load the square app logo for the filter panel header."""
    path = AppTheme.asset_path("logo.png")
    if not os.path.exists(path):
        return QPixmap()

    pixmap = QPixmap(path)
    if pixmap.isNull():
        return QPixmap()

    return pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)


class ModernFilterChip(QFrame):
    """Filter chip with hover state and actions."""

    removeClicked = pyqtSignal(object)
    editClicked = pyqtSignal(object)
    tabRequested = pyqtSignal(object)

    def __init__(self, filter_rule: FilterRule, parent=None):
        super().__init__(parent)
        self.filter_rule = filter_rule
        self._hovered = False
        self._setup_ui()

    def _setup_ui(self):
        self.setFrameStyle(QFrame.NoFrame)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 6, 6)
        layout.setSpacing(6)

        tag_label = QLabel(self._get_rule_tag())
        tag_label.setStyleSheet(
            f"""
            color: {AppTheme.PRIMARY_DARK};
            background-color: {AppTheme.PRIMARY_LIGHT};
            border: 1px solid {AppTheme.PRIMARY};
            border-radius: 3px;
            padding: 1px 5px;
            font-size: 7.5pt;
            font-weight: 600;
            """
        )
        layout.addWidget(tag_label, 0, Qt.AlignVCenter)

        rule_text = str(self.filter_rule)
        self.text_label = QLabel(rule_text)
        self.text_label.setWordWrap(False)
        self.text_label.setToolTip(rule_text)  # Show full text on hover
        self.text_label.setStyleSheet(
            f"""
            color: {AppTheme.TEXT};
            font-weight: 500;
            font-size: 8.5pt;
            background: transparent;
            border: none;
            """
        )
        layout.addWidget(self.text_label, 1, Qt.AlignVCenter)

        self.remove_btn = QPushButton("\u00d7")
        self.remove_btn.setFixedSize(18, 18)
        self.remove_btn.setCursor(Qt.PointingHandCursor)
        self.remove_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {AppTheme.GRAY_200};
                color: {AppTheme.TEXT_SECONDARY};
                border: none;
                font-size: 11pt;
                font-weight: 600;
                border-radius: 9px;
                padding: 0px;
                margin: 0px;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.ERROR};
                color: #FFFFFF;
            }}
            """
        )
        self.remove_btn.clicked.connect(lambda: self.removeClicked.emit(self.filter_rule))
        layout.addWidget(self.remove_btn, 0, Qt.AlignVCenter)

        self._update_style(hovered=False)

    def _get_rule_tag(self) -> str:
        if isinstance(self.filter_rule, NumericFilter):
            return "NUM"
        if isinstance(self.filter_rule, TextFilter):
            return "TXT"
        if isinstance(self.filter_rule, DateFilter):
            return "DATE"
        return "RULE"

    def _update_style(self, hovered: bool):
        if hovered:
            self.setStyleSheet(
                f"""
                ModernFilterChip {{
                    background-color: {AppTheme.PRIMARY_LIGHT};
                    border: 1px solid {AppTheme.PRIMARY};
                    border-radius: 8px;
                }}
                """
            )
            self.text_label.setStyleSheet(
                f"""
                color: {AppTheme.PRIMARY_DARK};
                font-weight: 600;
                font-size: 9.5pt;
                background: transparent;
                border: none;
                """
            )
        else:
            self.setStyleSheet(
                f"""
                ModernFilterChip {{
                    background-color: {AppTheme.BACKGROUND};
                    border: 1px solid {AppTheme.BORDER};
                    border-radius: 8px;
                }}
                """
            )
            self.text_label.setStyleSheet(
                f"""
                color: {AppTheme.TEXT};
                font-weight: 500;
                font-size: 9.5pt;
                background: transparent;
                border: none;
                """
            )

    def enterEvent(self, event):
        self._hovered = True
        self._update_style(hovered=True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self._update_style(hovered=False)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.editClicked.emit(self.filter_rule)
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet(
            f"""
            QMenu {{
                background-color: {AppTheme.BACKGROUND};
                color: {AppTheme.TEXT};
                border: 1px solid {AppTheme.BORDER};
                border-radius: 6px;
                padding: 4px;
            }}
            QMenu::item {{
                padding: 8px 18px;
                border-radius: 4px;
            }}
            QMenu::item:selected {{
                background-color: {AppTheme.PRIMARY};
                color: #FFFFFF;
            }}
            """
        )

        edit_action = menu.addAction("Edit rule")
        edit_action.triggered.connect(lambda: self.editClicked.emit(self.filter_rule))

        tab_action = menu.addAction("Open preview tab")
        tab_action.triggered.connect(lambda: self.tabRequested.emit(self.filter_rule))

        menu.addSeparator()

        remove_action = menu.addAction("Remove rule")
        remove_action.triggered.connect(lambda: self.removeClicked.emit(self.filter_rule))

        menu.exec_(event.globalPos())


class ModernFilterPanel(QWidget):
    """Filter management side panel."""

    filterAdded = pyqtSignal(object)
    filterRemoved = pyqtSignal(object)
    filterEdited = pyqtSignal(object, object)
    allFiltersCleared = pyqtSignal()
    filterModeChanged = pyqtSignal(str)
    ruleTabRequested = pyqtSignal(object)
    collapseToggled = pyqtSignal(bool)
    widthSuggested = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_filters: List[FilterRule] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.header = QFrame()
        self.header.setObjectName("FilterPanelHeader")
        header_layout = QVBoxLayout(self.header)
        header_layout.setContentsMargins(12, 12, 12, 10)
        header_layout.setSpacing(8)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(8)

        self.logo_label = QLabel()
        panel_logo = _load_panel_logo()
        if not panel_logo.isNull():
            self.logo_label.setPixmap(panel_logo)
            self.logo_label.setFixedSize(panel_logo.size())
        else:
            self.logo_label.setText("F")
            self.logo_label.setStyleSheet(f"font-size: 12pt; color: {AppTheme.PRIMARY}; font-weight: 800;")
        title_row.addWidget(self.logo_label, 0, Qt.AlignVCenter)

        self.title_label = QLabel("Rules")
        self.title_label.setStyleSheet(
            f"color: {AppTheme.TEXT}; font-size: 11.5pt; font-weight: 600; font-family: {AppTheme.FONT_UI_BOLD};"
        )
        title_row.addWidget(self.title_label, 1)

        self.collapse_btn = QToolButton()
        self.collapse_btn.setObjectName("FilterPanelCollapse")
        self.collapse_btn.setCheckable(False)
        self.collapse_btn.setText("<")
        self.collapse_btn.setToolTip("Collapse panel")
        self.collapse_btn.setFixedSize(24, 24)
        self.collapse_btn.setStyleSheet(
            f"""
            QToolButton {{
                border: 1px solid {AppTheme.BORDER};
                background-color: {AppTheme.BACKGROUND};
                color: {AppTheme.TEXT};
                border-radius: 4px;
                font-weight: 700;
                font-size: 10pt;
            }}
            QToolButton:hover {{
                background-color: {AppTheme.PRIMARY};
                color: #FFFFFF;
                border-color: {AppTheme.PRIMARY};
            }}
            """
        )
        self.collapse_btn.clicked.connect(self._on_collapse_clicked)
        self.collapse_btn.setVisible(False)
        self._is_collapsed = False
        title_row.addWidget(self.collapse_btn, 0, Qt.AlignRight)

        header_layout.addLayout(title_row)

        self.subtitle_label = QLabel("Add a filter to create a rule tab")
        self.subtitle_label.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY}; font-size: 8.5pt; font-weight: 400;")
        self.subtitle_label.setWordWrap(True)
        header_layout.addWidget(self.subtitle_label)

        self.header.setStyleSheet(
            f"""
            #FilterPanelHeader {{
                background-color: {AppTheme.BACKGROUND};
                border-left: 4px solid {AppTheme.PRIMARY};
                border-bottom: 1px solid {AppTheme.GRAY_200};
            }}
            """
        )
        layout.addWidget(self.header)

        self.control_bar = QFrame()
        control_layout = QHBoxLayout(self.control_bar)
        control_layout.setContentsMargins(12, 10, 12, 10)
        control_layout.setSpacing(8)

        self.add_btn = QPushButton("Create Rule")
        self.add_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {AppTheme.PRIMARY};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px 14px;
                font-weight: 600;
                font-family: {AppTheme.FONT_UI_BOLD};
                font-size: 9.5pt;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.PRIMARY_DARK};
            }}
            QPushButton:pressed {{
                background-color: {AppTheme.PRIMARY_HOVER};
            }}
            """
        )
        control_layout.addWidget(self.add_btn, 1)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFixedWidth(68)
        self.clear_btn.setToolTip("Clear all filters")
        self.clear_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent;
                color: {AppTheme.ERROR};
                border: 1px solid {AppTheme.ERROR};
                border-radius: 8px;
                padding: 8px;
                font-weight: 500;
                font-size: 9pt;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.ERROR};
                color: #FFFFFF;
            }}
            """
        )
        self.clear_btn.clicked.connect(self.allFiltersCleared.emit)
        control_layout.addWidget(self.clear_btn)

        self.control_bar.setStyleSheet(
            f"""
            QFrame {{
                background-color: {AppTheme.BACKGROUND};
                border-bottom: 1px solid {AppTheme.GRAY_200};
            }}
            """
        )
        layout.addWidget(self.control_bar)

        # Mode bar wrapper for proper margins
        mode_wrapper = QWidget()
        mode_wrapper_layout = QVBoxLayout(mode_wrapper)
        mode_wrapper_layout.setContentsMargins(12, 6, 12, 6)
        mode_wrapper_layout.setSpacing(0)

        self.mode_bar = QFrame()
        mode_layout = QHBoxLayout(self.mode_bar)
        mode_layout.setContentsMargins(8, 6, 8, 6)
        mode_layout.setSpacing(6)

        self.mode_label = QLabel("Combine")
        self.mode_label.setStyleSheet(
            f"""
            color: {AppTheme.TEXT_SECONDARY};
            font-size: 8.5pt;
            font-weight: 500;
            background: transparent;
            border: none;
            """
        )
        mode_layout.addWidget(self.mode_label, 0, Qt.AlignVCenter)

        # Segmented control container
        self._segment_container = QFrame()
        segment_layout = QHBoxLayout(self._segment_container)
        segment_layout.setContentsMargins(2, 2, 2, 2)
        segment_layout.setSpacing(0)

        self._mode_all_btn = QPushButton("ALL")
        self._mode_all_btn.setCheckable(True)
        self._mode_all_btn.setChecked(True)
        self._mode_all_btn.setCursor(Qt.PointingHandCursor)
        self._mode_all_btn.clicked.connect(lambda: self._on_segment_clicked("all"))

        self._mode_any_btn = QPushButton("ANY")
        self._mode_any_btn.setCheckable(True)
        self._mode_any_btn.setChecked(False)
        self._mode_any_btn.setCursor(Qt.PointingHandCursor)
        self._mode_any_btn.clicked.connect(lambda: self._on_segment_clicked("any"))

        # Style for segmented buttons
        segment_btn_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {AppTheme.TEXT_SECONDARY};
                border: none;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 8pt;
                font-weight: 600;
                min-width: 40px;
            }}
            QPushButton:hover {{
                background-color: {AppTheme.GRAY_200};
                color: {AppTheme.TEXT};
            }}
            QPushButton:checked {{
                background-color: {AppTheme.PRIMARY};
                color: #FFFFFF;
            }}
            QPushButton:checked:hover {{
                background-color: {AppTheme.PRIMARY_DARK};
            }}
        """
        self._mode_all_btn.setStyleSheet(segment_btn_style)
        self._mode_any_btn.setStyleSheet(segment_btn_style)

        segment_layout.addWidget(self._mode_all_btn)
        segment_layout.addWidget(self._mode_any_btn)

        self._segment_container.setStyleSheet(
            f"""
            QFrame {{
                background-color: {AppTheme.GRAY_100};
                border: 1px solid {AppTheme.GRAY_200};
                border-radius: 6px;
            }}
            """
        )
        mode_layout.addWidget(self._segment_container, 1)

        # Hidden combo for compatibility with existing code
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("ALL (AND)", "all")
        self.mode_combo.addItem("ANY (OR)", "any")
        self.mode_combo.setVisible(False)

        self.mode_bar.setStyleSheet(
            f"""
            QFrame {{
                background-color: {AppTheme.SURFACE};
                border: 1px solid {AppTheme.GRAY_200};
                border-radius: 6px;
            }}
            """
        )
        mode_wrapper_layout.addWidget(self.mode_bar)
        layout.addWidget(mode_wrapper)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet(
            f"""
            QScrollArea {{
                background-color: {AppTheme.BACKGROUND};
                border: none;
            }}
            """
        )

        self.filters_container = QWidget()
        self.filters_layout = QVBoxLayout(self.filters_container)
        self.filters_layout.setContentsMargins(8, 8, 8, 8)
        self.filters_layout.setSpacing(6)
        self.filters_layout.setAlignment(Qt.AlignTop)

        self.empty_label = QLabel("No active rules.\nUse Add Rule to begin.")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet(
            f"""
            color: {AppTheme.TEXT_SECONDARY};
            font-size: 10pt;
            font-weight: 400;
            padding: 36px 16px;
            """
        )
        self.filters_layout.addWidget(self.empty_label)

        self.scroll_area.setWidget(self.filters_container)
        layout.addWidget(self.scroll_area, 1)

        self.stats_label = QLabel("No rules active")
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setStyleSheet(
            f"""
            background-color: {AppTheme.BACKGROUND};
            color: {AppTheme.TEXT_SECONDARY};
            font-size: 9pt;
            font-weight: 400;
            padding: 9px;
            border-top: 1px solid {AppTheme.GRAY_200};
            """
        )
        layout.addWidget(self.stats_label)

        self._update_dynamic_width()

    def add_filter(self, filter_rule: FilterRule):
        if self.empty_label.isVisible():
            self.empty_label.hide()

        chip = ModernFilterChip(filter_rule)
        chip.removeClicked.connect(self._on_remove_filter)
        chip.editClicked.connect(self._on_edit_filter)
        chip.tabRequested.connect(self.ruleTabRequested.emit)

        self.filters_layout.addWidget(chip)
        self.active_filters.append(filter_rule)
        self._update_stats()
        self._update_dynamic_width()

    def remove_filter(self, filter_rule: FilterRule):
        for i in range(self.filters_layout.count()):
            widget = self.filters_layout.itemAt(i).widget()
            if isinstance(widget, ModernFilterChip) and widget.filter_rule == filter_rule:
                widget.deleteLater()
                self.active_filters.remove(filter_rule)
                break

        if not self.active_filters:
            self.empty_label.show()

        self._update_stats()
        self._update_dynamic_width()

    def clear_all_filters(self):
        for i in range(self.filters_layout.count() - 1, -1, -1):
            item = self.filters_layout.itemAt(i)
            widget = item.widget() if item else None
            if widget is None or widget is self.empty_label:
                continue
            self.filters_layout.takeAt(i)
            widget.deleteLater()

        self.active_filters.clear()
        self.empty_label.show()
        self._update_stats()
        self._update_dynamic_width()

    def _on_remove_filter(self, filter_rule):
        self.remove_filter(filter_rule)
        self.filterRemoved.emit(filter_rule)

    def _on_edit_filter(self, filter_rule):
        self.filterEdited.emit(filter_rule, filter_rule)

    def _on_segment_clicked(self, mode: str):
        """Handle segmented control click."""
        if mode == "all":
            self._mode_all_btn.setChecked(True)
            self._mode_any_btn.setChecked(False)
            self.mode_combo.setCurrentIndex(0)
        else:
            self._mode_all_btn.setChecked(False)
            self._mode_any_btn.setChecked(True)
            self.mode_combo.setCurrentIndex(1)
        self.filterModeChanged.emit(mode)

    def _on_mode_changed(self):
        mode = self.mode_combo.currentData()
        self.filterModeChanged.emit(mode)

    def _update_stats(self):
        count = len(self.active_filters)
        if count == 0:
            self.stats_label.setText("No rules active")
        elif count == 1:
            self.stats_label.setText("1 rule active")
        else:
            self.stats_label.setText(f"{count} rules active")

    def _update_dynamic_width(self):
        if getattr(self, "_is_collapsed", False):
            return

        # Calculate content widths with proper minimum
        min_width = 300
        max_width = 470
        padding = 32  # Account for margins and scrollbar

        widths = [min_width]

        # Check filter chips (these are the main content that might need space)
        for i in range(self.filters_layout.count()):
            item = self.filters_layout.itemAt(i)
            if item is None:
                continue
            widget = item.widget()
            if widget is not None and widget.isVisible() and isinstance(widget, ModernFilterChip):
                hint = widget.sizeHint().width()
                if hint > 0:
                    widths.append(hint + padding)

        desired = max(widths) if widths else min_width
        desired = min(max(desired, min_width), max_width)
        self.setMinimumWidth(desired)
        self.widthSuggested.emit(desired)

    def get_current_mode(self) -> str:
        if hasattr(self, "_mode_all_btn") and self._mode_all_btn.isChecked():
            return "all"
        elif hasattr(self, "_mode_any_btn") and self._mode_any_btn.isChecked():
            return "any"
        return self.mode_combo.currentData() or "all"

    def get_filter_mode(self) -> str:
        return self.get_current_mode()

    def set_mode(self, mode: str):
        # Update hidden combo
        self.mode_combo.blockSignals(True)
        try:
            for i in range(self.mode_combo.count()):
                if self.mode_combo.itemData(i) == mode:
                    self.mode_combo.setCurrentIndex(i)
                    break
        finally:
            self.mode_combo.blockSignals(False)

        # Update segmented control
        if hasattr(self, "_mode_all_btn") and hasattr(self, "_mode_any_btn"):
            self._mode_all_btn.setChecked(mode == "all")
            self._mode_any_btn.setChecked(mode == "any")

    def set_filter_mode(self, mode: str):
        self.set_mode(mode)

    def set_mode_enabled(self, enabled: bool):
        self.mode_combo.setEnabled(enabled)
        if hasattr(self, "mode_label"):
            self.mode_label.setEnabled(enabled)
        if hasattr(self, "_mode_all_btn"):
            self._mode_all_btn.setEnabled(enabled)
        if hasattr(self, "_mode_any_btn"):
            self._mode_any_btn.setEnabled(enabled)

    def set_action_controls_visible(self, visible: bool):
        if hasattr(self, "control_bar"):
            self.control_bar.setVisible(visible)

    def set_mode_visible(self, visible: bool):
        if hasattr(self, "mode_bar"):
            self.mode_bar.setVisible(visible)

    def set_collapse_available(self, visible: bool):
        if hasattr(self, "collapse_btn"):
            self.collapse_btn.setVisible(visible)

    def set_collapsed(self, collapsed: bool):
        self._is_collapsed = collapsed
        if hasattr(self, "collapse_btn"):
            self.collapse_btn.setText(">" if collapsed else "<")
            self.collapse_btn.setToolTip("Expand panel" if collapsed else "Collapse panel")

        if hasattr(self, "title_label"):
            self.title_label.setVisible(not collapsed)
        if hasattr(self, "logo_label"):
            self.logo_label.setVisible(not collapsed)

        for widget in [
            getattr(self, "subtitle_label", None),
            getattr(self, "control_bar", None),
            getattr(self, "mode_bar", None),
            getattr(self, "scroll_area", None),
            getattr(self, "stats_label", None),
        ]:
            if widget is not None:
                widget.setVisible(not collapsed)

    def _on_collapse_clicked(self):
        new_state = not getattr(self, "_is_collapsed", False)
        self.collapseToggled.emit(new_state)

    def set_context(self, title: str, subtitle: str):
        if hasattr(self, "title_label") and title is not None:
            self.title_label.setText(title)
        if hasattr(self, "subtitle_label") and subtitle is not None:
            self.subtitle_label.setText(subtitle)
        self._update_dynamic_width()

    def add_filter_chip(self, filter_rule: FilterRule):
        self.add_filter(filter_rule)

    def clear_all_chips(self):
        self.clear_all_filters()
