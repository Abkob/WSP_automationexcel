"""
Enhanced Column Navigator - Much better visualization and interaction.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame,
    QLabel, QPushButton, QComboBox, QLineEdit, QToolTip, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QSize, QRect
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPalette
from typing import List, Dict, Set
from styles import AppTheme


class ColumnBlock(QFrame):
    """Visual block representing a column in the minimap."""
    
    clicked = pyqtSignal(int)  # column_index
    
    def __init__(self, col_name: str, col_index: int, col_type: str, 
                 is_filtered: bool = False, parent=None):
        super().__init__(parent)
        
        self.col_name = col_name
        self.col_index = col_index
        self.col_type = col_type
        self.is_filtered = is_filtered
        self.is_hovered = False
        
        self.setFixedSize(50, 60)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(self._create_tooltip())
        
        self._update_style()
    
    def _create_tooltip(self) -> str:
        """Create detailed tooltip."""
        status = "FILTERED" if self.is_filtered else "Normal"
        return f"""<b>{self.col_name}</b><br>
Type: {self.col_type.title()}<br>
Status: {status}<br>
Index: {self.col_index}<br>
<i>Click to jump to column</i>"""
    
    def _get_color(self) -> QColor:
        """Get color based on column type and status."""
        if self.is_filtered:
            return QColor(AppTheme.WARNING)
        
        if self.col_type == "numeric":
            return QColor(AppTheme.PRIMARY)
        elif self.col_type == "date":
            return QColor(AppTheme.INFO)
        else:
            return QColor(AppTheme.SUCCESS)
    
    def _update_style(self):
        """Update visual style."""
        color = self._get_color()
        
        if self.is_hovered:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {color.lighter(120).name()};
                    border: 3px solid {AppTheme.TEXT};
                    border-radius: 6px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {color.name()};
                    border: 2px solid {color.darker(130).name()};
                    border-radius: 6px;
                }}
            """)
    
    def paintEvent(self, event):
        """Custom paint to show column initial."""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw column initial or icon
        painter.setPen(QPen(Qt.white))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        
        # Get first letter or special indicator
        if self.is_filtered:
            text = "F"
        else:
            text = self.col_name[0].upper() if self.col_name else "?"
        
        # Draw centered text
        rect = self.rect()
        painter.drawText(rect, Qt.AlignCenter, text)
        
        # Draw type indicator at bottom
        painter.setPen(QPen(QColor(255, 255, 255, 200)))
        font_small = QFont()
        font_small.setPointSize(7)
        painter.setFont(font_small)
        
        type_indicators = {
            "numeric": "123",
            "date": "Dt",
            "text": "Abc"
        }
        type_text = type_indicators.get(self.col_type, "?")
        
        bottom_rect = QRect(rect.left(), rect.bottom() - 15, rect.width(), 12)
        painter.drawText(bottom_rect, Qt.AlignCenter, type_text)
    
    def mousePressEvent(self, event):
        """Handle click."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.col_index)
    
    def enterEvent(self, event):
        """Handle hover enter."""
        self.is_hovered = True
        self._update_style()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle hover leave."""
        self.is_hovered = False
        self._update_style()
        super().leaveEvent(event)


