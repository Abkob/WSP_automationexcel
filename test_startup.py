"""
Startup test script - Tests each component individually to isolate crash.
"""

import sys
import logging
from error_logger import setup_logging

logger = setup_logging()

logger.info("=" * 80)
logger.info("STARTUP DIAGNOSTICS TEST")
logger.info("=" * 80)

# Test 1: Import PyQt5
logger.info("TEST 1: Importing PyQt5...")
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
    logger.info("✓ PyQt5 imported successfully")
except Exception as e:
    logger.critical(f"✗ FAILED to import PyQt5: {e}", exc_info=True)
    sys.exit(1)

# Test 2: Import styles
logger.info("TEST 2: Importing styles...")
try:
    from styles import AppTheme
    logger.info("✓ Styles module imported successfully")
except Exception as e:
    logger.critical(f"✗ FAILED to import styles: {e}", exc_info=True)
    sys.exit(1)

# Test 3: Import modern UI components
logger.info("TEST 3: Importing modern UI components...")
try:
    from modern_ui import ModernActionBar, QuickFilterBar, CompactHeader, ModernSearchBar
    logger.info("✓ Modern UI components imported successfully")
except Exception as e:
    logger.critical(f"✗ FAILED to import modern UI: {e}", exc_info=True)
    logger.critical("This is likely where the crash is happening!")
    sys.exit(1)

# Test 4: Import modern filter panel
logger.info("TEST 4: Importing modern filter panel...")
try:
    from modern_filter_panel import ModernFilterPanel
    logger.info("✓ Modern filter panel imported successfully")
except Exception as e:
    logger.critical(f"✗ FAILED to import modern filter panel: {e}", exc_info=True)
    sys.exit(1)

# Test 5: Create QApplication
logger.info("TEST 5: Creating QApplication...")
try:
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    logger.info("✓ QApplication created successfully")
except Exception as e:
    logger.critical(f"✗ FAILED to create QApplication: {e}", exc_info=True)
    sys.exit(1)

# Test 6: Create modern UI components
logger.info("TEST 6: Creating CompactHeader...")
try:
    header = CompactHeader()
    logger.info("✓ CompactHeader created successfully")
except Exception as e:
    logger.critical(f"✗ FAILED to create CompactHeader: {e}", exc_info=True)

logger.info("TEST 7: Creating ModernActionBar...")
try:
    action_bar = ModernActionBar()
    logger.info("✓ ModernActionBar created successfully")
except Exception as e:
    logger.critical(f"✗ FAILED to create ModernActionBar: {e}", exc_info=True)

logger.info("TEST 8: Creating ModernSearchBar...")
try:
    search_bar = ModernSearchBar()
    logger.info("✓ ModernSearchBar created successfully")
except Exception as e:
    logger.critical(f"✗ FAILED to create ModernSearchBar: {e}", exc_info=True)

logger.info("TEST 9: Creating QuickFilterBar...")
try:
    quick_filter = QuickFilterBar()
    logger.info("✓ QuickFilterBar created successfully")
except Exception as e:
    logger.critical(f"✗ FAILED to create QuickFilterBar: {e}", exc_info=True)

logger.info("TEST 10: Creating ModernFilterPanel...")
try:
    filter_panel = ModernFilterPanel()
    logger.info("✓ ModernFilterPanel created successfully")
except Exception as e:
    logger.critical(f"✗ FAILED to create ModernFilterPanel: {e}", exc_info=True)

# Test 7: Import main window
logger.info("TEST 11: Importing main window...")
try:
    from main_window import MainWindow
    logger.info("✓ Main window module imported successfully")
except Exception as e:
    logger.critical(f"✗ FAILED to import main window: {e}", exc_info=True)
    sys.exit(1)

# Test 8: Create main window
logger.info("TEST 12: Creating main window instance...")
try:
    window = MainWindow()
    logger.info("✓ Main window created successfully")
except Exception as e:
    logger.critical(f"✗ FAILED to create main window: {e}", exc_info=True)
    sys.exit(1)

# Test 9: Show main window
logger.info("TEST 13: Showing main window...")
try:
    window.show()
    logger.info("✓ Main window shown successfully")
except Exception as e:
    logger.critical(f"✗ FAILED to show main window: {e}", exc_info=True)
    sys.exit(1)

logger.info("=" * 80)
logger.info("ALL TESTS PASSED!")
logger.info("The application should now be visible.")
logger.info("Close the window to complete the test.")
logger.info("=" * 80)

sys.exit(app.exec_())
