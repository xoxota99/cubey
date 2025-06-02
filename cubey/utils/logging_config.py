"""
Enhanced logging configuration for Cubey
"""

import os
import logging
import logging.config
from typing import Optional
import yaml

def setup_logging(
    config_path: Optional[str] = None,
    default_level: int = logging.INFO,
    env_key: str = "CUBEY_LOG_CONFIG"
) -> None:
    """
    Set up logging configuration from a YAML file
    
    Args:
        config_path: Path to the logging configuration file
        default_level: Default logging level
        env_key: Environment variable that can override the config path
    """
    path = config_path
    value = os.getenv(env_key, None)
    if value:
        path = value
        
    if path and os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
            except Exception as e:
                print(f"Error in logging configuration: {e}")
                print("Using default logging configuration")
                _setup_default_logging(default_level)
    else:
        _setup_default_logging(default_level)
        
def _setup_default_logging(level: int) -> None:
    """
    Set up default logging configuration
    
    Args:
        level: Logging level
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=level, format=log_format)
    
    # Set up file handler with rotation
    try:
        from logging.handlers import RotatingFileHandler
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Add rotating file handler
        file_handler = RotatingFileHandler(
            "logs/cubey.log",
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        file_handler.setLevel(level)
        
        # Add handler to root logger
        logging.getLogger().addHandler(file_handler)
    except Exception as e:
        print(f"Could not set up file logging: {e}")
        
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
