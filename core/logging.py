import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Tuple

LOG_DIR = "app/log"
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logging() -> Tuple[logging.Logger, logging.Logger]:
    """
    Set up and configure loggers for the application.
    This function configures:
      - A primary logger ("scraper_api") that logs to both the console and a rotating file.
      - A separate logger ("request_logger") that logs request-specific logs to its own rotating file.
    Returns:
        Tuple[logging.Logger, logging.Logger]: A tuple containing the primary logger and the request logger.
    """
    # Get or create the main application logger.
    logger_app = logging.getLogger("scraper_api")
    logger_app.setLevel(logging.INFO)
    
    # If the logger already has handlers configured, assume setup is complete.
    if logger_app.handlers:
        return logger_app, logging.getLogger("request_logger")
    
    # Define a formatter for general logs with a timestamp.
    general_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    # Define a formatter for request logs.
    request_formatter = logging.Formatter(
        "%(asctime)s - %(message)s", 
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler for logging to the terminal (useful for debugging).
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(general_formatter)
    
    # File handler for general logs with rotation.
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "scraper_api.log"),
        maxBytes=10 * 1024 * 1024,  # 10 MB per log file
        backupCount=5              # Keep up to 5 backup log files
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(general_formatter)
    
    # File handler for request logs with rotation.
    request_file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "request.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    request_file_handler.setLevel(logging.INFO)
    request_file_handler.setFormatter(request_formatter)
    
    # Attach the console and file handlers to the main logger.
    logger_app.addHandler(console_handler)
    logger_app.addHandler(file_handler)
    
    # Create and configure a separate logger for requests.
    request_logger = logging.getLogger("request_logger")
    request_logger.setLevel(logging.INFO)
    request_logger.addHandler(request_file_handler)
    
    return logger_app, request_logger

logger, request_logger = setup_logging()