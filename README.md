# Automatic Radar Detection System for Raspberry Pi

This system automatically detects speed cameras/radars based on GPS location and announces alerts in English.

## Features

- **Automatic WiFi Connection**: Connects to WiFi on startup with voice feedback
- **Real-time GPS Tracking**: Continuously monitors your location
- **Radar Database**: Compares location with CSV database of radar positions
- **Voice Alerts**: Announces radar detection, distance, and speed limits in English
- **Optimized Performance**: Efficient proximity detection within 300m radius
- **Auto-startup**: Launches automatically when Raspberry Pi boots

## Installation

1. **Run the installation script as root:**
   ```bash
   sudo ./install.sh
   ```

2. **Place your radar CSV file:**
   ```bash
   sudo cp your_radars.csv /home/pi/radar-detector/radars.csv
   ```

3. **Configure WiFi (if not already done):**
   ```bash
   sudo wpa_passphrase "YOUR_WIFI_SSID" "YOUR_WIFI_PASSWORD" >> /etc/wpa_supplicant/wpa_supplicant.conf
   ```

4. **Reboot:**
   ```bash
   sudo reboot
   ```

## CSV Format

Your radar database should be in this format:
```
51436;ETT;2021-11-15;49.241198;3.031432;50
51437;ETT;2021-11-18;48.390184;-2.627093;80
```

Columns: `ID;TYPE;DATE;LATITUDE;LONGITUDE;SPEED_LIMIT`

## Manual Usage

```bash
python3 radar_detector_auto.py /path/to/radars.csv [wifi_ssid] [wifi_password]
```

## System Management

- **Check status:** `sudo systemctl status radar_detector.service`
- **View logs:** `sudo journalctl -u radar_detector.service -f`
- **Stop service:** `sudo systemctl stop radar_detector.service`
- **Start service:** `sudo systemctl start radar_detector.service`
- **Disable auto-start:** `sudo systemctl disable radar_detector.service`

## Hardware Requirements

- Raspberry Pi with GPS module
- USB speaker or audio output
- WiFi capability
- SD card with Raspberry Pi OS

## Audio Configuration

The system uses the existing TTS configuration with espeak and manages USB power automatically.

## Troubleshooting

1. **No GPS signal**: Check GPS module connection and wait for satellite lock
2. **WiFi issues**: Verify credentials in `/etc/wpa_supplicant/wpa_supplicant.conf`
3. **Audio problems**: Check audio device with `aplay -l`
4. **Service not starting**: Check logs with `journalctl -u radar_detector.service`