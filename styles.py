"""
Centralized application styling.
"""

import os
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication


class AppTheme:
    """Brand-aligned color system and shared stylesheet."""

    # AUB primary from guidelines.pdf
    PRIMARY = "#840132"       # Berytus Red
    PRIMARY_DARK = "#640027"
    PRIMARY_HOVER = "#4D001E"
    PRIMARY_LIGHT = "#F5E8EE"

    SUCCESS = "#26613A"
    WARNING = "#C85F00"
    ERROR = "#C85143"
    INFO = "#005E99"

    BACKGROUND = "#FFFFFF"
    SURFACE = "#F6F6F8"
    TEXT = "#111111"
    TEXT_SECONDARY = "#555555"
    BORDER = "#D8D8DD"

    GRAY_50 = "#FAFAFC"
    GRAY_100 = "#F2F2F5"
    GRAY_200 = "#E6E6EB"
    GRAY_300 = "#D8D8DD"
    GRAY_400 = "#BBBBBF"
    GRAY_500 = "#808080"      # exact light gray from guideline
    GRAY_600 = "#6D6D72"
    GRAY_700 = "#4C4C4F"
    GRAY_800 = "#2C2C2E"
    GRAY_900 = "#101012"

    FILTER_NUMERIC_HIGH = "#FBEAED"
    FILTER_NUMERIC_LOW = "#ECF8F2"
    FILTER_NUMERIC_EQ = "#EBF2FA"
    FILTER_TEXT = "#FFF7E9"
    FILTER_DATE = "#F3ECF8"

    # Typography stacks (guideline-aware with robust fallbacks)
    FONT_UI = '"Proxima Nova Rg", "Segoe UI", "Arial"'
    FONT_UI_MEDIUM = '"Proxima Nova Lt", "Proxima Nova Rg", "Segoe UI", "Arial"'
    FONT_UI_BOLD = '"Proxima Nova Th", "Proxima Nova Rg", "Segoe UI", "Arial"'

    @classmethod
    def asset_path(cls, filename: str) -> str:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    @classmethod
    def get_stylesheet(cls):
        """Shared stylesheet for the whole application."""
        return f"""
            QWidget {{
                font-family: {cls.FONT_UI};
                font-size: 9.75pt;
                font-weight: 400;
            }}

            QMainWindow {{
                background-color: {cls.BACKGROUND};
            }}

            QMenuBar {{
                background-color: {cls.BACKGROUND};
                border-bottom: 1px solid {cls.GRAY_200};
                padding: 4px 6px;
                color: {cls.TEXT};
                font-size: 10pt;
                font-family: {cls.FONT_UI_MEDIUM};
            }}
            QMenuBar::item {{
                padding: 8px 14px;
                border-radius: 4px;
                color: {cls.TEXT};
                font-weight: 500;
            }}
            QMenuBar::item:selected {{
                background-color: {cls.PRIMARY_LIGHT};
                color: {cls.PRIMARY_DARK};
                font-family: {cls.FONT_UI_BOLD};
                font-weight: 600;
            }}

            QMenu {{
                background-color: {cls.BACKGROUND};
                border: 1px solid {cls.BORDER};
                color: {cls.TEXT};
                padding: 4px;
            }}
            QMenu::item {{
                padding: 8px 24px;
                border-radius: 4px;
                font-family: {cls.FONT_UI_MEDIUM};
                font-weight: 500;
            }}
            QMenu::item:selected {{
                background-color: {cls.PRIMARY};
                color: #FFFFFF;
            }}
            QMenu::separator {{
                height: 1px;
                background: {cls.GRAY_200};
                margin: 5px 0;
            }}

            QTabWidget::pane {{
                border: 1px solid {cls.BORDER};
                border-radius: 8px;
                background-color: {cls.BACKGROUND};
                top: -1px;
            }}
            QTabBar::tab {{
                background-color: {cls.GRAY_100};
                color: {cls.TEXT_SECONDARY};
                border: 1px solid {cls.BORDER};
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 16px;
                margin-right: 2px;
                min-width: 100px;
                font-family: {cls.FONT_UI_MEDIUM};
                font-weight: 400;
            }}
            QTabBar::tab:selected {{
                background-color: {cls.BACKGROUND};
                color: {cls.PRIMARY};
                border-color: {cls.BORDER};
                border-top: 2px solid {cls.PRIMARY};
                font-family: {cls.FONT_UI_BOLD};
                font-weight: 600;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {cls.PRIMARY_LIGHT};
                color: {cls.PRIMARY_DARK};
            }}

            QPushButton {{
                background-color: {cls.BACKGROUND};
                color: {cls.TEXT};
                border: 1px solid {cls.BORDER};
                border-radius: 8px;
                padding: 8px 14px;
                font-family: {cls.FONT_UI_MEDIUM};
                font-weight: 500;
                min-height: 34px;
            }}
            QPushButton:hover {{
                background-color: {cls.PRIMARY_LIGHT};
                border-color: {cls.PRIMARY};
                color: {cls.PRIMARY_DARK};
            }}
            QPushButton:pressed {{
                background-color: {cls.GRAY_100};
            }}
            QPushButton:disabled {{
                background-color: {cls.GRAY_100};
                color: {cls.GRAY_500};
                border-color: {cls.GRAY_300};
            }}

            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {{
                border: 1px solid {cls.BORDER};
                border-radius: 8px;
                padding: 8px 10px;
                background-color: {cls.BACKGROUND};
                color: {cls.TEXT};
                min-height: 34px;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {{
                border: 1px solid {cls.PRIMARY};
            }}
            QLineEdit::placeholder {{
                color: {cls.GRAY_500};
            }}

            QComboBox::drop-down {{
                border: none;
                width: 18px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {cls.TEXT_SECONDARY};
                margin-right: 5px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {cls.BACKGROUND};
                border: 1px solid {cls.BORDER};
                selection-background-color: {cls.PRIMARY};
                selection-color: #FFFFFF;
            }}

            QStatusBar {{
                background-color: {cls.BACKGROUND};
                border-top: 1px solid {cls.GRAY_200};
                color: {cls.TEXT_SECONDARY};
                padding: 4px 8px;
                font-family: {cls.FONT_UI_MEDIUM};
                font-weight: 400;
            }}

            QScrollBar:vertical {{
                border: none;
                width: 10px;
                background: {cls.GRAY_100};
                margin: 2px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {cls.GRAY_400};
                min-height: 24px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {cls.GRAY_600};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QScrollBar:horizontal {{
                border: none;
                height: 10px;
                background: {cls.GRAY_100};
                margin: 2px;
                border-radius: 5px;
            }}
            QScrollBar::handle:horizontal {{
                background: {cls.GRAY_400};
                min-width: 24px;
                border-radius: 5px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {cls.GRAY_600};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0;
            }}

            QTableView {{
                gridline-color: {cls.GRAY_200};
                background-color: {cls.BACKGROUND};
                selection-background-color: {cls.PRIMARY};
                selection-color: #FFFFFF;
                color: {cls.TEXT};
                border: 1px solid {cls.BORDER};
                border-radius: 8px;
                alternate-background-color: {cls.GRAY_50};
            }}
            QTableView::item {{
                padding: 4px;
            }}
            QTableView::item:hover {{
                background-color: {cls.PRIMARY_LIGHT};
            }}

            QHeaderView::section {{
                background-color: {cls.SURFACE};
                color: {cls.TEXT};
                padding: 8px 10px;
                border: 1px solid {cls.BORDER};
                font-family: {cls.FONT_UI_BOLD};
                font-weight: 500;
                font-size: 9pt;
            }}
            QHeaderView::section:hover {{
                background-color: {cls.PRIMARY_LIGHT};
            }}

            QToolTip {{
                background-color: {cls.TEXT};
                color: #FFFFFF;
                border: 1px solid {cls.GRAY_700};
                border-radius: 4px;
                padding: 6px;
            }}
        """

    @classmethod
    def setup_application_palette(cls, app: QApplication):
        """Apply application palette so native widgets match theme."""
        palette = QPalette()

        palette.setColor(QPalette.Window, QColor(cls.BACKGROUND))
        palette.setColor(QPalette.WindowText, QColor(cls.TEXT))
        palette.setColor(QPalette.Base, QColor(cls.BACKGROUND))
        palette.setColor(QPalette.AlternateBase, QColor(cls.SURFACE))
        palette.setColor(QPalette.Text, QColor(cls.TEXT))
        palette.setColor(QPalette.PlaceholderText, QColor(cls.GRAY_500))
        palette.setColor(QPalette.Button, QColor(cls.BACKGROUND))
        palette.setColor(QPalette.ButtonText, QColor(cls.TEXT))
        palette.setColor(QPalette.Highlight, QColor(cls.PRIMARY))
        palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
        palette.setColor(QPalette.Link, QColor(cls.PRIMARY))
        palette.setColor(QPalette.LinkVisited, QColor(cls.PRIMARY_DARK))

        app.setPalette(palette)
