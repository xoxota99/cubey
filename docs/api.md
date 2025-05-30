# API Reference

## Core Modules

### Scanner

```python
from cubey.core.scanner import Scanner
```

The Scanner class uses the camera to scan the state of the cube.

#### Methods

- `__init__(config)`: Initialize the scanner with the given configuration
- `scan_state(motors)`: Scan the current state of the cube
- `get_state_string(motors, state=None)`: Get a string representation of the cube state

### MotorController

```python
from cubey.core.motorcontroller import MotorController
```

The MotorController class controls the stepper motors that manipulate the cube.

#### Methods

- `__init__(config)`: Initialize the motor controller with the given configuration
- `execute(recipe_str)`: Execute a sequence of cube moves
- `rot_90(motor_pin, direction=CW)`: Rotate a face 90 degrees
- `rot_180(motor_pin, direction=CW)`: Rotate a face 180 degrees

### Camera

```python
from cubey.core.camera import Camera
```

The Camera class captures images of the cube and processes them to determine the colors.

#### Methods

- `__init__(config, calib_data)`: Initialize the camera with the given configuration and calibration data
- `get_faces(filename=None)`: Get the colors of the visible faces
- `get_raw_hsv(filename=None)`: Get the raw HSV values of the visible faces
- `close()`: Release camera resources

## Utility Modules

### Logger

```python
from cubey.utils.logger import setup_logging, get_logger
```

Centralized logging configuration for the cubey project.

#### Functions

- `setup_logging(config_path=None)`: Set up logging configuration
- `get_logger(name)`: Get a logger with the specified name

### ConfigValidator

```python
from cubey.utils.config_validator import validate_config, load_and_validate_config
```

Configuration validation for the cubey project.

#### Functions

- `validate_config(config)`: Validate the configuration dictionary
- `load_and_validate_config(config_path)`: Load and validate configuration from a file

## Web Interface

```python
from cubey.web.app import main as run_web_server
```

The web interface allows remote operation of the cube solver.

### API Endpoints

- `GET /api/status`: Get the current status of the system
- `POST /api/scan`: Scan the cube
- `POST /api/solve`: Solve the cube
- `POST /api/move`: Execute a move
