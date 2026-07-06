"""
Centralized logging configuration for the RPG game.
Provides consistent logging across all modules with file and console output.
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Log file paths
GAME_LOG = os.path.join(LOGS_DIR, "game.log")
ERROR_LOG = os.path.join(LOGS_DIR, "error.log")
DEBUG_LOG = os.path.join(LOGS_DIR, "debug.log")

# Logging levels
LOG_LEVEL = logging.INFO  # Default level (change to DEBUG for development)

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logger(name, level=None):
    """
    Create and configure a logger with file and console handlers.
    
    Args:
        name (str): Logger name (usually __name__ from calling module)
        level (int): Logging level (defaults to LOG_LEVEL)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    if level is None:
        level = LOG_LEVEL
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler for general logs (rotating, 5MB max, 3 backups)
    file_handler = RotatingFileHandler(
        GAME_LOG,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Error file handler (ERROR and above only)
    error_handler = RotatingFileHandler(
        ERROR_LOG,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    # Debug file handler (all levels, only in DEBUG mode)
    if level == logging.DEBUG:
        debug_handler = RotatingFileHandler(
            DEBUG_LOG,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=2
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)
        logger.addHandler(debug_handler)
    
    return logger

def get_logger(name):
    """
    Get or create a logger with the given name.
    Convenience function that wraps setup_logger.
    
    Args:
        name (str): Logger name (usually __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return setup_logger(name)

# Module-level logger for this config file
logger = get_logger(__name__)
logger.info("Logging system initialized")
