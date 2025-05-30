"""
Custom exceptions for the Cubey project
"""

class CubeyError(Exception):
    """Base exception for all Cubey errors"""
    pass

class ConfigError(CubeyError):
    """Error related to configuration"""
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
