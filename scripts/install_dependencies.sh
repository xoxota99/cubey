#!/bin/bash
# Script to install system dependencies for Cubey

set -e

echo "Installing system dependencies for Cubey..."

# Check if running on Raspberry Pi
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [[ "$ID" == "raspbian" ]]; then
        echo "Detected Raspberry Pi OS"
        
        # Update package lists
        sudo apt-get update
        
        # Install dependencies for OpenCV and other libraries
        sudo apt-get install -y \
            python3-dev \
            python3-pip \
            python3-venv \
            libatlas-base-dev \
            libjasper-dev \
            libqtgui4 \
            libqt4-test \
            libhdf5-dev \
            libhdf5-serial-dev \
            libopenjp2-7 \
            libtiff5 \
            libjpeg-dev \
            libpng-dev \
            libavcodec-dev \
            libavformat-dev \
            libswscale-dev \
            libv4l-dev \
            libxvidcore-dev \
            libx264-dev \
            libgtk-3-dev \
            libcanberra-gtk* \
            libgstreamer1.0-dev \
            libgstreamer-plugins-base1.0-dev \
            gstreamer1.0-plugins-good \
            gstreamer1.0-plugins-bad \
            gstreamer1.0-plugins-ugly \
            gstreamer1.0-tools
            
        # Install Python 3.12
        echo "Installing Python 3.12..."
        sudo apt-get install -y \
            build-essential \
            software-properties-common \
            v4l-utils
            
        # Add deadsnakes PPA for Python 3.12
        sudo add-apt-repository -y ppa:deadsnakes/ppa
        sudo apt-get update
        sudo apt-get install -y \
            python3.12 \
            python3.12-venv \
            python3.12-dev
            
        # Set Python 3.12 as default
        sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
            
        # Install dependencies for GPIO control
        sudo apt-get install -y \
            python3-rpi.gpio \
            python3-pigpio \
            pigpio
            
        # Start pigpio daemon
        sudo systemctl enable pigpiod
        sudo systemctl start pigpiod
        
        echo "System dependencies installed successfully!"
    else
        echo "This script is intended for Raspberry Pi OS. Detected: $PRETTY_NAME"
        echo "Please install dependencies manually."
        exit 1
    fi
else
    echo "Could not determine operating system."
    echo "Please install dependencies manually."
    exit 1
fi
