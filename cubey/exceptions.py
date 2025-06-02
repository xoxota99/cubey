"""
Custom exceptions for the Cubey project.

This module defines custom exceptions used throughout the Cubey project.
"""

class CubeyError(Exception):
    """Base exception for all Cubey errors."""
    pass


class ConfigError(CubeyError):
    """Exception raised for configuration errors."""
    pass


class CameraError(CubeyError):
    """Exception raised for camera-related errors."""
    pass


class MotorError(CubeyError):
    """Exception raised for motor-related errors."""
    pass


class ScannerError(CubeyError):
    """Exception raised for scanner-related errors."""
    pass


class SolverError(CubeyError):
    """Exception raised for solver-related errors."""
    pass


class ValidationError(CubeyError):
    """Exception raised for validation errors."""
    pass


class WebError(CubeyError):
    """Exception raised for web interface errors."""
    pass
