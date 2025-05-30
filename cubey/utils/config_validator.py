import yaml
import os
import logging
from typing import Dict, Any, List, Optional, Tuple

"""
Configuration validator for the cubey project
"""

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
    
    # Check app section
    if 'app' not in config:
        errors.append("Missing 'app' section in configuration")
    else:
        app_config = config['app']
        if 'log_level' not in app_config:
            errors.append("Missing 'log_level' in app configuration")
        if 'log_format' not in app_config:
            errors.append("Missing 'log_format' in app configuration")
    
    # Check cam section
    if 'cam' not in config:
        errors.append("Missing 'cam' section in configuration")
    else:
        cam_config = config['cam']
        required_cam_fields = [
            'warmup_frames', 'camera_deviceID', 'calibration', 
            'sample_aperture', 'sample_coords', 'flip_camera', 'flip_code'
        ]
        for field in required_cam_fields:
            if field not in cam_config:
                errors.append(f"Missing '{field}' in cam configuration")
        
        # Check sample_coords format
        if 'sample_coords' in cam_config:
            if not isinstance(cam_config['sample_coords'], list):
                errors.append("'sample_coords' must be a list")
            elif len(cam_config['sample_coords']) != 6:
                errors.append("'sample_coords' must contain exactly 6 coordinate pairs")
            else:
                for coord in cam_config['sample_coords']:
                    if not isinstance(coord, list) or len(coord) != 2:
                        errors.append("Each sample coordinate must be a list of 2 integers")
    
    # Check stepper section
    if 'stepper' not in config:
        errors.append("Missing 'stepper' section in configuration")
    else:
        stepper_config = config['stepper']
        required_stepper_fields = [
            'pin_map', 'steps_per_rev', 'move_delay', 'hertz', 'step_factor'
        ]
        for field in required_stepper_fields:
            if field not in stepper_config:
                errors.append(f"Missing '{field}' in stepper configuration")
        
        # Check pin_map
        if 'pin_map' in stepper_config:
            pin_map = stepper_config['pin_map']
            required_pins = ['up', 'right', 'front', 'down', 'left', 'back', 'dir']
            for pin in required_pins:
                if pin not in pin_map:
                    errors.append(f"Missing '{pin}' in stepper pin_map")
    
    return len(errors) == 0, errors

def load_and_validate_config(config_path: str) -> Dict[str, Any]:
    """
    Load and validate configuration from a file
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Validated configuration dictionary
        
    Raises:
        ValueError: If the configuration is invalid
        FileNotFoundError: If the configuration file does not exist
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)
    
    is_valid, errors = validate_config(config)
    if not is_valid:
        error_msg = "Invalid configuration:\n" + "\n".join(errors)
        raise ValueError(error_msg)
    
    return config

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python config_validator.py <config_file>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    try:
        config = load_and_validate_config(config_path)
        print("Configuration is valid!")
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        sys.exit(1)
