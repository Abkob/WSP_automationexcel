"""
Student Admissions Manager - Main Entry Point
Professional DataFrame Viewer implementing the complete design document.
Version 2.0 - Full Integration with Error Logging
"""

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QFontDatabase

from error_logger import setup_logging, log_exception, ErrorHandler


# Setup logging FIRST
logger = setup_logging()

# Install global exception handler
sys.excepthook = lambda exc_type, exc_value, exc_traceback: log_exception(
    logger, exc_type, exc_value, exc_traceback
)


def _normalize_font_name(name: str) -> str:
    """Normalize font names for fuzzy matching across OS/build variants."""
    return "".join(ch for ch in name.lower() if ch.isalnum())


def _pick_font_family(db: QFontDatabase, candidates):
    """Pick the best installed family from a candidate list."""
    families = list(db.families())
    if not families:
        return None

    family_set = set(families)
    for candidate in candidates:
        if candidate in family_set:
            return candidate

    ranked_families = []
    normalized_families = [(fam, _normalize_font_name(fam)) for fam in families]
    for candidate in candidates:
        candidate_norm = _normalize_font_name(candidate)
        for family, family_norm in normalized_families:
            if candidate_norm and (candidate_norm in family_norm or family_norm in candidate_norm):
                score = (
                    0 if family_norm == candidate_norm else 1,
                    abs(len(family_norm) - len(candidate_norm)),
                    len(family_norm),
                )
                ranked_families.append((score, family))
        if ranked_families:
            ranked_families.sort(key=lambda item: item[0])
            return ranked_families[0][1]

    return None


def _resolve_app_fonts():
    """Resolve English/Arabic brand font families with robust fallbacks."""
    db = QFontDatabase()

    english_regular = [
        "Proxima Nova Rg",
        "Proxima Nova Regular",
        "Proxima Nova",
        "ProximaNova",
        "Segoe UI",
        "Helvetica Neue",
        "Arial",
    ]
    english_medium = [
        "Proxima Nova Lt",
        "Proxima Nova Semibold",
        "Proxima Nova",
        "Segoe UI Semibold",
        "Segoe UI",
        "Arial",
    ]
    english_bold = [
        "Proxima Nova Th",
        "Proxima Nova Extrabold",
        "Proxima Nova Bold",
        "Segoe UI Bold",
        "Segoe UI",
        "Arial",
    ]
    arabic_candidates = [
        "Cairo",
        "Cairo Regular",
        "Noto Sans Arabic",
        "Dubai",
        "Geeza Pro",
        "Arial",
    ]

    english_family = _pick_font_family(db, english_regular)
    english_medium_family = _pick_font_family(db, english_medium)
    english_bold_family = _pick_font_family(db, english_bold)
    arabic_family = _pick_font_family(db, arabic_candidates)

    if not english_family:
        english_family = QFont().defaultFamily()
    if not english_medium_family:
        english_medium_family = english_family
    if not english_bold_family:
        english_bold_family = english_family
    if not arabic_family:
        arabic_family = english_family

    return english_family, english_medium_family, english_bold_family, arabic_family


