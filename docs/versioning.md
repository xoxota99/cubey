# Versioning Strategy

Cubey follows [Semantic Versioning](https://semver.org/) for version numbering.

## Version Format

Versions are numbered in the format `MAJOR.MINOR.PATCH`:

- **MAJOR**: Incremented for incompatible API changes
- **MINOR**: Incremented for new functionality in a backward-compatible manner
- **PATCH**: Incremented for backward-compatible bug fixes

## Development Process

1. The version number is stored in `cubey/__init__.py` as `__version__`
2. Changes are tracked in `CHANGELOG.md` following the [Keep a Changelog](https://keepachangelog.com/) format
3. Git tags are used to mark releases with the format `vX.Y.Z` (e.g., `v1.0.0`)

## Bumping Versions

To bump the version, use the provided script:

```bash
python scripts/bump_version.py [major|minor|patch]
```

This script will:
1. Update the version in `cubey/__init__.py`
2. Update the `CHANGELOG.md` file
3. Commit the changes
4. Create a git tag for the new version

## Release Process

When a new tag is pushed to GitHub, the CI/CD pipeline will:

1. Build the package
2. Generate release notes from the changelog
3. Create a GitHub release
4. Publish the package to PyPI

## Changelog

The changelog is maintained in `CHANGELOG.md` and follows the [Keep a Changelog](https://keepachangelog.com/) format. It is automatically updated by the `bump_version.py` script using the `gitchangelog` tool.

To ensure your commits are properly categorized in the changelog, use the following prefixes in your commit messages:

- `new:` for new features
- `chg:` for changes to existing functionality
- `fix:` for bug fixes

For example:
```
new: Add support for custom cube colors
chg: Improve motor calibration process
fix: Correct scanning algorithm for low light conditions
```
