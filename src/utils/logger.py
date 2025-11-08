"""
Logging Setup
Configures application logging with file rotation.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logging(log_file: str = "app.log", level: int = logging.INFO):
    """
    Setup application logging with file rotation.
    
    Args:
        log_file: Path to log file
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
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
