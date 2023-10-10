import time
import RPi.GPIO as GPIO
import json
import os
from sps30 import SPS30
import paho.mqtt.client as mqtt

# Initialize GPIO for relay control
RELAY_PIN = 19
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

# Initialize SPS30 sensor
sps = SPS30(1)

# MQTT broker settings
MQTT_BROKER = "your_mqtt_broker_address"
MQTT_PORT = 1883
MQTT_TOPIC = "your_mqtt_topic"
MQTT_USERNAME = "your_mqtt_username"
MQTT_PASSWORD = "your_mqtt_password"

# Define constants
BASELINE_DURATION = 1 * 60
WINDOW_DURATION = 10 * 60
BASELINE_THRESHOLD = 0.1
READING_INTERVAL = 3
LOG_INTERVAL = 60

# File path for JSON data log
LOG_FILE_PATH = "sps30_data.json"

# Function to create the JSON file if it doesn't exist
def create_json_file():
    if not os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "w") as json_file:
            json_file.write("[]")

# Function to generate a random 8-character alphanumeric key for each entry
def generate_random_key():
    import string
    import secrets
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(8)

# Function to log data (including relay state) to the JSON file
def log_data(data, relay_state):
    try:
        with open(LOG_FILE_PATH, "a") as json_file:
            entry_with_timestamp_and_key = {
                "timestamp": int(time.time()),  # Add UNIX timestamp
                "key": generate_random_key(),  # Generate a new random key for each entry
                "pm2_5": data,
                "relay_state": relay_state
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
    baseline_data = []
    start_time = time.time()
    baseline_finished = False
    relay_state = GPIO.LOW
    setup_sps30()

    log_timer = time.time()
    log_interval = 60

    # Create an MQTT client instance
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.connect(MQTT_BROKER, MQTT_PORT)

    while True:
        if time.time() - start_time < BASELINE_DURATION:
            sps.read_measured_values()
            data = sps.dict_values['pm2p5']
            if data:
                baseline_data.append(data)
        else:
            if not baseline_finished:
                baseline_pm25 = sum(baseline_data) / len(baseline_data)
                print(f"Baseline PM2.5: {baseline_pm25} µg/m³")
                baseline_finished = True

            window_start_time = time.time()
            window_data = []

            while time.time() - window_start_time < WINDOW_DURATION:
                sps.read_measured_values()
                data = sps.dict_values['pm2p5']
                if data:
                    window_data.append(data)

                if window_data:
                    window_pm2_5 = sum(window_data) / len(window_data)
                else:
                    window_pm2_5 = 0.0

                if window_pm2_5 > baseline_pm25 * (1 + BASELINE_THRESHOLD):
                    print(f"Rising edge detected! PM2.5: {window_pm2_5} µg/m³")
                    GPIO.output(RELAY_PIN, GPIO.HIGH)
                    relay_state = GPIO.HIGH
                else:
                    GPIO.output(RELAY_PIN, GPIO.LOW)
                    relay_state = GPIO.LOW

                if time.time() - log_timer >= log_interval:
                    log_data(window_pm2_5, relay_state)
                    log_timer = time.time()

                    # Publish the data over MQTT with error handling
                    try:
                        mqtt_data = {
                            "timestamp": int(time.time()),
                            "pm2_5": window_pm2_5,
                            "relay_state": relay_state
                        }
                        client.publish(MQTT_TOPIC, json.dumps(mqtt_data))
                    except Exception as e:
                        print(f"MQTT publish error: {str(e)}")

                time.sleep(READING_INTERVAL)

            time.sleep(10)

# Start monitoring for rising edges
if __name__ == "__main__":
    try:
    
        create_json_file()  # Create the JSON file if it doesn't exist
        check_rising_edge()
    
    except KeyboardInterrupt:
        sps.stop_measurement()
        print("\nKeyboard interrupt detected. SPS30 turned off.")

