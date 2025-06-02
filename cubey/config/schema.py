"""
Configuration schema definitions for Cubey
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class CameraConfig:
    """Camera configuration schema"""
    camera_deviceID: int = 0
    warmup_frames: int = 5
    sample_aperture: int = 5
    sample_coords: List[List[int]] = field(default_factory=lambda: [
        [100, 100], [200, 100], [300, 100],
        [100, 200], [200, 200], [300, 200]
    ])
    calibration: str = "default_calib.yaml"
    flip_camera: bool = False
    flip_code: int = 0


@dataclass
class MotorConfig:
    """Motor controller configuration schema"""
    speed: int = 100
    pins: Dict[str, int] = field(default_factory=lambda: {
        "U": 17,  # Up face
        "R": 18,  # Right face
        "F": 27,  # Front face
        "D": 22,  # Down face
        "L": 23,  # Left face
        "B": 24   # Back face
    })


@dataclass
class WebConfig:
    """Web interface configuration schema"""
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    secret_key: Optional[str] = None


@dataclass
class LoggingConfig:
    """Logging configuration schema"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    max_size: int = 10485760  # 10MB
    backup_count: int = 5


@dataclass
class SolverConfig:
    """Solver configuration schema"""
    algorithm: str = "kociemba"
    timeout: int = 30  # seconds


@dataclass
class ScramblerConfig:
    """Scrambler configuration schema"""
    min_moves: int = 20
    max_moves: int = 25


@dataclass
class ConfigSchema:
    """Main configuration schema"""
    camera: CameraConfig = field(default_factory=CameraConfig)
    motor: MotorConfig = field(default_factory=MotorConfig)
    web: WebConfig = field(default_factory=WebConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    solver: SolverConfig = field(default_factory=SolverConfig)
    scrambler: ScramblerConfig = field(default_factory=ScramblerConfig)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ConfigSchema':
        """
        Create a ConfigSchema instance from a dictionary
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            ConfigSchema instance
        """
        # Create default instance
        config = cls()
        
        # Update camera config
        if 'cam' in config_dict:
            cam_dict = config_dict['cam']
            for key, value in cam_dict.items():
                if hasattr(config.camera, key):
                    setattr(config.camera, key, value)
        
        # Update motor config
        if 'motor' in config_dict:
            motor_dict = config_dict['motor']
            for key, value in motor_dict.items():
                if hasattr(config.motor, key):
                    setattr(config.motor, key, value)
        
        # Update web config
        if 'web' in config_dict:
            web_dict = config_dict['web']
            for key, value in web_dict.items():
                if hasattr(config.web, key):
                    setattr(config.web, key, value)
        
        # Update logging config
        if 'logging' in config_dict:
            logging_dict = config_dict['logging']
            for key, value in logging_dict.items():
                if hasattr(config.logging, key):
                    setattr(config.logging, key, value)
        
        # Update solver config
        if 'solver' in config_dict:
            solver_dict = config_dict['solver']
            for key, value in solver_dict.items():
                if hasattr(config.solver, key):
                    setattr(config.solver, key, value)
        
        # Update scrambler config
        if 'scrambler' in config_dict:
            scrambler_dict = config_dict['scrambler']
            for key, value in scrambler_dict.items():
                if hasattr(config.scrambler, key):
                    setattr(config.scrambler, key, value)
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the ConfigSchema to a dictionary
        
        Returns:
            Configuration dictionary
        """
        return {
            'cam': {
                'camera_deviceID': self.camera.camera_deviceID,
                'warmup_frames': self.camera.warmup_frames,
                'sample_aperture': self.camera.sample_aperture,
                'sample_coords': self.camera.sample_coords,
                'calibration': self.camera.calibration,
                'flip_camera': self.camera.flip_camera,
                'flip_code': self.camera.flip_code
            },
            'motor': {
                'speed': self.motor.speed,
                'pins': self.motor.pins
            },
            'web': {
                'host': self.web.host,
                'port': self.web.port,
                'debug': self.web.debug,
                'secret_key': self.web.secret_key
            },
            'logging': {
                'level': self.logging.level,
                'format': self.logging.format,
                'file': self.logging.file,
                'max_size': self.logging.max_size,
                'backup_count': self.logging.backup_count
            },
            'solver': {
                'algorithm': self.solver.algorithm,
                'timeout': self.solver.timeout
            },
            'scrambler': {
                'min_moves': self.scrambler.min_moves,
                'max_moves': self.scrambler.max_moves
            }
        }