def setup_application():
    """Configure application settings."""
    try:
        logger.info("Setting up application...")

        # High DPI support
        logger.debug("Enabling High DPI scaling")
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        logger.debug("Creating QApplication instance")
        app = QApplication(sys.argv)
        app.setApplicationName("Student Admissions Manager")
        app.setOrganizationName("AdmissionsTools")
        app.setApplicationVersion("2.0")

        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))

        # Typography from guideline:
        # English UI: Proxima Nova (with smart variant matching)
        # Arabic content: Cairo (stored for components that need Arabic rendering)
        logger.debug(f"Resolving fonts for platform: {sys.platform}")
        ui_font_family, ui_font_medium, ui_font_bold, arabic_font_family = _resolve_app_fonts()
        font = QFont(ui_font_family, 10)
        font.setStyleStrategy(QFont.PreferAntialias)
        app.setFont(font)
        app.setProperty("ui_font_family", ui_font_family)
        app.setProperty("ui_font_family_medium", ui_font_medium)
        app.setProperty("ui_font_family_bold", ui_font_bold)
        app.setProperty("arabic_font_family", arabic_font_family)
        logger.info(
            "Font families selected: UI='%s', UI Medium='%s', UI Bold='%s', Arabic='%s'",
            ui_font_family,
            ui_font_medium,
            ui_font_bold,
            arabic_font_family,
        )

        # Apply theme
        logger.debug("Applying theme...")
        try:
            from styles import AppTheme
            AppTheme.setup_application_palette(app)
            app.setStyleSheet(AppTheme.get_stylesheet())
            logger.info("Theme applied successfully")
        except Exception as e:
            logger.error(f"Error applying theme: {e}", exc_info=True)
            # Continue anyway - theme is not critical

        logger.info("Application setup complete")
        return app

    except Exception as e:
        logger.critical(f"FATAL: Failed to setup application: {e}", exc_info=True)
        raise


def main():
    """Main entry point."""
    try:
        logger.info("=" * 80)
        logger.info("STARTING MAIN APPLICATION")
        logger.info("=" * 80)

        with ErrorHandler(logger, "Application Setup"):
            app = setup_application()

        # Import main window AFTER logging is set up
        logger.info("Importing main window module...")
        try:
            from main_window import MainWindow
            logger.info("Main window module imported successfully")
        except Exception as e:
            logger.critical(f"FATAL: Failed to import MainWindow: {e}", exc_info=True)
            QMessageBox.critical(
                None,
                "Import Error",
                f"Failed to import main window module:\n\n{str(e)}\n\nCheck logs/app_*.log for details"
            )
            return 1

        # Create and show main window
        logger.info("Creating main window instance...")
        try:
            window = MainWindow()
            logger.info("Main window created successfully")
        except Exception as e:
            logger.critical(f"FATAL: Failed to create MainWindow: {e}", exc_info=True)
            QMessageBox.critical(
                None,
                "Startup Error",
                f"Failed to create main window:\n\n{str(e)}\n\nCheck logs/app_*.log for details"
            )
            return 1

        logger.info("Showing main window...")
        try:
            window.show()
            logger.info("Main window displayed successfully")
        except Exception as e:
            logger.critical(f"FATAL: Failed to show MainWindow: {e}", exc_info=True)
            QMessageBox.critical(
                None,
                "Display Error",
                f"Failed to display main window:\n\n{str(e)}\n\nCheck logs/app_*.log for details"
            )
            return 1

        # Check for command line file argument
        if len(sys.argv) > 1:
            filepath = sys.argv[1]
            logger.info(f"Command line file argument: {filepath}")
            if os.path.exists(filepath) and filepath.lower().endswith(('.xlsx', '.xls', '.csv', '.tsv', '.json')):
                logger.info(f"Loading file from command line: {filepath}")
                try:
                    window.load_file(filepath)
                    logger.info("File loaded successfully")
                except Exception as e:
                    logger.error(f"Error loading file from command line: {e}", exc_info=True)

        logger.info("Starting event loop...")
        return_code = app.exec_()
        logger.info(f"Application exited with code: {return_code}")
        return return_code

    except Exception as e:
        logger.critical(f"FATAL ERROR in main(): {e}", exc_info=True)
        try:
            QMessageBox.critical(
                None,
                "Fatal Error",
                f"Application crashed:\n\n{str(e)}\n\nCheck logs/app_*.log for full details"
            )
        except:
            pass
        return 1


if __name__ == "__main__":
    exit_code = main()
    logger.info("=" * 80)
    logger.info(f"APPLICATION SHUTDOWN - Exit code: {exit_code}")
    logger.info("=" * 80)
    sys.exit(exit_code)
