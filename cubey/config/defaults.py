"""
Default configuration values for Cubey
"""

from typing import Dict, Any

# Default configuration dictionary
DEFAULT_CONFIG: Dict[str, Any] = {
    'cam': {
        'camera_deviceID': 0,
        'warmup_frames': 5,
        'sample_aperture': 5,
        'sample_coords': [
            [100, 100], [200, 100], [300, 100],
            [100, 200], [200, 200], [300, 200]
        ],
        'calibration': 'default_calib.yaml',
        'flip_camera': False,
        'flip_code': 0
    },
    'motor': {
        'speed': 100,
        'pins': {
            'U': 17,  # Up face
            'R': 18,  # Right face
            'F': 27,  # Front face
            'D': 22,  # Down face
            'L': 23,  # Left face
            'B': 24   # Back face
        }
    },
    'web': {
        'host': '0.0.0.0',
        'port': 5000,
        'debug': False
    },
    'logging': {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': None,
        'max_size': 10485760,  # 10MB
        'backup_count': 5
    },
    'solver': {
        'algorithm': 'kociemba',
        'timeout': 30  # seconds
    },
    'scrambler': {
        'min_moves': 20,
        'max_moves': 25
    }
}
