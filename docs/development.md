# Development Guide

This guide provides information for developers who want to contribute to the Cubey project or extend its functionality.

## Development Environment Setup

### Prerequisites

- Python 3.10 or newer
- Git
- OpenCV dependencies
- Raspberry Pi (for hardware testing) or a development machine

### Setting Up the Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/cubey/cubey.git
   cd cubey
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## Project Structure

```
/
├── config/                     # Configuration files
├── cubey/                      # Main package directory
│   ├── config/                 # Configuration management
│   ├── hardware/               # Hardware interfaces
│   ├── solver/                 # Cube solving algorithms
│   ├── ui/                     # User interfaces
│   ├── utils/                  # Utility modules
│   └── web/                    # Web interface
├── docs/                       # Documentation
├── scripts/                    # Utility scripts
└── tests/                      # Test suite
```

## Core Components

### Configuration System

The configuration system is responsible for loading, validating, and providing access to configuration values:

- `cubey/config/defaults.py`: Default configuration values
- `cubey/config/loader.py`: Configuration loading and merging
- `cubey/config/validation.py`: Configuration validation

### Hardware Interfaces

Hardware interfaces provide abstraction layers for physical components:

- `cubey/hardware/camera.py`: Camera interface
- `cubey/hardware/motorcontroller.py`: Motor controller
- `cubey/hardware/motors.py`: Interactive motor control

### Solver Components

Solver components handle cube state detection and solving:

- `cubey/solver/scanner.py`: Cube state scanner
- `cubey/solver/kociemba_solver.py`: Kociemba solver implementation
- `cubey/solver/scrambler.py`: Cube scrambler

### User Interfaces

User interfaces provide ways to interact with the system:

- `cubey/ui/cli_controller.py`: Command-line interface controller
- `cubey/ui/web_controller.py`: Web interface controller

## Development Workflow

### Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, following the coding standards

3. Write tests for your changes

4. Run the tests:
   ```bash
   pytest
   ```

5. Commit your changes:
   ```bash
   git commit -m "Add your feature description"
   ```

6. Push your branch:
   ```bash
   git push origin feature/your-feature-name
   ```

7. Create a pull request on GitHub

### Coding Standards

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all modules, classes, and functions
- Keep functions focused on a single responsibility
- Use meaningful variable and function names

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_solver.py

# Run with coverage report
pytest --cov=cubey
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files with the `test_` prefix
- Use descriptive test function names
- Use fixtures for common setup
- Mock hardware components for unit tests

Example test:

```python
def test_solver_finds_solution():
    # Arrange
    solver = KociembaSolver(mock_config)
    cube_state = "UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB"
    
    # Act
    solution = solver.solve(cube_state)
    
    # Assert
    assert solution is not None
    assert len(solution) > 0
```

## Extending Cubey

### Adding a New Solver Algorithm

1. Create a new file in `cubey/solver/` (e.g., `cubey/solver/new_solver.py`)
2. Implement the solver class with a `solve` method
3. Update the configuration schema to include your solver
4. Add the solver to the factory in `cubey/solver/__init__.py`
5. Write tests for your solver

### Adding Hardware Support

1. Create a new file in `cubey/hardware/` for your hardware component
2. Implement the hardware interface class
3. Update the configuration schema to include your hardware settings
4. Write tests for your hardware interface

### Adding Web Features

1. Update the API endpoints in `cubey/web/integration.py`
2. Add new routes to `cubey/web/app.py`
3. Update the web templates in `cubey/web/templates/`
4. Add any required JavaScript in `cubey/web/static/js/`

## Debugging

### Logging

Use the logging system for debugging:

```python
import logging

logger = logging.getLogger(__name__)
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
```

### Remote Debugging

For debugging on a Raspberry Pi:

1. Install debugpy:
   ```bash
   pip install debugpy
   ```

2. Add this to your code where you want to start debugging:
   ```python
   import debugpy
   debugpy.listen(("0.0.0.0", 5678))
   print("Waiting for debugger to attach...")
   debugpy.wait_for_client()
   ```

3. Connect from VS Code using the Python remote debugging configuration

## Documentation

### Building Documentation

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation
cd docs
make html
```

### Documentation Standards

- Use Markdown for all documentation files
- Include code examples where appropriate
- Keep documentation up-to-date with code changes
- Document both API usage and implementation details

## Release Process

1. Update version number in `cubey/__init__.py`
2. Update CHANGELOG.md
3. Create a new release branch:
   ```bash
   git checkout -b release/vX.Y.Z
   ```
4. Run tests and ensure all pass
5. Build and test the package:
   ```bash
   python -m build
   pip install dist/cubey-X.Y.Z.tar.gz
   ```
6. Create a pull request to merge into main
7. After merging, tag the release:
   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```
8. Publish to PyPI:
   ```bash
   python -m twine upload dist/*
   ```

## Getting Help

If you need help with development:

- Check the existing documentation
- Look at the source code and tests
- Ask questions in the GitHub issues
- Join the developer community on Discord
