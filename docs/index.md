# Cubey Documentation

Welcome to the Cubey documentation. Cubey is a Raspberry Pi-based Rubik's Cube solving robot.

## Overview

Cubey uses computer vision to scan a Rubik's Cube, calculates a solution, and then manipulates the cube to solve it using stepper motors.

## Features

- Computer vision-based cube scanning
- Efficient solving algorithm
- Stepper motor control
- Web interface for remote operation
- Command-line interface for local operation

## Installation

```bash
pip install cubey
```

## Quick Start

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

## Command Line Usage

```bash
# Solve a cube
cubey solve

# Scramble a cube
cubey scramble

# Calibrate the scanner
cubey calibrate

# Manual control
cubey manual
```

## Web Interface

Start the web server:

```bash
cubey web
```

Then open a browser to http://localhost:5000/
