#!/usr/bin/env python3
import os
import time

def usb_power_on():
    """Allumer l'alimentation USB"""
    # Activer l'alimentation USB (adaptez le numéro si nécessaire)
    os.system("echo '1-1' | sudo tee /sys/bus/usb/drivers/usb/bind > /dev/null 2>&1")

def usb_power_off():
    """Éteindre l'alimentation USB"""
    # Couper l'alimentation USB
    os.system("echo '1-1' | sudo tee /sys/bus/usb/drivers/usb/unbind > /dev/null 2>&1")

def speak(text):
    """Parler avec espeak en gérant l'alimentation"""
    print("Activation du haut-parleur...")
    usb_power_on()
    time.sleep(0.5)  # Laisser le temps au speaker de s'initialiser

    # Parler
    os.system(f'espeak -s 160 -p 50 -a 100 "{text}" --stdout | aplay -D plughw:0,0')

    time.sleep(0.5)  # Laisser finir complètement
    print("Désactivation du haut-parleur...")
    usb_power_off()

def radar_alert():
    """Alerte radar avec voix"""
    speak("Radar detected! Slow down immediately!")

if __name__ == "__main__":
    print("🚨 RADAR DÉTECTÉ! 🚨")
    radar_alert()
    print("Alerte terminée")