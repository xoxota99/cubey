"""
Default configuration values for Cubey
"""

from typing import Dict, Any

# Default configuration values
DEFAULT_CONFIG: Dict[str, Any] = {
    "cam": {
        "camera_deviceID": 0,
        "frame_width": 640,
        "frame_height": 480,
        "warmup_frames": 30,
        "flip_camera": False,
        "flip_code": 0,
        "calibration": "calibration.yaml",
        "sample_aperture": 10,
        "use_threading": True,
        "max_workers": 4,
        "frame_buffer_size": 3,
        "sample_coords": [
            [300, 30],
            [440, 40],
            [270, 220],
            [440, 220],
            [270, 430],
            [420, 440]
        ]
    },
    "motors": {
        "speed": 100,
        "face_pins": {
            "U": 19,
            "R": 10,
            "F": 3,
            "D": 13,
            "L": 22,
            "B": 2
        },
        "disable_pin": 6,
        "direction_pin": 26
    },
    "solver": {
        "max_time": 2.0,
        "max_depth": 20,
        "use_cache": True
    },
    "scanner": {
        "use_threading": True,
        "max_workers": 4,
        "use_cache": True
    },
    "logging": {
        "level": "INFO",
        "file": "cubey.log",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "max_size": 10485760,
        "backup_count": 5
    }
}