class EnhancedColumnNavigator(QWidget):
    """Enhanced column navigator with better visualization."""
    
    columnSelected = pyqtSignal(int)  # column_index
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.columns = []
        self.column_types = {}
        self.filtered_columns = set()
        self.column_blocks = []
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Top bar with title and controls
        top_bar = QHBoxLayout()
        
        # Title
        title_label = QLabel("Column Navigator")
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 11pt;
                font-weight: 600;
                color: {AppTheme.TEXT};
            }}
        """)
        top_bar.addWidget(title_label)
        
        # Column count
        self.count_label = QLabel("0 columns")
        self.count_label.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY}; font-size: 10pt;")
        top_bar.addWidget(self.count_label)
        
        top_bar.addStretch()
        
        # Search box
        search_label = QLabel("Find:")
        search_label.setStyleSheet(f"color: {AppTheme.TEXT}; font-weight: 600;")
        top_bar.addWidget(search_label)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search columns...")
        self.search_box.setMaximumWidth(200)
        self.search_box.textChanged.connect(self._on_search)
        top_bar.addWidget(self.search_box)
        
        # Quick jump combo
        jump_label = QLabel("Jump:")
        jump_label.setStyleSheet(f"color: {AppTheme.TEXT}; font-weight: 600;")
        top_bar.addWidget(jump_label)
        
        self.quick_combo = QComboBox()
        self.quick_combo.setMinimumWidth(200)
        self.quick_combo.currentIndexChanged.connect(self._on_quick_jump)
        top_bar.addWidget(self.quick_combo)
        
        layout.addLayout(top_bar)
        
        # Legend
        legend_layout = QHBoxLayout()
        legend_label = QLabel("Legend:")
        legend_label.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY}; font-size: 9pt;")
        legend_layout.addWidget(legend_label)
        
        legends = [
            ("Numeric", QColor(AppTheme.PRIMARY)),
            ("Date", QColor(AppTheme.INFO)),
            ("Text", QColor(AppTheme.SUCCESS)),
            ("Filtered", QColor(AppTheme.WARNING))
        ]
        
        for label_text, color in legends:
            legend_item = QFrame()
            legend_item.setFixedSize(15, 15)
            legend_item.setStyleSheet(f"""
                QFrame {{
                    background-color: {color.name()};
                    border: 1px solid {color.darker(130).name()};
                    border-radius: 3px;
                }}
            """)
            legend_layout.addWidget(legend_item)
            
            label = QLabel(label_text)
            label.setStyleSheet(f"color: {AppTheme.TEXT_SECONDARY}; font-size: 9pt;")
            legend_layout.addWidget(label)
            legend_layout.addSpacing(10)
        
        legend_layout.addStretch()
        layout.addLayout(legend_layout)
        
        # Minimap scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFixedHeight(90)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {AppTheme.BACKGROUND};
                border: 2px solid {AppTheme.BORDER};
                border-radius: 4px;
            }}
        """)
        
        self.minimap_widget = QWidget()
        self.minimap_layout = QHBoxLayout(self.minimap_widget)
        self.minimap_layout.setContentsMargins(4, 4, 4, 4)
        self.minimap_layout.setSpacing(6)
        self.minimap_layout.setAlignment(Qt.AlignLeft)
        
        self.scroll_area.setWidget(self.minimap_widget)
        layout.addWidget(self.scroll_area)
    
    def set_columns(self, columns: List[str], column_types: Dict[str, str] = None, 
                    filtered_columns: Set[str] = None):
        """Update navigator with column information."""
        self.columns = columns
        self.column_types = column_types or {}
        self.filtered_columns = filtered_columns or set()
        
        # Clear existing blocks
        self.column_blocks.clear()
        while self.minimap_layout.count():
            item = self.minimap_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Update quick combo
        self.quick_combo.blockSignals(True)
        self.quick_combo.clear()
        self.quick_combo.addItems(columns)
        self.quick_combo.blockSignals(False)
        
        # Create blocks for each column
        for idx, col_name in enumerate(columns):
            col_type = self.column_types.get(col_name, "text")
            is_filtered = col_name in self.filtered_columns
            
            block = ColumnBlock(col_name, idx, col_type, is_filtered)
            block.clicked.connect(self._on_block_clicked)
            
            self.minimap_layout.addWidget(block)
            self.column_blocks.append(block)
        
        self.minimap_layout.addStretch()
        
        # Update count
        filtered_count = len(self.filtered_columns)
        if filtered_count > 0:
            self.count_label.setText(f"{len(columns)} columns ({filtered_count} filtered)")
        else:
            self.count_label.setText(f"{len(columns)} columns")
    
    def highlight_column(self, col_idx: int):
        """Visually highlight a column."""
        self.quick_combo.blockSignals(True)
        self.quick_combo.setCurrentIndex(col_idx)
        self.quick_combo.blockSignals(False)
        
        # Scroll to block
        if 0 <= col_idx < len(self.column_blocks):
            block = self.column_blocks[col_idx]
            self.scroll_area.ensureWidgetVisible(block, 50, 0)
    
    def _on_block_clicked(self, col_idx: int):
        """Handle block click."""
        self.columnSelected.emit(col_idx)
        self.highlight_column(col_idx)
    
    def _on_quick_jump(self, index):
        """Handle quick jump combo selection."""
        if index >= 0:
            self.columnSelected.emit(index)
    
    def _on_search(self, text):
        """Handle search text change."""
        text = text.lower()
        
        if not text:
            # Show all
            for block in self.column_blocks:
                block.show()
            return
        
        # Filter blocks
        for block in self.column_blocks:
            if text in block.col_name.lower():
                block.show()
            else:
                block.hide()
    
    def sizeHint(self):
        """Provide size hint."""
        return QSize(800, 140)
    
    def minimumSizeHint(self):
        """Provide minimum size hint."""
        return QSize(400, 140)
