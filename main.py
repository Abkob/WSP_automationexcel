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
from PyQt5.QtGui import QFont

from error_logger import setup_logging, log_exception, ErrorHandler


# Setup logging FIRST
logger = setup_logging()

# Install global exception handler
sys.excepthook = lambda exc_type, exc_value, exc_traceback: log_exception(
    logger, exc_type, exc_value, exc_traceback
)


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

        # Set default font - Segoe UI as per design document
        logger.debug(f"Setting font for platform: {sys.platform}")
        if sys.platform == 'win32':
            font = QFont("Segoe UI", 10)
        elif sys.platform == 'darwin':
            font = QFont("-apple-system", 10)
        else:
            font = QFont("sans-serif", 10)

        app.setFont(font)

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
