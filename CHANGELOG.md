# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Restructured project to follow Python package best practices
- Added CI/CD configuration with tox and GitHub Actions
- Added comprehensive documentation
- Added proper error handling and validation
- Added type hints for improved code documentation
- Added centralized logging system
- Added configuration validation
- Added web interface improvements
- Added custom exceptions and global error handling
- Added enhanced configuration management with environment variable support
- Added enhanced logging with rotating file handlers
- Added web security features with CSRF protection
- Added comprehensive tests for camera and web interface

### Changed
- Refactored global variables into class attributes
- Improved camera resource management
- Enhanced CLI with argparse
- Updated dependency management with version pinning
- Removed redundant src directory in favor of new package structure
- Merged doc and docs directories to follow standard naming convention
- Updated Python version requirement to 3.10+ (from 3.7+)

### Fixed
- Fixed configuration file path resolution
- Fixed HSV color space handling for red
- Fixed argument parsing issues

## [0.1.0] - 2023-05-30

### Added
- Initial release of Cubey
- Basic cube scanning functionality
- Motor control for cube manipulation
- Solving algorithm integration
- Simple web interface
