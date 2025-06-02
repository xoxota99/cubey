"""
Configuration management for Cubey
"""

import os
import yaml
from typing import Dict, Any, Optional, Union, List
import logging

from cubey.exceptions import ConfigError
from cubey.utils.config_validator import validate_config

logger = logging.getLogger(__name__)

def get_config_path(config_path: Optional[str] = None) -> str:
    """
    Get the path to the configuration file
    
    Args:
        config_path: Optional path to the configuration file
        
    Returns:
        Path to the configuration file
        
    Raises:
        ConfigError: If the configuration file does not exist
    """
    if config_path is None:
        # Use default config path - now at the top level
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "config",
            "config.yaml"
        )
    
    if not os.path.exists(config_path):
        raise ConfigError(f"Configuration file not found: {config_path}")
    
    return config_path

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a YAML file
    
    Args:
        config_path: Optional path to the configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        ConfigError: If the configuration file cannot be loaded or is invalid
    """
    config_path = get_config_path(config_path)
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        raise ConfigError(f"Failed to load configuration: {str(e)}")
    
    # Validate the configuration
    validate_config(config)
    
    return config
def get_env_config() -> Dict[str, Any]:
    """
    Get configuration from environment variables
    
    Returns:
        Configuration dictionary from environment variables
    """
    env_config: Dict[str, Any] = {}
    
    # Camera configuration
    if "CUBEY_CAMERA_DEVICE_ID" in os.environ:
        env_config.setdefault("cam", {})
        env_config["cam"]["camera_deviceID"] = int(os.environ["CUBEY_CAMERA_DEVICE_ID"])
    
    # Motor configuration
    if "CUBEY_MOTOR_SPEED" in os.environ:
        env_config.setdefault("motor", {})
        env_config["motor"]["speed"] = int(os.environ["CUBEY_MOTOR_SPEED"])
    
    # Web configuration
    if "CUBEY_WEB_PORT" in os.environ:
        env_config.setdefault("web", {})
        env_config["web"]["port"] = int(os.environ["CUBEY_WEB_PORT"])
    
    return env_config

def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries
    
    Args:
        base_config: Base configuration
        override_config: Configuration to override the base
        
def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries
    
    Args:
        base_config: Base configuration
        override_config: Configuration to override the base
        
    Returns:
        Merged configuration
    """
    result = dict(base_config)
    
    for key, value in override_config.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            # Recursively merge nested dictionaries
            result[key] = merge_configs(result[key], value)
        else:
            # Override or add the value
            result[key] = value
    
    return result

def get_merged_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Get the merged configuration from file and environment variables
    
    Args:
        config_path: Optional path to the configuration file
        
    Returns:
        Merged configuration
    """
    # Load from file
    file_config = load_config(config_path)
    
    # Load from environment
    env_config = get_env_config()
    
    # Merge configurations
    merged_config = merge_configs(file_config, env_config)
    
    return merged_config
