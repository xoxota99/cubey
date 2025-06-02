#!/usr/bin/env python3
"""
Version bumping script for Cubey.

This script updates the version number in cubey/__init__.py and creates a git tag.
It follows semantic versioning (https://semver.org/).

Usage:
    python scripts/bump_version.py [major|minor|patch]
"""

import re
import sys
import os
import subprocess
from typing import Tuple, Optional

VERSION_FILE = "cubey/__init__.py"
VERSION_PATTERN = r'__version__ = ["\']([^"\']*)["\']'


def get_current_version() -> str:
    """Get the current version from the version file."""
    with open(VERSION_FILE, "r") as f:
        content = f.read()
        match = re.search(VERSION_PATTERN, content)
        if not match:
            raise ValueError(f"Could not find version in {VERSION_FILE}")
        return match.group(1)


def bump_version(current_version: str, bump_type: str) -> str:
    """Bump the version according to semantic versioning."""
    major, minor, patch = map(int, current_version.split("."))
    
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}. Use 'major', 'minor', or 'patch'.")
    
    return f"{major}.{minor}.{patch}"


def update_version_file(new_version: str) -> None:
    """Update the version in the version file."""
    with open(VERSION_FILE, "r") as f:
        content = f.read()
    
    new_content = re.sub(VERSION_PATTERN, f'__version__ = "{new_version}"', content)
    
    with open(VERSION_FILE, "w") as f:
        f.write(new_content)


def create_git_tag(version: str) -> None:
    """Create a git tag for the new version."""
    tag_name = f"v{version}"
    subprocess.run(["git", "tag", "-a", tag_name, "-m", f"Release {tag_name}"], check=True)
    print(f"Created git tag: {tag_name}")
    print("To push the tag to the remote repository, run:")
    print(f"  git push origin {tag_name}")


def update_changelog(version: str) -> None:
    """Update the CHANGELOG.md file."""
    try:
        # Install gitchangelog if not already installed
        subprocess.run(["pip", "install", "gitchangelog"], check=True)
        
        # Generate changelog
        changelog_output = subprocess.check_output(["gitchangelog"], text=True)
        
        # Write to CHANGELOG.md
        with open("CHANGELOG.md", "w") as f:
            f.write(changelog_output)
        
        print("Updated CHANGELOG.md")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Failed to update changelog: {e}")
        print("You may need to update CHANGELOG.md manually.")


def main() -> int:
    """Main function."""
    if len(sys.argv) != 2 or sys.argv[1] not in ["major", "minor", "patch"]:
        print(__doc__)
        return 1
    
    bump_type = sys.argv[1]
    current_version = get_current_version()
    new_version = bump_version(current_version, bump_type)
    
    print(f"Current version: {current_version}")
    print(f"New version: {new_version}")
    
    # Confirm with the user
    response = input("Do you want to continue? [y/N] ")
    if response.lower() != "y":
        print("Aborted.")
        return 0
    
    # Update version file
    update_version_file(new_version)
    print(f"Updated {VERSION_FILE}")
    
    # Update changelog
    update_changelog(new_version)
    
    # Commit changes
    subprocess.run(["git", "add", VERSION_FILE, "CHANGELOG.md"], check=True)
    subprocess.run(["git", "commit", "-m", f"Bump version to {new_version}"], check=True)
    print("Committed version bump")
    
    # Create git tag
    create_git_tag(new_version)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
