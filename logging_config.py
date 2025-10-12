"""
Centralized logging configuration for the Azure Document Intelligence demo.
"""

import logging
import os
from typing import Optional

def setup_logging(level: Optional[str] = None) -> None:
    """
    Set up logging configuration for the entire application.
    
    Args:
        level: Optional logging level override (DEBUG, INFO, WARNING, ERROR)
    """
    # Determine log level
    if level:
        log_level = getattr(logging, level.upper(), logging.INFO)
    else:
        # Check environment variable first, default to INFO
        env_level = os.getenv('AZURE_DI_LOG_LEVEL', 'INFO').upper()
        log_level = getattr(logging, env_level, logging.INFO)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(funcName)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        force=True  # Override any existing configuration
    )
    
    # Set specific logger levels
    loggers = {
        'azure_di_client': log_level,
        'app': log_level,
        'test_client': log_level,
        'debug_runner': log_level,
        # Suppress some noisy third-party loggers
        'urllib3': logging.WARNING,
        'requests': logging.WARNING,
        'streamlit': logging.WARNING
    }
    
    for logger_name, logger_level in loggers.items():
        logging.getLogger(logger_name).setLevel(logger_level)
    
    # Log the configuration
    logger = logging.getLogger(__name__)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with consistent formatting.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

# Environment variable reference for users
LOGGING_HELP = """
Set logging level with environment variable:

export AZURE_DI_LOG_LEVEL=DEBUG    # Show all debug messages
export AZURE_DI_LOG_LEVEL=INFO     # Show info and above (default)
export AZURE_DI_LOG_LEVEL=WARNING  # Show warnings and errors only
export AZURE_DI_LOG_LEVEL=ERROR    # Show errors only

Or set in your .env file:
AZURE_DI_LOG_LEVEL=DEBUG
"""