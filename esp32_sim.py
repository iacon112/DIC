"""
ESP32 Simulator — sends fake DHT11 sensor readings every 5 seconds
via HTTP POST to the Flask API.
"""

import time
import random
import json
import urllib.request
import urllib.error

FLASK_URL = "http://127.0.0.1:5000/sensor"

# Simulated ESP32 metadata
DEVICE_ID = "ESP32-AIOT-001"
SSID = "HomeNetwork_5G"
IP_ADDRESS = "192.168.1.42"


def generate_dht11_reading():
    """Generate a fake DHT11 sensor reading."""
    return {
        "device_id": DEVICE_ID,
        "ssid": SSID,
        "ip_address": IP_ADDRESS,
        "temperature": round(random.uniform(18.0, 38.0), 1), 
        "humidity": round(random.uniform(40.0, 80.0), 1), 
    }


def send_reading(payload):
    """POST the payload to the Flask /sensor endpoint."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        FLASK_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
            body = json.loads(resp.read())
            print(f"[ESP32] POST {FLASK_URL} → {status}  {body}  |  "
                  f"temp={payload['temperature']}°C  hum={payload['humidity']}%")
    except urllib.error.URLError as e:
        print(f"[ESP32] ERROR: {e}")


def main():
    print(f"[ESP32] Simulator started — device_id={DEVICE_ID}")
    print(f"[ESP32] Posting to {FLASK_URL} every 5 seconds\n")
    while True:
        reading = generate_dht11_reading()
        send_reading(reading)
        time.sleep(5)


if __name__ == "__main__":
    main()
