"""
Design Document Compliant Styling - Professional, accessible, high-contrast.
Colors match specification exactly.
"""

from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication


class AppTheme:
    """Design document compliant color scheme."""
    
    # Primary colors - EXACT from design document
    PRIMARY = "#2563EB"          # Blue
    PRIMARY_DARK = "#1D4ED8"     # Darker blue  
    PRIMARY_HOVER = "#1E40AF"    # Pressed blue
    PRIMARY_LIGHT = "#DBEAFE"    # Light blue
    
    # Semantic colors - EXACT from design document
    SUCCESS = "#10B981"          # Green
    WARNING = "#F59E0B"          # Orange/Amber
    ERROR = "#EF4444"            # Red
    INFO = "#3B82F6"             # Info blue
    
    # Base colors - EXACT from design document
    BACKGROUND = "#FFFFFF"       # Pure white
    SURFACE = "#F9FAFB"          # Very light gray
    TEXT = "#111827"             # Very dark gray (not pure black for accessibility)
    TEXT_SECONDARY = "#6B7280"   # Medium gray
    BORDER = "#D1D5DB"           # Light gray border
    
    # Grays from design document
    GRAY_50 = "#F9FAFB"
    GRAY_100 = "#F3F4F6"
    GRAY_200 = "#E5E7EB"
    GRAY_300 = "#D1D5DB"
    GRAY_400 = "#9CA3AF"
    GRAY_500 = "#6B7280"
    GRAY_600 = "#4B5563"
    GRAY_700 = "#374151"
    GRAY_800 = "#1F2937"
    GRAY_900 = "#111827"
    
    # Filter highlight colors
    FILTER_NUMERIC_HIGH = "#FFE6E6"
    FILTER_NUMERIC_LOW = "#E6FFE6"
    FILTER_NUMERIC_EQ = "#E6E6FF"
    FILTER_TEXT = "#FFFACD"
    FILTER_DATE = "#F0E6FF"
    
    @staticmethod
    def get_stylesheet():
        """Get complete application stylesheet per design document."""
        return """
            /* Main Application */
            QMainWindow {
                background-color: #FFFFFF;
            }
            
            /* Menu Bar */
            QMenuBar {
                background-color: #F9FAFB;
                border-bottom: 2px solid #D1D5DB;
                padding: 4px;
                color: #111827;
                font-size: 10pt;
            }
            QMenuBar::item {
                padding: 8px 16px;
                background: transparent;
                color: #111827;
                font-weight: 500;
            }
            QMenuBar::item:selected {
                background-color: #2563EB;
                color: #FFFFFF;
                border-radius: 4px;
            }
            QMenu {
                background-color: #FFFFFF;
                border: 2px solid #D1D5DB;
                color: #111827;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 32px;
                color: #111827;
            }
            QMenu::item:selected {
                background-color: #2563EB;
                color: #FFFFFF;
                border-radius: 4px;
            }
            QMenu::separator {
                height: 1px;
                background: #E5E7EB;
                margin: 4px 0px;
            }
            
            /* Tabs - Enhanced Modern Design */
            QTabWidget::pane {
                border: 2px solid #D1D5DB;
                background-color: #FFFFFF;
                top: -2px;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #F9FAFB;
                color: #6B7280;
                border: 2px solid #E5E7EB;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 10px 20px;
                margin-right: 2px;
                font-weight: 500;
                font-size: 10pt;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: #2563EB;
                font-weight: 700;
                border: 2px solid #2563EB;
                border-bottom: 2px solid #FFFFFF;
            }
            QTabBar::tab:hover:!selected {
                background-color: #F3F4F6;
                color: #374151;
                border-color: #9CA3AF;
            }
            QTabBar::tab:!selected {
                margin-top: 3px;
            }
            
            /* Primary Buttons */
            QPushButton {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 11pt;
                min-height: 36px;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
            QPushButton:disabled {
                background-color: #D1D5DB;
                color: #9CA3AF;
            }
            
            /* Input Fields */
            QLineEdit {
                border: 2px solid #D1D5DB;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: #FFFFFF;
                color: #111827;
                font-size: 10pt;
                min-height: 36px;
            }
            QLineEdit:focus {
                border: 2px solid #2563EB;
                outline: none;
            }
            QLineEdit::placeholder {
                color: #9CA3AF;
            }
            
            /* Combo Boxes */
            QComboBox {
                border: 2px solid #D1D5DB;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: #FFFFFF;
                color: #111827;
                font-size: 10pt;
                min-height: 36px;
            }
            QComboBox:focus {
                border: 2px solid #2563EB;
            }
            QComboBox:hover {
                border: 2px solid #9CA3AF;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid #111827;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #111827;
                selection-background-color: #2563EB;
                selection-color: #FFFFFF;
                border: 2px solid #D1D5DB;
                border-radius: 6px;
                padding: 4px;
            }
            
            /* Status Bar */
            QStatusBar {
                background-color: #F9FAFB;
                border-top: 2px solid #D1D5DB;
                color: #111827;
                font-weight: 500;
                padding: 4px 8px;
            }
            
            /* Dock Widgets */
            QDockWidget {
                color: #111827;
                font-weight: 600;
            }
            QDockWidget::title {
                background-color: #F9FAFB;
                padding: 8px;
                border-bottom: 2px solid #D1D5DB;
                color: #111827;
                font-weight: 600;
            }
            
            /* Labels */
            QLabel {
                color: #111827;
            }
            
            /* Group Boxes */
            QGroupBox {
                border: 2px solid #D1D5DB;
                border-radius: 6px;
                margin-top: 16px;
                padding-top: 16px;
                font-weight: 600;
                color: #111827;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 8px;
                background-color: #FFFFFF;
            }
            
            /* Scroll Bars */
            QScrollBar:vertical {
                border: 1px solid #D1D5DB;
                background: #F9FAFB;
                width: 16px;
                border-radius: 8px;
            }
            QScrollBar::handle:vertical {
                background: #D1D5DB;
                min-height: 20px;
                border-radius: 7px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9CA3AF;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                border: 1px solid #D1D5DB;
                background: #F9FAFB;
                height: 16px;
                border-radius: 8px;
            }
            QScrollBar::handle:horizontal {
                background: #D1D5DB;
                min-width: 20px;
                border-radius: 7px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #9CA3AF;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            
            /* Spin Boxes */
            QSpinBox, QDoubleSpinBox {
                border: 2px solid #D1D5DB;
                border-radius: 6px;
                padding: 6px;
                background-color: #FFFFFF;
                color: #111827;
            }
            QSpinBox:focus, QDoubleSpinBox:focus {
                border: 2px solid #2563EB;
            }
            
            /* Text Edits */
            QTextEdit {
                border: 2px solid #D1D5DB;
                border-radius: 6px;
                padding: 8px;
                background-color: #FFFFFF;
                color: #111827;
            }
            QTextEdit:focus {
                border: 2px solid #2563EB;
            }
            
            /* List Widgets */
            QListWidget {
                border: 2px solid #D1D5DB;
                background-color: #FFFFFF;
                color: #111827;
                border-radius: 6px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #E5E7EB;
            }
            QListWidget::item:selected {
                background-color: #2563EB;
                color: #FFFFFF;
            }
            QListWidget::item:hover {
                background-color: #F3F4F6;
            }
            
            /* Table Views */
            QTableView {
                gridline-color: #E5E7EB;
                background-color: #FFFFFF;
                selection-background-color: #2563EB;
                selection-color: #FFFFFF;
                color: #111827;
                border: 2px solid #D1D5DB;
                border-radius: 6px;
            }
            QTableView::item {
                padding: 6px;
            }
            QTableView::item:hover {
                background-color: #F3F4F6;
            }
            
            /* Table Headers */
            QHeaderView::section {
                background-color: #F9FAFB;
                color: #111827;
                padding: 8px 12px;
                border: 1px solid #D1D5DB;
                border-bottom: 2px solid #D1D5DB;
                font-weight: 600;
                font-size: 10pt;
            }
            QHeaderView::section:hover {
                background-color: #F3F4F6;
            }
            QHeaderView::section:pressed {
                background-color: #E5E7EB;
            }
            
            /* Dialogs */
            QDialog {
                background-color: #FFFFFF;
            }
            
            /* Tool Tips */
            QToolTip {
                background-color: #111827;
                color: #FFFFFF;
                border: 1px solid #374151;
                padding: 6px 8px;
                border-radius: 4px;
                font-size: 10pt;
            }
            
            /* Frames */
            QFrame {
                color: #111827;
            }
        """
    
    @staticmethod
    def setup_application_palette(app: QApplication):
        """Setup color palette per design document."""
        palette = QPalette()
        
        # Window colors
        palette.setColor(QPalette.Window, QColor("#FFFFFF"))
        palette.setColor(QPalette.WindowText, QColor("#111827"))
        
        # Base colors (input fields)
        palette.setColor(QPalette.Base, QColor("#FFFFFF"))
        palette.setColor(QPalette.AlternateBase, QColor("#F9FAFB"))
        
        # Text colors
        palette.setColor(QPalette.Text, QColor("#111827"))
        palette.setColor(QPalette.PlaceholderText, QColor("#9CA3AF"))
        
        # Button colors
        palette.setColor(QPalette.Button, QColor("#2563EB"))
        palette.setColor(QPalette.ButtonText, QColor("#FFFFFF"))
        
        # Highlight colors
        palette.setColor(QPalette.Highlight, QColor("#2563EB"))
        palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
        
        # Link colors
        palette.setColor(QPalette.Link, QColor("#2563EB"))
        palette.setColor(QPalette.LinkVisited, QColor("#1D4ED8"))
        
        app.setPalette(palette)
