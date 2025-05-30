# Development Guide

This guide provides information for developers who want to contribute to Cubey.

## Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cubey.git
   cd cubey
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

## Project Structure

```
/cubey/
├── cubey/                      # Main package directory
│   ├── __init__.py             # Package initialization
│   ├── cli.py                  # Command-line interface
│   ├── core/                   # Core functionality
│   │   ├── __init__.py
│   │   ├── camera.py
│   │   ├── motorcontroller.py
│   │   └── scanner.py
│   ├── utils/                  # Utility modules
│   │   ├── __init__.py
│   │   ├── config_validator.py
│   │   └── logger.py
│   ├── web/                    # Web interface
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── integration.py
│   │   ├── static/
│   │   └── templates/
│   └── data/                   # Configuration and data files
│       ├── config.yaml
│       └── default_calib.yaml
├── tests/                      # All tests in one directory
│   ├── __init__.py
│   ├── test_camera.py
│   ├── test_motorcontroller.py
│   ├── test_scanner.py
│   └── test_web.py
├── docs/                       # Documentation
├── scripts/                    # Utility scripts
├── setup.py                    # Package installation
├── pyproject.toml              # Modern Python packaging
├── LICENSE
├── README.md
└── requirements.txt
```

## Running Tests

Run the tests using pytest:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=cubey
```

## Code Style

We use several tools to enforce code style:

- Black for code formatting:
  ```bash
  black cubey tests
  ```

- isort for import sorting:
  ```bash
  isort cubey tests
  ```

- flake8 for linting:
  ```bash
  flake8 cubey tests
  ```

- mypy for type checking:
  ```bash
  mypy cubey
  ```

You can run all of these using tox:

```bash
tox -e lint
tox -e type
```

## Building Documentation

We use MkDocs for documentation:

```bash
pip install mkdocs
mkdocs serve  # Preview documentation locally
mkdocs build  # Build documentation
```

## Release Process

1. Update version in `cubey/__init__.py`
2. Update CHANGELOG.md
3. Create a new release on GitHub
4. Build and publish to PyPI:
   ```bash
   python -m build
   python -m twine upload dist/*
   ```

## Python Version Support

Cubey requires Python 3.10 or newer. We test on Python 3.10, 3.11, and 3.12.
