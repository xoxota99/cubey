import logging
import yaml
from typing import Optional

"""
Centralized logging configuration for the cubey project
"""

def setup_logging(config_path: Optional[str] = None) -> None:
    """
    Set up logging configuration for the cubey project
    
    Args:
        config_path: Path to the configuration file. If None, uses default config.
    """
    if config_path is None:
        # Use default config
        log_level = "INFO"
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
    else:
        # Load config from file
        with open(config_path, 'r') as ymlfile:
            config = yaml.load(ymlfile, Loader=yaml.FullLoader)
        log_level = config['app']['log_level']
        log_format = config['app']['log_format']
    
    # Configure root logger
    logging.basicConfig(
        level=logging.getLevelName(log_level),
        format=log_format
    )
    
    # Return the logger for the calling module
    return logging.getLogger()

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name
    
    Args:
        name: Name of the logger
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
