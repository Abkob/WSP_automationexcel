"""
Error logging system for debugging crashes and issues.
"""

import logging
import sys
import traceback
from datetime import datetime
from pathlib import Path


def setup_logging():
    """Setup comprehensive logging system."""
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"app_{timestamp}.log"

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Create logger
    logger = logging.getLogger('StudentManager')
    logger.info("=" * 80)
    logger.info("Application Starting")
    logger.info(f"Log file: {log_file}")
    logger.info("=" * 80)

    return logger


def log_exception(logger, exc_type, exc_value, exc_traceback):
    """Log uncaught exceptions."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    logger.critical("=" * 80)
    logger.critical("CRASH DETAILS:")
    logger.critical("=" * 80)
    logger.critical(f"Exception Type: {exc_type.__name__}")
    logger.critical(f"Exception Value: {exc_value}")
    logger.critical("\nFull Traceback:")
    logger.critical(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    logger.critical("=" * 80)


class ErrorHandler:
    """Context manager for handling errors in specific sections."""

    def __init__(self, logger, section_name):
        self.logger = logger
        self.section_name = section_name

    def __enter__(self):
        self.logger.debug(f"Entering: {self.section_name}")
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is not None:
            self.logger.error(f"Error in {self.section_name}: {exc_type.__name__}: {exc_value}")
            self.logger.debug("Traceback:", exc_info=True)
            return False  # Re-raise the exception

        self.logger.debug(f"Completed: {self.section_name}")
        return True
