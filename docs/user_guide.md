# Cubey User Guide

This guide provides detailed instructions for setting up, configuring, and using the Cubey Rubik's Cube solving robot.

## Table of Contents

1. [Hardware Setup](#hardware-setup)
2. [Software Installation](#software-installation)
3. [Configuration](#configuration)
4. [Basic Usage](#basic-usage)
5. [Web Interface](#web-interface)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

## Hardware Setup

### Components List

- Raspberry Pi 3 or newer
- USB Camera
- 6 Stepper Motors (NEMA 17 recommended)
- Stepper Motor Drivers (A4988 for NEMA 17)
- Power Supply (5V for Raspberry Pi, 12V for motors)
- Cube Holder Frame (3D printed or custom built)
- Wiring and Connectors
- Optional: LED Lighting for consistent illumination

### Assembly Instructions

1. **Prepare the Raspberry Pi**
   - Install Raspberry Pi OS on an SD card
   - Connect the Raspberry Pi Camera Module to the CSI port

2. **Build the Cube Holder Frame**
   - If using 3D printed parts, print all components from the provided STL files
   - Assemble the frame according to the diagram in [hardware_assembly.md](hardware_assembly.md)

3. **Mount the Motors**
   - Attach each stepper motor to the corresponding face mount
   - Ensure motors are aligned properly with the cube faces
   - Secure motors with screws and ensure they can rotate freely

4. **Connect the Electronics**
   - Wire each stepper motor to its driver board
   - Connect the driver boards to the Raspberry Pi GPIO pins according to the pinout in the configuration
   - Connect the power supply to the motors and Raspberry Pi

5. **Position the Camera**
   - Mount the camera facing the front of the cube
   - Ensure the camera has a clear view of all visible cube faces
   - Adjust lighting to minimize reflections and shadows

## Software Installation

### Prerequisites

- Raspberry Pi OS (Bullseye or newer)
- Python 3.10 or newer
- Git (for installation from source)

### Installation Steps

1. **Update your system**
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

2. **Install system dependencies**
   ```bash
   sudo apt install -y python3-pip python3-venv libopencv-dev
   ```

3. **Install Cubey**

   Option 1: Install from PyPI
   ```bash
   # Create and activate a virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install Cubey
   pip install cubey
   ```

   Option 2: Install from source
   ```bash
   # Clone the repository
   git clone https://github.com/cubey/cubey.git
   cd cubey
   
   # Create and activate a virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install in development mode
   pip install -e .
   ```

4. **Verify installation**
   ```bash
   cubey --version
   ```

## Configuration

Cubey uses YAML configuration files to define hardware settings, camera parameters, and solver options.

### Default Configuration

The default configuration is located at `config/config.yaml`. You can override it by creating a custom configuration file.

### Configuration Sections

- **cam**: Camera settings (device ID, resolution, calibration)
- **motors**: Motor controller settings (pin assignments, speed)
- **solver**: Solver algorithm parameters
- **scanner**: Scanner settings
- **logging**: Logging configuration
- **web**: Web interface settings

### Example Configuration

```yaml
# Camera settings
cam:
  camera_deviceID: 0
  frame_width: 640
  frame_height: 480
  warmup_frames: 30
  flip_camera: false
  flip_code: 0
  calibration: "calibration.yaml"
  sample_aperture: 10

# Motor controller settings
motors:
  speed: 100  # milliseconds per step
  face_pins:
    U: 19
    R: 10
    F: 3
    D: 13
    L: 22
    B: 2
  disable_pin: 6
  direction_pin: 26
```

### Camera Calibration

Before using Cubey, you need to calibrate the camera:

1. Run the calibration command:
   ```bash
   cubey calibrate
   ```

2. Follow the on-screen instructions to position the cube for calibration

3. The calibration data will be saved to `config/calibration.yaml`

## Basic Usage

Cubey provides a command-line interface for basic operations.

### Solving a Cube

1. Position the scrambled cube in the holder
2. Run the solve command:
   ```bash
   cubey solve
   ```
3. The robot will scan the cube, calculate a solution, and execute it

### Scrambling a Cube

To scramble a solved cube:

```bash
cubey scramble
```

### Manual Control

To manually control the motors:

```bash
cubey manual
```

This will enter an interactive mode where you can input moves directly.

### Command Options

For a full list of commands and options:

```bash
cubey --help
```

## Web Interface

Cubey includes a web interface for remote operation.

### Starting the Web Server

```bash
cubey web --host 0.0.0.0 --port 5000
```

### Accessing the Interface

Open a web browser and navigate to:

```
http://<raspberry-pi-ip>:5000
```

Replace `<raspberry-pi-ip>` with the IP address of your Raspberry Pi.

### Web Interface Features

- Live camera feed
- Scan and solve buttons
- Manual move input
- Solution history
- System status

## Troubleshooting

### Common Issues

#### Camera Not Detected

- Check that the camera is properly connected to the Raspberry Pi
- Ensure the camera is enabled in Raspberry Pi configuration
- Try a different camera device ID in the configuration

#### Motors Not Moving

- Verify power supply is connected and providing adequate voltage
- Check GPIO pin connections
- Ensure motor drivers are functioning properly
- Test motors individually using the manual control mode

#### Incorrect Cube State Detection

- Improve lighting conditions to ensure consistent color detection
- Recalibrate the camera
- Adjust the sample coordinates in the configuration
- Clean the cube faces to remove dirt or stickers that may affect color detection

#### Solver Errors

- Ensure the cube state is valid (each color appears exactly 9 times)
- Check that the cube is positioned correctly for scanning
- Try rescanning the cube

### Diagnostic Commands

- Check system status:
  ```bash
  cubey status
  ```

- Test individual motors:
  ```bash
  cubey test motors
  ```

- Test camera:
  ```bash
  cubey test camera
  ```

## Maintenance

### Software Updates

To update Cubey to the latest version:

```bash
pip install --upgrade cubey
```

### Hardware Maintenance

- **Motors**: Periodically check motor alignment and tighten any loose screws
- **Camera**: Clean the camera lens regularly to ensure clear images
- **Cube**: Replace worn stickers or use a new cube if colors become difficult to detect
- **Wiring**: Inspect wiring connections for damage or loose connections

### Backup Configuration

It's recommended to back up your configuration files:

```bash
cp -r config/ config_backup/
```

## Advanced Topics

For advanced usage and development information, see the [Development Guide](development.md).
