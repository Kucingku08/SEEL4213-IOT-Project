import os
import time
import logging
import requests
import board
import sqlite3
import adafruit_dht
from dotenv import load_dotenv
from datetime import datetime
# Load environment variables
load_dotenv()

# Configuration
PIN = os.getenv("DHT11_GPIO", "D4")
BLYNK_TOKEN = os.getenv("BLYNK_AUTH_TOKEN")
BLYNK_BASE = "https://blynk.cloud/external/api"
DB_FILE = "sensor_data.db"
# Initialize DHT11 sensor
dht_device = adafruit_dht.DHT11(board.D4)


def read_dht11(retries=5, delay=2.0):
    """
    Read temperature and humidity from DHT11 sensor.
    """
    for i in range(retries):
        try:
            temperature = dht_device.temperature
            humidity = dht_device.humidity

            if temperature is not None and humidity is not None:
                return round(temperature, 1), round(humidity, 1)

        except RuntimeError as e:
            logging.warning(
                f"DHT11 read failed (attempt {i + 1}/{retries}): {e}"
            )

        time.sleep(delay)

    raise RuntimeError("DHT11 sensor not responding")


def send_to_blynk(temp, humidity):
    """
    Send data to Blynk Cloud.
    """
    if not BLYNK_TOKEN:
        raise RuntimeError("BLYNK_AUTH_TOKEN not set in .env")

    # Temperature -> V0
    r1 = requests.get(
        f"{BLYNK_BASE}/update",
        params={
            "token": BLYNK_TOKEN,
            "V0": temp
        },
        timeout=5
    )
    r1.raise_for_status()

    # Humidity -> V1
    r2 = requests.get(
        f"{BLYNK_BASE}/update",
        params={
            "token": BLYNK_TOKEN,
            "V1": humidity
        },
        timeout=5
    )
    r2.raise_for_status()

def save_reading(temperature, humidity):
    timestamp = datetime.now().isoformat()

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO readings (timestamp, temperature, humidity, synced)
            VALUES (?, ?, ?, 0)
            """,
            (timestamp, temperature, humidity)
        )
        return cursor.lastrowid


def mark_as_synced(reading_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE readings
            SET synced = 1
            WHERE id = ?
            """,
            (reading_id,)
        )

def send_to_blynk_safe(temp, humidity, reading_id):
    try:
        send_to_blynk(temp, humidity)
        mark_as_synced(reading_id)
        return True

    except Exception as e:
        logging.warning(
            f"Cloud send failed: {e}. Data buffered."
        )
        return False


def resend_unsynced():
    """Retry all unsent data."""

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, temperature, humidity
            FROM readings
            WHERE synced = 0
            """
        )

        for reading_id, temp, hum in cursor.fetchall():
            send_to_blynk_safe(temp, hum, reading_id)

if __name__ == "__main__":
    while True:
        logging.basicConfig(level=logging.INFO)

        try:
            temp, hum = read_dht11()

       	    print(f"Temperature: {temp}°C")
            print(f"Humidity: {hum}%")

            try:
                reading_id = save_reading(temp, hum)
                send_to_blynk_safe(temp, hum, reading_id)
                logging.info("Data sent to Blynk")

            except requests.exceptions.Timeout:
                logging.error("Blynk timeout - saved locally")

            except requests.exceptions.ConnectionError:
                logging.error("Network unavailable")

            except Exception as e:
                logging.error(f"Unexpected error: {e}")

        except Exception as e:
            print(f"Sensor Error: {e}")
        
        time.sleep(10)
