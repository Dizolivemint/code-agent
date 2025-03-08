import logging
import os
import sys
from pathlib import Path

# Create logger
logger = logging.getLogger("code_agent")
logger.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
console_handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(console_handler)

def setup_logger(log_file: str = None, level: int = logging.INFO):
    """
    Set up logger with file handler
    
    Args:
        log_file: Path to log file
        level: Logging level
    """
    global logger
    
    # Set logger level
    logger.setLevel(level)
    
    # Create file handler if log file provided
    if log_file:
        # Create directory if it doesn't exist
        log_path = Path(log_file)
        os.makedirs(log_path.parent, exist_ok=True)
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
        
        logger.info(f"Logging to file: {log_file}") 
