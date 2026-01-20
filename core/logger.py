"""Thread-safe logging system for Easy Bulk GIF Optimizer."""

import logging
import threading
from pathlib import Path
from datetime import datetime
import sys


class ThreadSafeLogger:
    """Thread-safe logger that writes to application directory."""

    def __init__(self):
        self.logger = None
        self.lock = threading.Lock()
        self._initialize_default_logger()

    def _initialize_default_logger(self):
        """Initialize a default logger that writes to application directory."""
        with self.lock:
            # Determine default log location (same directory as executable/script)
            if getattr(sys, 'frozen', False):
                # Running as PyInstaller exe - use directory where exe is located
                base_path = Path(sys.executable).parent
            else:
                # Running in development mode - files are now in root
                base_path = Path(__file__).parent.parent

            log_file = base_path / "log.txt"

            # Create logger
            self.logger = logging.getLogger("GIFOptimizer")
            self.logger.setLevel(logging.DEBUG)

            # Remove existing handlers
            self.logger.handlers.clear()

            # Create file handler
            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)

            # Create formatter: timestamp + level + message
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)

            # Add handler to logger
            self.logger.addHandler(file_handler)

            # Log session start
            self.logger.info("=" * 80)
            self.logger.info("Easy Bulk GIF Optimizer - Application Started")
            self.logger.info("=" * 80)


    def info(self, message: str):
        """Log info message (thread-safe)."""
        with self.lock:
            if self.logger:
                self.logger.info(message)

    def warning(self, message: str):
        """Log warning message (thread-safe)."""
        with self.lock:
            if self.logger:
                self.logger.warning(message)

    def error(self, message: str):
        """Log error message (thread-safe)."""
        with self.lock:
            if self.logger:
                self.logger.error(message)

    def debug(self, message: str):
        """Log debug message (thread-safe)."""
        with self.lock:
            if self.logger:
                self.logger.debug(message)


# Global logger instance
_logger = ThreadSafeLogger()


def log_info(message: str):
    """Log info message."""
    _logger.info(message)


def log_warning(message: str):
    """Log warning message."""
    _logger.warning(message)


def log_error(message: str):
    """Log error message."""
    _logger.error(message)


def log_debug(message: str):
    """Log debug message."""
    _logger.debug(message)
