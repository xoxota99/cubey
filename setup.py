#!/usr/bin/env python3

from setuptools import setup, find_packages
import os
import re

# Read the version from cubey/__init__.py
with open(os.path.join("cubey", "__init__.py"), encoding="utf-8") as f:
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string in cubey/__init__.py")

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cubey",
    version=version,
    author="Cubey Team",
    author_email="info@cubey.org",
    description="A Raspberry Pi-based Rubik's Cube solving robot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cubey/cubey",
    project_urls={
        "Bug Tracker": "https://github.com/cubey/cubey/issues",
        "Documentation": "https://cubey.github.io/cubey/",
        "Source Code": "https://github.com/cubey/cubey",
        "Changelog": "https://github.com/cubey/cubey/blob/main/CHANGELOG.md",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
    package_dir={"": "."},
    packages=find_packages(where="."),
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.22.0",
        "opencv-python>=4.5.0",
        "kociemba>=1.2.1",
        "pyyaml>=6.0",
        "flask>=2.0.0",
        "pillow>=9.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.1.0",
            "isort>=5.10.0",
            "mypy>=0.931",
            "flake8>=4.0.0",
            "pre-commit>=2.17.0",
            "build>=0.10.0",
            "twine>=4.0.0",
            "gitchangelog>=3.0.4",
        ],
        "docs": [
            "mkdocs>=1.2.0",
            "mkdocs-material>=8.1.0",
            "mkdocstrings>=0.18.0",
        ],
        "rpi": [
            "RPi.GPIO>=0.7.0",
            "pigpio>=1.78",
        ],
    },
    entry_points={
        "console_scripts": [
            "cubey=cubey.cli:main",
        ],
    },
    include_package_data=True,
)
