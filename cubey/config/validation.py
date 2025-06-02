"""
Configuration validation for Cubey
"""

import logging
from typing import Dict, Any, List, Tuple

from cubey.config.schema import ConfigSchema

logger = logging.getLogger(__name__)


def validate_camera_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate camera configuration
    
    Args:
        config: Camera configuration dictionary
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    required_fields = [
        'camera_deviceID', 'warmup_frames', 'sample_aperture', 
        'sample_coords', 'calibration'
    ]
    
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field 'cam.{field}'")
    
    if 'sample_coords' in config:
        if not isinstance(config['sample_coords'], list):
            errors.append("'cam.sample_coords' must be a list")
        elif len(config['sample_coords']) != 6:
            errors.append("'cam.sample_coords' must contain exactly 6 coordinate pairs")
        else:
            for i, coord in enumerate(config['sample_coords']):
                if not isinstance(coord, list) or len(coord) != 2:
                    errors.append(f"'cam.sample_coords[{i}]' must be a list of 2 integers")
                elif not all(isinstance(x, int) for x in coord):
                    errors.append(f"'cam.sample_coords[{i}]' must contain only integers")
    
    if 'camera_deviceID' in config and not isinstance(config['camera_deviceID'], int):
        errors.append("'cam.camera_deviceID' must be an integer")
    
    if 'warmup_frames' in config and not isinstance(config['warmup_frames'], int):
        errors.append("'cam.warmup_frames' must be an integer")
    
    if 'sample_aperture' in config and not isinstance(config['sample_aperture'], int):
        errors.append("'cam.sample_aperture' must be an integer")
    
    if 'flip_camera' in config and not isinstance(config['flip_camera'], bool):
        errors.append("'cam.flip_camera' must be a boolean")
    
    if 'flip_code' in config and not isinstance(config['flip_code'], int):
        errors.append("'cam.flip_code' must be an integer")
    
    return errors


def validate_motor_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate motor configuration
    
    Args:
        config: Motor configuration dictionary
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    required_fields = ['speed', 'pins']
    
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field 'motor.{field}'")
    
    if 'speed' in config and not isinstance(config['speed'], int):
        errors.append("'motor.speed' must be an integer")
    
    if 'pins' in config:
        if not isinstance(config['pins'], dict):
            errors.append("'motor.pins' must be a dictionary")
        else:
            required_pins = ['U', 'R', 'F', 'D', 'L', 'B']
            for pin in required_pins:
                if pin not in config['pins']:
                    errors.append(f"Missing required pin 'motor.pins.{pin}'")
                elif not isinstance(config['pins'][pin], int):
                    errors.append(f"'motor.pins.{pin}' must be an integer")
    
    return errors


def validate_web_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate web configuration
    
    Args:
        config: Web configuration dictionary
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    if 'host' in config and not isinstance(config['host'], str):
        errors.append("'web.host' must be a string")
    
    if 'port' in config:
        if not isinstance(config['port'], int):
            errors.append("'web.port' must be an integer")
        elif config['port'] < 1 or config['port'] > 65535:
            errors.append("'web.port' must be between 1 and 65535")
    
    if 'debug' in config and not isinstance(config['debug'], bool):
        errors.append("'web.debug' must be a boolean")
    
    return errors


def validate_logging_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate logging configuration
    
    Args:
        config: Logging configuration dictionary
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    if 'level' in config:
        if not isinstance(config['level'], str):
            errors.append("'logging.level' must be a string")
        elif config['level'] not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            errors.append("'logging.level' must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    
    if 'format' in config and not isinstance(config['format'], str):
        errors.append("'logging.format' must be a string")
    
    if 'file' in config and config['file'] is not None and not isinstance(config['file'], str):
        errors.append("'logging.file' must be a string or null")
    
    if 'max_size' in config and not isinstance(config['max_size'], int):
        errors.append("'logging.max_size' must be an integer")
    
    if 'backup_count' in config and not isinstance(config['backup_count'], int):
        errors.append("'logging.backup_count' must be an integer")
    
    return errors


def validate_solver_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate solver configuration
    
    Args:
        config: Solver configuration dictionary
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    if 'algorithm' in config:
        if not isinstance(config['algorithm'], str):
            errors.append("'solver.algorithm' must be a string")
        elif config['algorithm'] not in ['kociemba']:
            errors.append("'solver.algorithm' must be one of: kociemba")
    
    if 'timeout' in config:
        if not isinstance(config['timeout'], int):
            errors.append("'solver.timeout' must be an integer")
        elif config['timeout'] < 1:
            errors.append("'solver.timeout' must be greater than 0")
    
    return errors


def validate_scrambler_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate scrambler configuration
    
    Args:
        config: Scrambler configuration dictionary
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    if 'min_moves' in config:
        if not isinstance(config['min_moves'], int):
            errors.append("'scrambler.min_moves' must be an integer")
        elif config['min_moves'] < 1:
            errors.append("'scrambler.min_moves' must be greater than 0")
    
    if 'max_moves' in config:
        if not isinstance(config['max_moves'], int):
            errors.append("'scrambler.max_moves' must be an integer")
        elif config['max_moves'] < 1:
            errors.append("'scrambler.max_moves' must be greater than 0")
    
    if 'min_moves' in config and 'max_moves' in config:
        if config['min_moves'] > config['max_moves']:
            errors.append("'scrambler.min_moves' must be less than or equal to 'scrambler.max_moves'")
    
    return errors


def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate the configuration dictionary
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        Tuple containing:
            - Boolean indicating if the configuration is valid
            - List of error messages if any
    """
    errors = []
    
    # Check required sections
    required_sections = ['cam', 'motor']
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing required section '{section}'")
    
    # Validate camera configuration
    if 'cam' in config:
        errors.extend(validate_camera_config(config['cam']))
    
    # Validate motor configuration
    if 'motor' in config:
        errors.extend(validate_motor_config(config['motor']))
    
    # Validate web configuration
    if 'web' in config:
        errors.extend(validate_web_config(config['web']))
    
    # Validate logging configuration
    if 'logging' in config:
        errors.extend(validate_logging_config(config['logging']))
    
    # Validate solver configuration
    if 'solver' in config:
        errors.extend(validate_solver_config(config['solver']))
    
    # Validate scrambler configuration
    if 'scrambler' in config:
        errors.extend(validate_scrambler_config(config['scrambler']))
    
    return len(errors) == 0, errors


def validate_config_schema(config: ConfigSchema) -> Tuple[bool, List[str]]:
    """
    Validate a ConfigSchema instance
    
    Args:
        config: ConfigSchema instance to validate
        
    Returns:
        Tuple containing:
            - Boolean indicating if the configuration is valid
            - List of error messages if any
    """
    # Convert to dictionary and validate
    config_dict = config.to_dict()
    return validate_config(config_dict)
