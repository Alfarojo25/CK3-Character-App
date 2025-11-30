"""
Logging Setup
Configures application logging with file rotation.
"""

import logging
import os
import sys
import traceback
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logging(log_file: str = None, level: int = logging.INFO):
    """
    Setup application logging with file rotation.
    
    Args:
        log_file: Path to log file (default: log/log.txt)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Default log file in log directory
    if log_file is None:
        log_file = os.path.join("log", "log.txt")
    
    # Create logs directory if needed
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # File handler with rotation (max 5MB, keep 3 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler (only WARNING and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Setup global exception handler to log uncaught exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions and log them."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Don't log keyboard interrupt
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger.critical("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))
        logger.critical("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    
    sys.excepthook = handle_exception
    
    # Log startup
    logger.info("="*50)
    logger.info(f"Application started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*50)


def get_logger(name: str) -> logging.Logger:
    """
    Get logger for a module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
