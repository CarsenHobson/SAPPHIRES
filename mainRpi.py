import time
import RPi.GPIO as GPIO
import json
import os
from sps30 import SPS30
import bme280  # Ensure you have this library installed

# Initialize GPIO for relay control
RELAY_PIN = 19
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

# Initialize SPS30 sensor
sps = SPS30(1)

# Initialize BME280 sensor
bme280.setup()

# Define constants
BASELINE_FILE_PATH = "baseline.json"
LOG_FILE_PATH = "main.json"
WINDOW_SIZE = 10  # Number of readings to consider
BASELINE_THRESHOLD = 0.1
READING_INTERVAL = 3

# Function to generate a random 8-character alphanumeric key for each entry
def generate_random_key():
    import string
    import secrets
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(8))

# Function to read baseline value from a file
def read_baseline_value():
    try:
        with open(BASELINE_FILE_PATH, "r") as baseline_file:
            baseline_data = json.load(baseline_file)
            return baseline_data.get("baseline_pm25", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

# Function to read the last 10 measurements from the main file or use the last 10 baseline values
def read_last_10_measurements():
    try:
        with open(LOG_FILE_PATH, "r") as log_file:
            log_data = json.load(log_file)
            last_10_measurements = [entry.get("pm2_5", read_baseline_value()) for entry in log_data[-10:]]
            return last_10_measurements
    except (FileNotFoundError, json.JSONDecodeError, IndexError):
        return [read_baseline_value()] * 10

# Function to log data (including relay state, PM2.5, BME280, and baseline) to the JSON file
def log_data(pm2_5, relay_state, bme280_data, baseline_pm25):
    try:
        with open(LOG_FILE_PATH, "a") as json_file:
            entry_with_timestamp_and_key = {
                "timestamp": int(time.time()),  # Add UNIX timestamp
                "key": generate_random_key(),  # Generate a new random key for each entry
                "pm2_5": pm2_5,
                "relay_state": relay_state,
                "bme280_data": {
                    "temperature": bme280_data["temperature"],
                    "humidity": bme280_data["humidity"]
                },
                "baseline_pm25": baseline_pm25
            }
            json_file.write(json.dumps(entry_with_timestamp_and_key) + "\n")
    except Exception as e:
        print(f"Error writing to JSON file: {str(e)}")

# Function to setup the SPS30 sensor
def setup_sps30():
    sps.start_measurement()
    time.sleep(2)

# Function to check for rising edges
def check_rising_edge():
    relay_state = GPIO.LOW
    baseline_pm25 = read_baseline_value()

    # Check if there is no data in the main file
    last_10_measurements = read_last_10_measurements()

    if all(value > baseline_pm25 * (1 + BASELINE_THRESHOLD) for value in last_10_measurements):
        print(f"All last 10 measurements were above the baseline. Turning on relay.")
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        relay_state = GPIO.HIGH
    else:
        GPIO.output(RELAY_PIN, GPIO.LOW)
        relay_state = GPIO.LOW

    bme280_data = bme280.readData()
    log_data(last_10_measurements[-1], relay_state, bme280_data, baseline_pm25)

# Function to stop the SPS30 measurement
def stop_sps30():
    sps.stop_measurement()

if __name__ == "__main__":
    try:
        sps = SPS30(1)
        setup_sps30()

        while True:
            check_rising_edge()
            time.sleep(READING_INTERVAL)

    except KeyboardInterrupt:
        sps.stop_measurement()
        print("\nKeyboard interrupt detected. SPS30 turned off.")
