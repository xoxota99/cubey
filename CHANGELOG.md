# Changelog

All notable changes to the Cubey project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Type annotations throughout the codebase
- Improved error handling with custom exceptions
- Scrambler class for web interface
- Configuration validation
- Proper versioning strategy with semantic versioning

### Changed
- Reorganized project structure
- Moved configuration files to top-level config directory
- Improved import structure and removed unused imports
- Enhanced web module with proper type annotations
- Updated dependency management in setup.py

### Fixed
- Fixed incorrect import paths in web modules
- Fixed configuration loading in web modules
- Fixed missing Scrambler class implementation
- Fixed duplicate function definitions

## [0.1.0] - 2024-05-15

### Added
- Initial release of Cubey
- Basic cube solving functionality
- Web interface for controlling the robot
- Hardware control for Raspberry Pi
- Camera integration for cube scanning
- Kociemba solver implementation

[Unreleased]: https://github.com/cubey/cubey/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/cubey/cubey/releases/tag/v0.1.0
