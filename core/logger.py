import logging
import sys
from typing import Optional

def setup_logger(
    name: str,
    level: Optional[str] = "INFO",
    format_string: Optional[str] = None
) -> logging.Logger:
    """Configure logger with console-only output"""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove any existing handlers
    logger.handlers.clear()
    
    # Default format if none provided
    if not format_string:
        format_string = '%(asctime)s | %(levelname)-8s | %(name)-12s | %(message)s'
    
    # Create formatter
    formatter = logging.Formatter(
        format_string,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
