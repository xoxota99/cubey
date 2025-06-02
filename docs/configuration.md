# Configuration Guide

This guide explains how to configure the Cubey robot to match your hardware setup and preferences.

## Configuration Files

Cubey uses YAML files for configuration:

- **Main Configuration**: `config/config.yaml`
- **Camera Calibration**: `config/calibration.yaml`

## Configuration Structure

The main configuration file is divided into several sections:

```yaml
cam:     # Camera settings
motors:  # Motor controller settings
solver:  # Solver algorithm settings
scanner: # Scanner settings
logging: # Logging configuration
web:     # Web interface settings
```

## Camera Configuration

The `cam` section configures the camera used for scanning the cube:

```yaml
cam:
  camera_deviceID: 0           # Camera device ID (usually 0 for the first camera)
  frame_width: 640             # Frame width in pixels
  frame_height: 480            # Frame height in pixels
  warmup_frames: 30            # Number of frames to discard during initialization
  flip_camera: false           # Whether to flip the camera image
  flip_code: 0                 # Flip code (0: horizontal, 1: vertical, -1: both)
  calibration: "calibration.yaml"  # Path to calibration file
  sample_aperture: 10          # Size of the sampling area in pixels
  use_threading: true          # Whether to use threading for frame processing
  max_workers: 4               # Maximum number of worker threads
  frame_buffer_size: 3         # Size of the frame buffer
  sample_coords:               # Coordinates for sampling cube colors
    - [300, 30]                # Top-left facelet
    - [440, 40]                # Top-right facelet
    - [270, 220]               # Middle-left facelet
    - [440, 220]               # Middle-right facelet
    - [270, 430]               # Bottom-left facelet
    - [420, 440]               # Bottom-right facelet
```

### Camera Calibration

The camera calibration file contains color thresholds and camera parameters:

```yaml
camera:
  CAP_PROP_BRIGHTNESS: 50
  CAP_PROP_CONTRAST: 50
  CAP_PROP_SATURATION: 50
  CAP_PROP_EXPOSURE: -6

colors:
  white:
    min: [0, 0, 200]
    max: [180, 30, 255]
  red:
    min: [170, 120, 70]
    max: [10, 255, 255]
  green:
    min: [45, 100, 50]
    max: [75, 255, 255]
  blue:
    min: [100, 100, 50]
    max: [130, 255, 255]
  orange:
    min: [10, 150, 100]
    max: [25, 255, 255]
  yellow:
    min: [25, 100, 100]
    max: [45, 255, 255]
```

## Motor Configuration

The `motors` section configures the stepper motors that manipulate the cube:

```yaml
motors:
  speed: 100                # Milliseconds per step
  face_pins:                # GPIO pins for each face
    U: 19                   # Up face
    R: 10                   # Right face
    F: 3                    # Front face
    D: 13                   # Down face
    L: 22                   # Left face
    B: 2                    # Back face
  disable_pin: 6            # Pin to disable all motors
  direction_pin: 26         # Pin to control motor direction
```

### Motor Pin Assignments

The pin numbers correspond to the Raspberry Pi GPIO numbers (BCM mode), not the physical pin numbers. Refer to the [Raspberry Pi GPIO pinout](https://pinout.xyz/) for details.

## Solver Configuration

The `solver` section configures the cube-solving algorithm:

```yaml
solver:
  max_time: 2.0             # Maximum time in seconds for the solver
  max_depth: 20             # Maximum search depth
```

## Scanner Configuration

The `scanner` section configures the cube scanner:

```yaml
scanner:
  use_threading: true       # Whether to use threading for scanning
  max_workers: 4            # Maximum number of worker threads
  use_cache: true           # Whether to cache scan results
```

## Logging Configuration

The `logging` section configures the logging system:

```yaml
logging:
  level: "INFO"             # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  file: "cubey.log"         # Log file path
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # Log format
  max_size: 10485760        # Maximum log file size (10MB)
  backup_count: 5           # Number of backup log files to keep
```

## Web Interface Configuration

The `web` section configures the web interface:

```yaml
web:
  host: "0.0.0.0"           # Host to bind to (0.0.0.0 for all interfaces)
  port: 5000                # Port to listen on
  debug: false              # Whether to enable debug mode
  secret_key: "dev-key-change-in-production"  # Secret key for sessions
```

## Environment Variables

Configuration values can be overridden with environment variables:

| Environment Variable | Configuration Key |
|---------------------|-------------------|
| `CUBEY_CAM_DEVICE_ID` | `cam.camera_deviceID` |
| `CUBEY_CAM_WARMUP_FRAMES` | `cam.warmup_frames` |
| `CUBEY_CAM_SAMPLE_APERTURE` | `cam.sample_aperture` |
| `CUBEY_CAM_FLIP_CAMERA` | `cam.flip_camera` |
| `CUBEY_CAM_FLIP_CODE` | `cam.flip_code` |
| `CUBEY_CAM_CALIBRATION` | `cam.calibration` |
| `CUBEY_MOTORS_SPEED` | `motors.speed` |
| `CUBEY_MOTORS_DISABLE_PIN` | `motors.disable_pin` |
| `CUBEY_MOTORS_DIRECTION_PIN` | `motors.direction_pin` |
| `CUBEY_WEB_HOST` | `web.host` |
| `CUBEY_WEB_PORT` | `web.port` |
| `CUBEY_WEB_DEBUG` | `web.debug` |
| `CUBEY_LOG_LEVEL` | `logging.level` |
| `CUBEY_LOG_FILE` | `logging.file` |
| `CUBEY_SOLVER_MAX_TIME` | `solver.max_time` |
| `CUBEY_SOLVER_MAX_DEPTH` | `solver.max_depth` |

## Custom Configuration Files

You can specify a custom configuration file with the `--config` option:

```bash
cubey --config /path/to/custom_config.yaml solve
```

## Configuration Validation

Cubey validates the configuration at startup. If there are errors, it will display detailed error messages.

To manually validate a configuration file:

```bash
cubey validate-config --config /path/to/config.yaml
```

## Default Values

Default configuration values are defined in `cubey/config/defaults.py`. These values are used if not specified in the configuration file.

## Configuration Tips

- **Camera**: Adjust `sample_coords` based on your camera position and cube size
- **Motors**: Decrease `speed` for smoother but slower movements, increase for faster solving
- **Solver**: Increase `max_time` and `max_depth` for more complex cube states
- **Web**: Change `host` to `127.0.0.1` for local access only
- **Logging**: Use `DEBUG` level for troubleshooting, `INFO` for normal operation
