# Cubey - Rubik's Cube Solving Robot

[![Python Tests](https://github.com/cubey/cubey/actions/workflows/python-tests.yml/badge.svg)](https://github.com/cubey/cubey/actions/workflows/python-tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)

Cubey is a Raspberry Pi-based Rubik's Cube solving robot that uses computer vision to scan a cube, calculates a solution, and manipulates the cube to solve it using stepper motors.

## Features

- Computer vision-based cube scanning with OpenCV
- Efficient solving algorithm using Kociemba's two-phase algorithm
- Precise stepper motor control for cube manipulation
- Web interface for remote operation
- Command-line interface for local operation
- Comprehensive logging and error handling
- Performance optimizations for faster solving

## Project Structure

```
/
├── config/                     # Configuration files
│   ├── config.yaml             # Main configuration
│   └── calibration.yaml        # Camera calibration
│
├── cubey/                      # Main package directory
│   ├── __init__.py             # Package initialization with version
│   ├── cli.py                  # Command-line interface
│   ├── exceptions.py           # Custom exceptions
│   │
│   ├── config/                 # Configuration management
│   │   ├── __init__.py
│   │   ├── defaults.py         # Default configuration values
│   │   ├── loader.py           # Configuration loading
│   │   ├── schema.py           # Configuration schema
│   │   └── validation.py       # Configuration validation
│   │
│   ├── hardware/               # Hardware interfaces
│   │   ├── __init__.py
│   │   ├── camera.py           # Camera interface
│   │   ├── motorcontroller.py  # Motor controller
│   │   ├── motors.py           # Interactive motor control
│   │   └── calibration.py      # Hardware calibration
│   │
│   ├── solver/                 # Cube solving algorithms
│   │   ├── __init__.py
│   │   ├── kociemba_solver.py  # Kociemba solver
│   │   ├── scanner.py          # Cube state scanner
│   │   └── scrambler.py        # Cube scrambler
│   │
│   ├── ui/                     # User interfaces
│   │   ├── __init__.py
│   │   ├── cli_controller.py   # CLI controller
│   │   └── web_controller.py   # Web interface controller
│   │
│   ├── utils/                  # Utility modules
│   │   ├── __init__.py
│   │   ├── error_handler.py    # Error handling
│   │   ├── logger.py           # Logging setup
│   │   └── logging_config.py   # Logging configuration
│   │
│   └── web/                    # Web interface
│       ├── __init__.py
│       ├── app.py              # Flask application
│       ├── camera.py           # Camera streaming
│       ├── frame_event.py      # Frame event handling
│       ├── integration.py      # API integration
│       ├── security.py         # Security utilities
│       └── webstream.py        # Video streaming
│
├── docs/                       # Documentation
│   ├── api.md                  # API documentation
│   ├── configuration.md        # Configuration guide
│   └── development.md          # Development guide
│
├── scripts/                    # Utility scripts
│   ├── install_dependencies.sh # Install system dependencies
│   └── profile_solver.py       # Solver profiling script
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Test configuration
│   ├── test_solver.py          # Solver tests
│   └── test_scanner.py         # Scanner tests
│
├── setup.py                    # Package setup
├── pyproject.toml              # Project metadata
├── CONTRIBUTING.md             # Contribution guidelines
├── CHANGELOG.md                # Project changelog
└── README.md                   # This file
```

## Installation

### System Requirements

- Raspberry Pi 3 or newer
- Raspberry Pi Camera Module
- Stepper motors and drivers
- Python 3.10 or newer

### Install System Dependencies

```bash
# Run the dependency installation script
sudo ./scripts/install_dependencies.sh
```

### Install Cubey

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install from PyPI
pip install cubey

# Or install from source
pip install -e .
```

## Quick Start

### Command Line Interface

```bash
# Solve a cube
cubey solve

# Scramble a cube
cubey scramble

# Calibrate the scanner
cubey calibrate

# Manual control of motors
cubey manual

# Start the web interface
cubey web
```

### Python API

```python
from cubey.hardware.motorcontroller import MotorController
from cubey.solver.scanner import Scanner
from cubey.solver.kociemba_solver import KociembaSolver
from cubey.config.loader import load_config

# Load configuration
config = load_config()

# Initialize components
scanner = Scanner(config)
motors = MotorController(config)
solver = KociembaSolver(config)

# Scan the cube
state = scanner.get_state_string(motors)

# Solve the cube
solution = solver.solve(state)
motors.execute(solution)
```

## Web Interface

Start the web server:

```bash
cubey web --host 0.0.0.0 --port 5000
```

Then open a browser to http://localhost:5000/

## Configuration

Configuration is stored in YAML files in the `config/` directory:

- `config/config.yaml`: Main configuration
- `config/calibration.yaml`: Camera calibration

You can override the configuration by creating a custom config file and specifying it with the `--config` option:

```bash
cubey --config /path/to/custom_config.yaml solve
```

All default configuration values are defined in `cubey/config/defaults.py`.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/cubey/cubey.git
cd cubey

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Herbert Kociemba](http://kociemba.org/cube.htm) for the two-phase algorithm
- [OpenCV](https://opencv.org/) for computer vision capabilities
- All contributors to this project
