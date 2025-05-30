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

# Start the web interface
cubey web
```

### Python API

```python
from cubey.core.scanner import Scanner
from cubey.core.motorcontroller import MotorController
import cubey

# Initialize components
scanner = Scanner(config)
motors = MotorController(config)

# Scan the cube
state = scanner.get_state_string(motors)

# Solve the cube
solution = cubey.kociemba.solve(state)
motors.execute(solution)
```

## Web Interface

Start the web server:

```bash
cubey web
```

Then open a browser to http://localhost:5000/

## Configuration

Configuration is stored in YAML files:

- `cubey/data/config.yaml`: Main configuration
- `cubey/data/default_calib.yaml`: Camera calibration

You can override the configuration by creating a custom config file and specifying it with the `--config` option:

```bash
cubey --config /path/to/custom_config.yaml solve
```

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
