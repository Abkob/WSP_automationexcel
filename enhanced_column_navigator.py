"""
Smart Column Navigator - Ergonomic slider with minimap and quick actions.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QPushButton, QComboBox, QToolButton, QMenu, QSizePolicy,
    QToolTip, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QSize, QPoint, QTimer
from PyQt5.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush, QLinearGradient,
    QFontMetrics, QPainterPath, QCursor
)
from typing import List, Dict, Set, Optional
from styles import AppTheme


class ColumnMinimap(QWidget):
    """Compact minimap slider showing all columns with smart interaction."""

    columnClicked = pyqtSignal(int)  # column_index
    columnHovered = pyqtSignal(int, str)  # column_index, column_name

    def __init__(self, parent=None):
        super().__init__(parent)

        self.columns: List[str] = []
        self.column_types: Dict[str, str] = {}
        self.filtered_columns: Set[str] = set()
        self.current_column: int = -1
        self.hovered_column: int = -1
        self.visible_range: tuple = (0, 10)  # Start, end visible columns

        self.setMinimumHeight(32)
        self.setMaximumHeight(32)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMouseTracking(True)
        self.setCursor(Qt.PointingHandCursor)

        # Colors
        self.color_numeric = QColor(AppTheme.PRIMARY)
        self.color_date = QColor(AppTheme.INFO)
        self.color_text = QColor(AppTheme.SUCCESS)
        self.color_filtered = QColor(AppTheme.WARNING)
        self.color_current = QColor(AppTheme.ERROR)

    def set_data(self, columns: List[str], column_types: Dict[str, str],
                 filtered_columns: Set[str]):
        """Update minimap data."""
        self.columns = columns
        self.column_types = column_types
        self.filtered_columns = filtered_columns
        self.update()

    def set_current_column(self, idx: int):
        """Set current column indicator."""
        self.current_column = idx
        self.update()

    def set_visible_range(self, start: int, end: int):
        """Set the visible column range (for viewport indicator)."""
        self.visible_range = (start, end)
        self.update()

    def _get_column_color(self, col_name: str) -> QColor:
        """Get color for a column."""
        if col_name in self.filtered_columns:
            return self.color_filtered
        col_type = self.column_types.get(col_name, "text")
        if col_type == "numeric":
            return self.color_numeric
        elif col_type == "date":
            return self.color_date
        return self.color_text

    def _column_at_pos(self, x: int) -> int:
        """Get column index at x position."""
        if not self.columns:
            return -1

        total_width = self.width() - 8  # Padding
        col_width = total_width / len(self.columns)
        idx = int((x - 4) / col_width)
        return max(0, min(idx, len(self.columns) - 1))

    def paintEvent(self, event):
        """Paint the minimap."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        padding = 4
        track_height = rect.height() - padding * 2
        track_rect = QRect(padding, padding, rect.width() - padding * 2, track_height)

        # Draw track background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(AppTheme.SURFACE))
        painter.drawRoundedRect(track_rect, 4, 4)

        if not self.columns:
            # Empty state
            painter.setPen(QColor(AppTheme.TEXT_SECONDARY))
            painter.drawText(track_rect, Qt.AlignCenter, "No columns")
            return

        # Draw column bars
        col_count = len(self.columns)
        bar_width = max(2, (track_rect.width() - col_count + 1) / col_count)
        spacing = 1 if col_count > 50 else 2

        for i, col_name in enumerate(self.columns):
            x = track_rect.left() + i * (bar_width + spacing)
            color = self._get_column_color(col_name)

            # Highlight hovered
            if i == self.hovered_column:
                color = color.lighter(130)
                bar_rect = QRect(int(x), track_rect.top(), int(bar_width) + 1, track_height)
            else:
                bar_rect = QRect(int(x), track_rect.top() + 2, int(bar_width), track_height - 4)

            painter.setBrush(color)
            painter.drawRoundedRect(bar_rect, 2, 2)

        # Draw current column indicator
        if 0 <= self.current_column < col_count:
            x = track_rect.left() + self.current_column * (bar_width + spacing)
            indicator_rect = QRect(int(x) - 1, track_rect.top() - 2, int(bar_width) + 3, track_height + 4)

            painter.setPen(QPen(QColor(AppTheme.TEXT), 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(indicator_rect, 3, 3)

        # Draw visible range overlay
        if self.visible_range[0] >= 0 and self.visible_range[1] > self.visible_range[0]:
            start_x = track_rect.left() + self.visible_range[0] * (bar_width + spacing)
            end_x = track_rect.left() + min(self.visible_range[1], col_count) * (bar_width + spacing)

            viewport_rect = QRect(int(start_x) - 2, track_rect.top() - 1,
                                  int(end_x - start_x) + 4, track_height + 2)

            painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
            painter.setBrush(QColor(255, 255, 255, 30))
            painter.drawRoundedRect(viewport_rect, 3, 3)

    def mouseMoveEvent(self, event):
        """Handle mouse move for hover."""
        col_idx = self._column_at_pos(event.x())
        if col_idx != self.hovered_column:
            self.hovered_column = col_idx
            self.update()

            if 0 <= col_idx < len(self.columns):
                col_name = self.columns[col_idx]
                col_type = self.column_types.get(col_name, "text")
                is_filtered = "Yes" if col_name in self.filtered_columns else "No"

                tooltip = f"<b>{col_name}</b><br>Type: {col_type.title()}<br>Filtered: {is_filtered}<br>Index: {col_idx}"
                QToolTip.showText(event.globalPos(), tooltip, self)
                self.columnHovered.emit(col_idx, col_name)

    def mousePressEvent(self, event):
        """Handle click to select column."""
        if event.button() == Qt.LeftButton:
            col_idx = self._column_at_pos(event.x())
            if 0 <= col_idx < len(self.columns):
                self.current_column = col_idx
                self.update()
                self.columnClicked.emit(col_idx)

    def leaveEvent(self, event):
        """Clear hover on leave."""
        self.hovered_column = -1
        self.update()


class QuickFilterButton(QToolButton):
    """Quick filter button for column types."""

    def __init__(self, text: str, color: QColor, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setCheckable(True)
        self.base_color = color
        self._update_style()

    def _update_style(self):
        checked = self.isChecked()
        self.setStyleSheet(f"""
            QToolButton {{
                background-color: {self.base_color.name() if checked else AppTheme.SURFACE};
                color: {"#FFFFFF" if checked else AppTheme.TEXT};
                border: 1px solid {self.base_color.darker(110).name()};
                border-radius: 10px;
                padding: 3px 8px;
                font-size: 9pt;
                font-weight: 600;
            }}
            QToolButton:hover {{
                background-color: {self.base_color.lighter(110).name()};
                color: #FFFFFF;
            }}
        """)

    def setChecked(self, checked):
        super().setChecked(checked)
        self._update_style()


class EnhancedColumnNavigator(QWidget):
    """Smart column navigator with ergonomic slider design."""

    columnSelected = pyqtSignal(int)  # column_index

    def __init__(self, parent=None):
        super().__init__(parent)

        self.columns: List[str] = []
        self.column_types: Dict[str, str] = {}
        self.filtered_columns: Set[str] = set()
        self._type_filters: Set[str] = {"numeric", "date", "text"}  # All enabled by default
        self._show_filtered_only = False

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._setup_ui()

    def _setup_ui(self):
        """Setup compact UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)

        # Top row: Title + Stats + Quick Jump
        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        # Compact title with icon
        title = QLabel("Columns")
        title.setStyleSheet(f"""
            font-size: 10pt;
            font-weight: 700;
            color: {AppTheme.TEXT};
        """)
        top_row.addWidget(title)

        # Column count badge
        self.count_badge = QLabel("0")
        self.count_badge.setStyleSheet(f"""
            background-color: {AppTheme.PRIMARY};
            color: #FFFFFF;
            border-radius: 8px;
            padding: 2px 6px;
            font-size: 9pt;
            font-weight: 700;
        """)
        self.count_badge.setFixedHeight(18)
        top_row.addWidget(self.count_badge)

        # Filtered indicator
        self.filtered_badge = QLabel("0 filtered")
        self.filtered_badge.setStyleSheet(f"""
            color: {AppTheme.WARNING};
            font-size: 9pt;
            font-weight: 600;
        """)
        self.filtered_badge.hide()
        top_row.addWidget(self.filtered_badge)

        top_row.addStretch()

        # Type filter buttons
        type_frame = QFrame()
        type_layout = QHBoxLayout(type_frame)
        type_layout.setContentsMargins(0, 0, 0, 0)
        type_layout.setSpacing(4)

        self.btn_numeric = QuickFilterButton("123", QColor(AppTheme.PRIMARY))
        self.btn_numeric.setToolTip("Numeric columns")
        self.btn_numeric.setChecked(True)
        self.btn_numeric.toggled.connect(lambda: self._on_type_filter("numeric"))
        type_layout.addWidget(self.btn_numeric)

        self.btn_date = QuickFilterButton("Date", QColor(AppTheme.INFO))
        self.btn_date.setToolTip("Date columns")
        self.btn_date.setChecked(True)
        self.btn_date.toggled.connect(lambda: self._on_type_filter("date"))
        type_layout.addWidget(self.btn_date)

        self.btn_text = QuickFilterButton("Abc", QColor(AppTheme.SUCCESS))
        self.btn_text.setToolTip("Text columns")
        self.btn_text.setChecked(True)
        self.btn_text.toggled.connect(lambda: self._on_type_filter("text"))
        type_layout.addWidget(self.btn_text)

        # Filtered only toggle
        self.btn_filtered = QuickFilterButton("Filtered", QColor(AppTheme.WARNING))
        self.btn_filtered.setToolTip("Show only filtered columns")
        self.btn_filtered.setChecked(False)
        self.btn_filtered.toggled.connect(self._on_filtered_toggle)
        type_layout.addWidget(self.btn_filtered)

        top_row.addWidget(type_frame)

        # Quick jump dropdown
        self.jump_combo = QComboBox()
        self.jump_combo.setMinimumWidth(180)
        self.jump_combo.setMaximumWidth(250)
        self.jump_combo.setPlaceholderText("Jump to column...")
        self.jump_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 4px 8px;
                font-size: 9pt;
                color: {AppTheme.TEXT};
                background-color: {AppTheme.SURFACE};
                border: 1px solid {AppTheme.BORDER};
                border-radius: 4px;
            }}
            QComboBox:hover {{
                border-color: {AppTheme.PRIMARY};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
        """)
        self.jump_combo.currentIndexChanged.connect(self._on_jump_selected)
        top_row.addWidget(self.jump_combo)

        # Navigation buttons
        nav_frame = QFrame()
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(2)

        self.btn_first = QToolButton()
        self.btn_first.setText("<<")
        self.btn_first.setToolTip("First column")
        self.btn_first.clicked.connect(self._go_first)
        self._style_nav_button(self.btn_first)
        nav_layout.addWidget(self.btn_first)

        self.btn_prev = QToolButton()
        self.btn_prev.setText("<")
        self.btn_prev.setToolTip("Previous column")
        self.btn_prev.clicked.connect(self._go_prev)
        self._style_nav_button(self.btn_prev)
        nav_layout.addWidget(self.btn_prev)

        self.btn_next = QToolButton()
        self.btn_next.setText(">")
        self.btn_next.setToolTip("Next column")
        self.btn_next.clicked.connect(self._go_next)
        self._style_nav_button(self.btn_next)
        nav_layout.addWidget(self.btn_next)

        self.btn_last = QToolButton()
        self.btn_last.setText(">>")
        self.btn_last.setToolTip("Last column")
        self.btn_last.clicked.connect(self._go_last)
        self._style_nav_button(self.btn_last)
        nav_layout.addWidget(self.btn_last)

        top_row.addWidget(nav_frame)

        layout.addLayout(top_row)

        # Minimap slider
        self.minimap = ColumnMinimap()
        self.minimap.columnClicked.connect(self._on_minimap_click)
        layout.addWidget(self.minimap)

        # Info label (shows on hover)
        self.info_label = QLabel("")
        self.info_label.setStyleSheet(f"""
            color: {AppTheme.TEXT_SECONDARY};
            font-size: 9pt;
            padding: 2px 0;
        """)
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        self.minimap.columnHovered.connect(self._on_column_hover)

    def _style_nav_button(self, btn: QToolButton):
        """Style navigation button."""
        btn.setFixedSize(24, 24)
        btn.setStyleSheet(f"""
            QToolButton {{
                background-color: {AppTheme.SURFACE};
                color: {AppTheme.TEXT};
                border: 1px solid {AppTheme.BORDER};
                border-radius: 4px;
                font-weight: 700;
            }}
            QToolButton:hover {{
                background-color: {AppTheme.PRIMARY};
                color: #FFFFFF;
                border-color: {AppTheme.PRIMARY};
            }}
            QToolButton:pressed {{
                background-color: {AppTheme.PRIMARY_DARK};
            }}
        """)

    def set_columns(self, columns: List[str], column_types: Dict[str, str] = None,
                    filtered_columns: Set[str] = None):
        """Update navigator with column data."""
        self.columns = columns or []
        self.column_types = column_types or {}
        self.filtered_columns = filtered_columns or set()

        self._update_display()

    def _update_display(self):
        """Update all display elements."""
        # Apply type filters
        filtered_cols = []
        filtered_types = {}
        filtered_set = set()

        for col in self.columns:
            col_type = self.column_types.get(col, "text")
            is_filtered = col in self.filtered_columns

            # Type filter
            if col_type not in self._type_filters:
                continue

            # Filtered only filter
            if self._show_filtered_only and not is_filtered:
                continue

            filtered_cols.append(col)
            filtered_types[col] = col_type
            if is_filtered:
                filtered_set.add(col)

        # Update minimap
        self.minimap.set_data(filtered_cols, filtered_types, filtered_set)

        # Update jump combo
        self.jump_combo.blockSignals(True)
        self.jump_combo.clear()
        for i, col in enumerate(filtered_cols):
            col_type = filtered_types.get(col, "text")
            icon = {"numeric": "123", "date": "Dt", "text": "Abc"}.get(col_type, "?")
            self.jump_combo.addItem(f"[{icon}] {col}", i)
        self.jump_combo.setCurrentIndex(-1)
        self.jump_combo.blockSignals(False)

        # Update badges
        self.count_badge.setText(str(len(filtered_cols)))

        filtered_count = len(self.filtered_columns)
        if filtered_count > 0:
            self.filtered_badge.setText(f"{filtered_count} filtered")
            self.filtered_badge.show()
        else:
            self.filtered_badge.hide()

        # Update info
        total = len(self.columns)
        showing = len(filtered_cols)
        if showing < total:
            self.info_label.setText(f"Showing {showing} of {total} columns")
        else:
            self.info_label.setText(f"{total} columns total")

    def _on_type_filter(self, col_type: str):
        """Handle type filter toggle."""
        btn_map = {
            "numeric": self.btn_numeric,
            "date": self.btn_date,
            "text": self.btn_text
        }

        btn = btn_map.get(col_type)
        if btn and btn.isChecked():
            self._type_filters.add(col_type)
        else:
            self._type_filters.discard(col_type)

        self._update_display()

    def _on_filtered_toggle(self, checked: bool):
        """Handle filtered-only toggle."""
        self._show_filtered_only = checked
        self._update_display()

    def _on_jump_selected(self, index: int):
        """Handle jump combo selection."""
        if index >= 0:
            # Get actual column index from the filtered list
            col_name = self.jump_combo.currentText()
            # Extract column name (remove prefix)
            if "] " in col_name:
                col_name = col_name.split("] ", 1)[1]

            # Find original index
            try:
                orig_idx = self.columns.index(col_name)
                self.minimap.set_current_column(index)
                self.columnSelected.emit(orig_idx)
            except ValueError:
                pass

    def _on_minimap_click(self, idx: int):
        """Handle minimap click."""
        # idx is in filtered list, need to map to original
        filtered_cols = self._get_filtered_columns()
        if 0 <= idx < len(filtered_cols):
            col_name = filtered_cols[idx]
            try:
                orig_idx = self.columns.index(col_name)
                self.columnSelected.emit(orig_idx)
            except ValueError:
                pass

    def _on_column_hover(self, idx: int, col_name: str):
        """Handle column hover."""
        col_type = self.column_types.get(col_name, "text")
        is_filtered = col_name in self.filtered_columns
        status = " [FILTERED]" if is_filtered else ""
        self.info_label.setText(f"{col_name} ({col_type}){status}")

    def _get_filtered_columns(self) -> List[str]:
        """Get currently filtered column list."""
        result = []
        for col in self.columns:
            col_type = self.column_types.get(col, "text")
            is_filtered = col in self.filtered_columns

            if col_type not in self._type_filters:
                continue
            if self._show_filtered_only and not is_filtered:
                continue

            result.append(col)
        return result

    def _go_first(self):
        """Navigate to first column."""
        filtered = self._get_filtered_columns()
        if filtered:
            col_name = filtered[0]
            try:
                orig_idx = self.columns.index(col_name)
                self.minimap.set_current_column(0)
                self.columnSelected.emit(orig_idx)
            except ValueError:
                pass

    def _go_last(self):
        """Navigate to last column."""
        filtered = self._get_filtered_columns()
        if filtered:
            col_name = filtered[-1]
            try:
                orig_idx = self.columns.index(col_name)
                self.minimap.set_current_column(len(filtered) - 1)
                self.columnSelected.emit(orig_idx)
            except ValueError:
                pass

    def _go_prev(self):
        """Navigate to previous column."""
        current = self.minimap.current_column
        if current > 0:
            filtered = self._get_filtered_columns()
            new_idx = current - 1
            if 0 <= new_idx < len(filtered):
                col_name = filtered[new_idx]
                try:
                    orig_idx = self.columns.index(col_name)
                    self.minimap.set_current_column(new_idx)
                    self.columnSelected.emit(orig_idx)
                except ValueError:
                    pass

    def _go_next(self):
        """Navigate to next column."""
        current = self.minimap.current_column
        filtered = self._get_filtered_columns()
        new_idx = current + 1
        if 0 <= new_idx < len(filtered):
            col_name = filtered[new_idx]
            try:
                orig_idx = self.columns.index(col_name)
                self.minimap.set_current_column(new_idx)
                self.columnSelected.emit(orig_idx)
            except ValueError:
                pass

    def highlight_column(self, col_idx: int):
        """Highlight a specific column."""
        if 0 <= col_idx < len(self.columns):
            col_name = self.columns[col_idx]
            filtered = self._get_filtered_columns()
            try:
                filtered_idx = filtered.index(col_name)
                self.minimap.set_current_column(filtered_idx)

                # Update combo
                self.jump_combo.blockSignals(True)
                self.jump_combo.setCurrentIndex(filtered_idx)
                self.jump_combo.blockSignals(False)
            except ValueError:
                pass

    def sizeHint(self) -> QSize:
        return QSize(800, 85)

    def minimumSizeHint(self) -> QSize:
        return QSize(400, 85)
