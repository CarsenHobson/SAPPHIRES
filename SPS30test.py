import time
import pandas as pd
import RPi.GPIO as GPIO
import psutil
import json
from sps30 import SPS30

# Initialize GPIO for relay control
RELAY_PIN = 19
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

# Initialize SPS30 sensor
sps = SPS30(1)  # I2C interface, address 0x69
sps.begin()

# Define constants
BASELINE_DURATION = 30 * 60  # 30 minutes for baseline
WINDOW_DURATION = 10 * 60  # 10 minutes for each window
BASELINE_THRESHOLD = 0.1  # 10% of baseline value
DATA_LOG_INTERVAL = 60  # Log data every 60 seconds

# File path for JSON data log
LOG_FILE_PATH = "sps30_data.json"

# Function to check if the Raspberry Pi is connected to Wi-Fi
def is_connected_to_wifi():
    try:
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == psutil.AF_INET and not addr.address.startswith("127."):
                    return True
        return False
    except Exception as e:
        print(f"Error checking Wi-Fi status: {str(e)}")
        return False

# Create a function to read SPS30 data and check for rising edges
def check_rising_edge():
    baseline_data = []
    start_time = time.time()
    baseline_finished = False
    relay_state = GPIO.LOW  # Initialize relay state to off

    while True:
        if time.time() - start_time < BASELINE_DURATION:
            # Collect baseline data
            data = sps.read_measurement()
            if data:
                baseline_data.append(data)
        else:
            if not baseline_finished:
                # Calculate the baseline value as the average
                baseline_pm2_5 = sum([entry['pm2_5'] for entry in baseline_data]) / len(baseline_data)
                print(f"Baseline PM2.5: {baseline_pm2_5} µg/m³")
                baseline_finished = True

            # Start monitoring for rising edges
            window_start_time = time.time()
            window_data = []

            while time.time() - window_start_time < WINDOW_DURATION:
                data = sps.read_measurement()
                if data:
                    window_data.append(data)

                # Calculate the average PM2.5 for the current window
                window_pm2_5 = sum([entry['pm2_5'] for entry in window_data]) / len(window_data)

                # Check if the average exceeds the threshold
                if window_pm2_5 > baseline_pm2_5 * (1 + BASELINE_THRESHOLD):
                    print(f"Rising edge detected! PM2.5: {window_pm2_5} µg/m³")
                    GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn on the relay
                    relay_state = GPIO.HIGH
                else:
                    GPIO.output(RELAY_PIN, GPIO.LOW)  # Turn off the relay
                    relay_state = GPIO.LOW

                # Log the data (including relay state) to the JSON file
                log_data(window_data, relay_state)

                # Send data to the remote server if connected to Wi-Fi
                if is_connected_to_wifi():
                    send_data_to_server(window_data)

            # Wait for a while before starting the next window
            time.sleep(10)

# Function to log data (including relay state) to the JSON file
def log_data(data, relay_state):
    try:
        with open(LOG_FILE_PATH, "a") as json_file:
            for entry in data:
                entry_with_relay = {"pm2_5": entry['pm2_5'], "relay_state": relay_state}
                json.dump(entry_with_relay, json_file)
                json_file.write("\n")
    except Exception as e:
        print(f"Error writing to JSON file: {str(e)}")

try:
    if is_connected_to_wifi():
        print("Connected to Wi-Fi")
    check_rising_edge()
except KeyboardInterrupt:
    # Cleanup GPIO on Ctrl+C
    GPIO.cleanup()
