"""
Configuration loading utilities for Cubey
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional

from cubey.exceptions import ConfigError
from cubey.config.validation import validate_config
from cubey.config.defaults import DEFAULT_CONFIG
from cubey.config.schema import ConfigSchema

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
            
        if config is None:
            raise ConfigError(f"Configuration file is empty: {config_path}")
            
    except yaml.YAMLError as e:
        raise ConfigError(f"Failed to parse configuration file: {str(e)}")
    except Exception as e:
        raise ConfigError(f"Failed to load configuration: {str(e)}")
    
    # Validate the configuration
    is_valid, errors = validate_config(config)
    if not is_valid:
        error_msg = "Invalid configuration:\n" + "\n".join(errors)
        raise ConfigError(error_msg)
    
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
    
    if "CUBEY_CAMERA_WARMUP_FRAMES" in os.environ:
        env_config.setdefault("cam", {})
        env_config["cam"]["warmup_frames"] = int(os.environ["CUBEY_CAMERA_WARMUP_FRAMES"])
    
    if "CUBEY_CAMERA_SAMPLE_APERTURE" in os.environ:
        env_config.setdefault("cam", {})
        env_config["cam"]["sample_aperture"] = int(os.environ["CUBEY_CAMERA_SAMPLE_APERTURE"])
    
    if "CUBEY_CAMERA_FLIP_CAMERA" in os.environ:
        env_config.setdefault("cam", {})
        env_config["cam"]["flip_camera"] = os.environ["CUBEY_CAMERA_FLIP_CAMERA"].lower() == "true"
    
    if "CUBEY_CAMERA_FLIP_CODE" in os.environ:
        env_config.setdefault("cam", {})
        env_config["cam"]["flip_code"] = int(os.environ["CUBEY_CAMERA_FLIP_CODE"])
    
    if "CUBEY_CAMERA_CALIBRATION" in os.environ:
        env_config.setdefault("cam", {})
        env_config["cam"]["calibration"] = os.environ["CUBEY_CAMERA_CALIBRATION"]
    
    # Motors configuration
    if "CUBEY_MOTORS_SPEED" in os.environ:
        env_config.setdefault("motors", {})
        env_config["motors"]["speed"] = int(os.environ["CUBEY_MOTORS_SPEED"])
    
    if "CUBEY_MOTORS_DISABLE_PIN" in os.environ:
        env_config.setdefault("motors", {})
        env_config["motors"]["disable_pin"] = int(os.environ["CUBEY_MOTORS_DISABLE_PIN"])
        
    if "CUBEY_MOTORS_DIRECTION_PIN" in os.environ:
        env_config.setdefault("motors", {})
        env_config["motors"]["direction_pin"] = int(os.environ["CUBEY_MOTORS_DIRECTION_PIN"])
    
    # Web configuration
    if "CUBEY_WEB_HOST" in os.environ:
        env_config.setdefault("web", {})
        env_config["web"]["host"] = os.environ["CUBEY_WEB_HOST"]
    
    if "CUBEY_WEB_PORT" in os.environ:
        env_config.setdefault("web", {})
        env_config["web"]["port"] = int(os.environ["CUBEY_WEB_PORT"])
    
    if "CUBEY_WEB_DEBUG" in os.environ:
        env_config.setdefault("web", {})
        env_config["web"]["debug"] = os.environ["CUBEY_WEB_DEBUG"].lower() == "true"
    
    if "CUBEY_WEB_SECRET_KEY" in os.environ:
        env_config.setdefault("web", {})
        env_config["web"]["secret_key"] = os.environ["CUBEY_WEB_SECRET_KEY"]
    
    # Logging configuration
    if "CUBEY_LOG_LEVEL" in os.environ:
        env_config.setdefault("logging", {})
        env_config["logging"]["level"] = os.environ["CUBEY_LOG_LEVEL"]
    
    if "CUBEY_LOG_FILE" in os.environ:
        env_config.setdefault("logging", {})
        env_config["logging"]["file"] = os.environ["CUBEY_LOG_FILE"]
    
    # Solver configuration
    if "CUBEY_SOLVER_ALGORITHM" in os.environ:
        env_config.setdefault("solver", {})
        env_config["solver"]["algorithm"] = os.environ["CUBEY_SOLVER_ALGORITHM"]
    
    if "CUBEY_SOLVER_TIMEOUT" in os.environ:
        env_config.setdefault("solver", {})
        env_config["solver"]["timeout"] = int(os.environ["CUBEY_SOLVER_TIMEOUT"])
    
    # Scrambler configuration
    if "CUBEY_SCRAMBLER_MIN_MOVES" in os.environ:
        env_config.setdefault("scrambler", {})
        env_config["scrambler"]["min_moves"] = int(os.environ["CUBEY_SCRAMBLER_MIN_MOVES"])
    
    if "CUBEY_SCRAMBLER_MAX_MOVES" in os.environ:
        env_config.setdefault("scrambler", {})
        env_config["scrambler"]["max_moves"] = int(os.environ["CUBEY_SCRAMBLER_MAX_MOVES"])
    
    return env_config


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
    Get the merged configuration from defaults, file, and environment variables
    
    Args:
        config_path: Optional path to the configuration file
        
    Returns:
        Merged configuration
    """
    # Start with default configuration
    merged_config = dict(DEFAULT_CONFIG)
    
    try:
        # Load from file if available
        file_config = load_config(config_path)
        merged_config = merge_configs(merged_config, file_config)
    except ConfigError as e:
        logger.warning(f"Could not load configuration file: {e}")
        logger.warning("Using default configuration with environment overrides")
    
    # Load from environment
    env_config = get_env_config()
    merged_config = merge_configs(merged_config, env_config)
    
    return merged_config


def get_config_schema(config_path: Optional[str] = None) -> ConfigSchema:
    """
    Get the configuration as a ConfigSchema instance
    
    Args:
        config_path: Optional path to the configuration file
        
    Returns:
        ConfigSchema instance
    """
    config_dict = get_merged_config(config_path)
    return ConfigSchema.from_dict(config_dict)
