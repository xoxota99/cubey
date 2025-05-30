"""
Custom exceptions for the Cubey project
"""

class CubeyError(Exception):
    """Base exception for all Cubey errors"""
    pass


class ConfigurationError(CubeyError):
    """Exception raised for errors in the configuration"""
    pass


class CameraError(CubeyError):
    """Exception raised for camera-related errors"""
    pass


class MotorError(CubeyError):
    """Exception raised for motor-related errors"""
    pass


class ScannerError(CubeyError):
    """Exception raised for scanner-related errors"""
    pass


class InvalidCubeStateError(CubeyError):
    """Exception raised when the cube state is invalid"""
    pass


class SolverError(CubeyError):
    """Exception raised for solver-related errors"""
    pass


class WebInterfaceError(CubeyError):
    """Exception raised for web interface-related errors"""
    pass
