# Contributing to Cubey

Thank you for your interest in contributing to Cubey! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/cubey.git`
3. Create a branch for your changes: `git checkout -b feature/your-feature-name`
4. Install development dependencies: `pip install -e ".[dev]"`

## Development Environment

We recommend using a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

## Code Style

We follow PEP 8 with some modifications:
- Line length: 88 characters (enforced by Black)
- Use type hints for all function definitions
- Use docstrings for all modules, classes, and functions

We use the following tools to enforce code style:
- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

You can run these tools using tox:

```bash
tox -e lint
tox -e type
```

## Testing

Write tests for all new features and bug fixes. Run the tests using:

```bash
pytest
```

Or with coverage:

```bash
pytest --cov=cubey
```

## Pull Request Process

1. Update the README.md and documentation with details of changes if appropriate
2. Update the CHANGELOG.md with your changes
3. The PR should work for Python 3.10, 3.11, and 3.12
4. Make sure all tests pass and code style checks pass
5. Your PR will be reviewed by maintainers

## Release Process

1. Update version in `cubey/__init__.py`
2. Update CHANGELOG.md
3. Create a new release on GitHub with release notes
4. Publish to PyPI (maintainers only)

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
