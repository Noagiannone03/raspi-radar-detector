#!/usr/bin/env python3
import os
import time
import subprocess
import csv
import math
import threading
from typing import List, Tuple, Optional
import json

class GPSRadarDetector:
    def __init__(self, csv_file_path: str, wifi_ssid: str = None, wifi_password: str = None):
        self.csv_file_path = csv_file_path
        self.wifi_ssid = wifi_ssid
        self.wifi_password = wifi_password
        self.radar_points = []
        self.current_location = None
        self.detection_radius = 300  # meters
        self.last_alert_time = {}
        self.alert_cooldown = 30  # seconds
        self.running = False

    def usb_power_on(self):
        """Turn on USB power"""
        os.system("echo '1-1' | sudo tee /sys/bus/usb/drivers/usb/bind > /dev/null 2>&1")

    def usb_power_off(self):
        """Turn off USB power"""
        os.system("echo '1-1' | sudo tee /sys/bus/usb/drivers/usb/unbind > /dev/null 2>&1")

    def speak(self, text: str):
        """Speak text using espeak with power management"""
        print(f"Speaking: {text}")
        self.usb_power_on()
        time.sleep(0.5)

        os.system(f'espeak -s 160 -p 50 -a 100 "{text}" --stdout | aplay -D plughw:0,0')

        time.sleep(0.5)
        self.usb_power_off()

    def check_wifi_connection(self) -> bool:
        """Check if WiFi is connected"""
        try:
            result = subprocess.run(['iwgetid', '-r'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0 and result.stdout.strip()
        except:
            return False

    def connect_wifi(self) -> bool:
        """Connect to WiFi if not already connected"""
        if self.check_wifi_connection():
            return True

        self.speak("Connecting to WiFi")

        try:
            if self.wifi_ssid and self.wifi_password:
                cmd = f'sudo wpa_passphrase "{self.wifi_ssid}" "{self.wifi_password}" >> /etc/wpa_supplicant/wpa_supplicant.conf'
                os.system(cmd)

            os.system("sudo wpa_cli -i wlan0 reconfigure")
            time.sleep(10)

            if self.check_wifi_connection():
                self.speak("WiFi connection established. Starting laser radar detection.")
                return True
            else:
                self.speak("WiFi connection failed")
                return False

        except Exception as e:
            print(f"WiFi connection error: {e}")
            self.speak("WiFi connection error")
            return False

    def load_radar_database(self):
        """Load radar points from CSV file with optimization"""
        print("Loading radar database...")
        self.radar_points = []

        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file, delimiter=';')
                for row in csv_reader:
                    if len(row) >= 6:
                        try:
                            radar_id = row[0]
                            lat = float(row[3])
                            lon = float(row[4])
                            speed_limit = int(row[5])

                            self.radar_points.append({
                                'id': radar_id,
                                'lat': lat,
                                'lon': lon,
                                'speed_limit': speed_limit
                            })
                        except (ValueError, IndexError):
                            continue

            print(f"Loaded {len(self.radar_points)} radar points")

        except FileNotFoundError:
            print(f"Radar database file not found: {self.csv_file_path}")
        except Exception as e:
            print(f"Error loading radar database: {e}")

    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two GPS points using Haversine formula"""
        R = 6371000  # Earth radius in meters

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def get_gps_location(self) -> Optional[Tuple[float, float]]:
        """Get current GPS location using gpsd"""
        try:
            result = subprocess.run(['gpspipe', '-w', '-n', '5'],
                                   capture_output=True, text=True, timeout=10)

            for line in result.stdout.split('\n'):
                if '"class":"TPV"' in line:
                    try:
                        data = json.loads(line)
                        if 'lat' in data and 'lon' in data:
                            return float(data['lat']), float(data['lon'])
                    except:
                        continue

        except Exception as e:
            print(f"GPS error: {e}")

        return None

    def check_nearby_radars(self, current_lat: float, current_lon: float) -> List[dict]:
        """Check for radars within detection radius using optimized search"""
        nearby_radars = []

        lat_range = self.detection_radius / 111000  # Approximate degrees per meter
        lon_range = self.detection_radius / (111000 * math.cos(math.radians(current_lat)))

        for radar in self.radar_points:
            if (abs(radar['lat'] - current_lat) <= lat_range and
                abs(radar['lon'] - current_lon) <= lon_range):

                distance = self.haversine_distance(
                    current_lat, current_lon,
                    radar['lat'], radar['lon']
                )

                if distance <= self.detection_radius:
                    radar['distance'] = distance
                    nearby_radars.append(radar)

        return sorted(nearby_radars, key=lambda x: x['distance'])

    def alert_radar(self, radar: dict):
        """Alert for detected radar with cooldown"""
        radar_id = radar['id']
        current_time = time.time()

        if (radar_id in self.last_alert_time and
            current_time - self.last_alert_time[radar_id] < self.alert_cooldown):
            return

        self.last_alert_time[radar_id] = current_time

        distance = int(radar['distance'])
        speed_limit = radar['speed_limit']

        alert_message = f"Attention! Radar detected {distance} meters ahead. Speed limit {speed_limit} kilometers per hour. Slow down!"

        print(f"🚨 RADAR ALERT: {alert_message}")
        self.speak(alert_message)

    def gps_monitoring_loop(self):
        """Main GPS monitoring loop"""
        print("Starting GPS monitoring...")

        while self.running:
            try:
                location = self.get_gps_location()

                if location:
                    current_lat, current_lon = location
                    self.current_location = location

                    print(f"Current location: {current_lat:.6f}, {current_lon:.6f}")

                    nearby_radars = self.check_nearby_radars(current_lat, current_lon)

                    for radar in nearby_radars:
                        self.alert_radar(radar)

                else:
                    print("No GPS signal")

                time.sleep(2)  # Check every 2 seconds

            except Exception as e:
                print(f"GPS monitoring error: {e}")
                time.sleep(5)

    def start_detection(self):
        """Start the radar detection system"""
        print("Starting Radar Detection System...")

        if not self.connect_wifi():
            print("Cannot start without WiFi connection")
            return False

        self.load_radar_database()

        if not self.radar_points:
            print("No radar data loaded")
            return False

        self.running = True

        gps_thread = threading.Thread(target=self.gps_monitoring_loop, daemon=True)
        gps_thread.start()

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_detection()

        return True

    def stop_detection(self):
        """Stop the radar detection system"""
        print("Stopping radar detection...")
        self.running = False
        self.speak("Radar detection stopped")

def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 radar_detector_auto.py <csv_file_path> [wifi_ssid] [wifi_password]")
        sys.exit(1)

    csv_file = sys.argv[1]
    wifi_ssid = sys.argv[2] if len(sys.argv) > 2 else None
    wifi_password = sys.argv[3] if len(sys.argv) > 3 else None

    detector = GPSRadarDetector(csv_file, wifi_ssid, wifi_password)

    try:
        detector.start_detection()
    except Exception as e:
        print(f"System error: {e}")
        detector.speak("System error occurred")

if __name__ == "__main__":
    main()