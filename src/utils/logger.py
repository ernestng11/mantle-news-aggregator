"""
Logging configuration for the application
"""
import logging
from typing import Optional

def setup_logger(name: str = "pg_onchain", level: int = logging.INFO) -> logging.Logger:
    """Setup and configure logger"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(level)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def get_logger(name: str = "pg_onchain") -> logging.Logger:
    """Get logger instance"""
    logger = logging.getLogger(name)
    
    # Ensure logger has handlers (configured)
    if not logger.handlers:
        setup_logger(name)
    
    # Test the logger
    logger.debug(f"Logger '{name}' is working")
    
    return logger 