"""
Custom exceptions for the Cubey project
"""

from typing import Optional, Any

class CubeyError(Exception):
    """Base exception for all Cubey errors"""
    
    def __init__(self, message: str, details: Optional[Any] = None) -> None:
        """
        Initialize the exception
        
        Args:
            message: Error message
            details: Optional additional details about the error
        """
        self.message = message
        self.details = details
        super().__init__(message)

class ConfigError(CubeyError):
    """Error related to configuration"""
    pass

class ConfigurationError(ConfigError):
    """Error related to configuration (alias for backward compatibility)"""
    pass

class HardwareError(CubeyError):
    """Base exception for hardware-related errors"""
    pass

class CameraError(HardwareError):
    """Error related to camera operations"""
    pass

class MotorError(HardwareError):
    """Error related to motor operations"""
    pass

class SolverError(CubeyError):
    """Error related to cube solving"""
    pass

class ScannerError(CubeyError):
    """Error related to cube scanning"""
    pass

class CalibrationError(CubeyError):
    """Error related to calibration"""
    pass

class WebInterfaceError(CubeyError):
    """Error related to the web interface"""
    pass
