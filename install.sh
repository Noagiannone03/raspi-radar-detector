#!/bin/bash

echo "Installing Radar Detection System..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Install required packages
echo "Installing required packages..."
apt-get update
apt-get install -y python3 python3-pip espeak alsa-utils gpsd gpsd-clients

# Install Python dependencies
pip3 install gpsd-py3

# Create project directory
PROJECT_DIR="/home/pi/radar-detector"
mkdir -p $PROJECT_DIR

# Copy files to project directory
echo "Copying files..."
cp radar_detector_auto.py $PROJECT_DIR/
chmod +x $PROJECT_DIR/radar_detector_auto.py

# Copy service file
cp radar_detector.service /etc/systemd/system/

# Enable GPS daemon
echo "Configuring GPS..."
systemctl enable gpsd
systemctl start gpsd

# Enable radar detection service
echo "Enabling radar detection service..."
systemctl daemon-reload
systemctl enable radar_detector.service

# Set permissions
chown -R pi:pi $PROJECT_DIR

echo ""
echo "Installation complete!"
echo ""
echo "To use the system:"
echo "1. Place your CSV radar file at: $PROJECT_DIR/radars.csv"
echo "2. Configure WiFi credentials in /etc/wpa_supplicant/wpa_supplicant.conf"
echo "3. Reboot the system: sudo reboot"
echo ""
echo "The radar detection will start automatically on boot."
echo ""
echo "To check status: sudo systemctl status radar_detector.service"
echo "To view logs: sudo journalctl -u radar_detector.service -f"