#!/bin/bash
# Script to set up Cubey as a systemd service

set -e

echo "Setting up Cubey as a systemd service..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

# Create service file
cat > /etc/systemd/system/cubey.service << EOF
[Unit]
Description=Cubey Rubik's Cube Solver
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/cubey
ExecStart=/home/pi/cubey/venv/bin/python -m cubey.web.app
Restart=on-failure
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=cubey

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

echo "Service file created at /etc/systemd/system/cubey.service"
echo ""
echo "To start the service:"
echo "  sudo systemctl start cubey"
echo ""
echo "To enable the service at boot:"
echo "  sudo systemctl enable cubey"
echo ""
echo "To check the status:"
echo "  sudo systemctl status cubey"
