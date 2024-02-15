import time
import RPi.GPIO as GPIO
import json
import os
import paho.mqtt.client as mqtt
import requests
import ast
# Initialize GPIO for relay control
RELAY_PIN = 19
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

# Define the URL to perform the Google search
google_search_url = "https://www.google.com"

# Define a timeout for the request (in seconds)
timeout = 5

# MQTT broker settings
LOCAL_MQTT_BROKER = "10.42.0.1"
LOCAL_MQTT_PORT = 1883
LOCAL_MQTT_TOPIC = "test/topic"

REMOTE_MQTT_BROKER = "10.42.0.1"
REMOTE_MQTT_PORT = 1883
REMOTE_MQTT_TOPIC = "Maindata"
REMOTE_MQTT_USERNAME = "SAPPHIRE"
REMOTE_MQTT_PASSWORD = "SAPPHIRE"

# Define constants
BASELINE_DURATION = 30 * 60
WINDOW_DURATION = 10 * 60
BASELINE_THRESHOLD = 0.1
READING_INTERVAL = 3
LOG_INTERVAL = 60

# File path for JSON data log
LOG_FILE_PATH = "sps30_data.json"

# Initialize global variables
mqtt_values = {"pm2.5": 0, "temperature": 0, "humidity": 0, "pressure": 0}
baseline_pm25 = 0

# Create the JSON file if it doesn't exist
def create_json_file():
    if not os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "w") as json_file:
            json_file.write("[]")

# Function to log data (including relay state) to the JSON file
def log_data(data, relay_state):
    current_time = int(time.time())
    entry_with_timestamp_and_key = {
        "timestamp": current_time,
        "key": generate_random_key(),
        **data,
        "relay_state": relay_state
    }
    try:
        with open(LOG_FILE_PATH, "a") as json_file:
            json_file.write(json.dumps(entry_with_timestamp_and_key) + "\n")
    except Exception as e:
        print(f"Error writing to JSON file: {str(e)}")

# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(LOCAL_MQTT_TOPIC)
# MQTT on_message callback
def on_message(client, userdata, msg):
    global mqtt_values

    try:
        data_str = msg.payload.decode("utf-8")  # Convert the MQTT message to a string
        data_dict = ast.literal_eval(data_str)  # Safely evaluate the string as a dictionary
        print(f"Received MQTT values: {data_dict}")

        if "PM2.5" in data_dict:
            mqtt_values["pm2.5"] = data_dict["PM2.5"]
        if "Temperature (F)" in data_dict:
            mqtt_values["temperature"] = data_dict["Temperature (F)"]
        if "Humidity (%)" in data_dict:
            mqtt_values["humidity"] = data_dict["Humidity (%)"]
        if "Pressure (hPa)" in data_dict:
            mqtt_values["pressure"] = data_dict["Pressure (hPa)"]
    except ValueError:
        pass

# Create an MQTT client instance for local MQTT
local_mqtt_client = mqtt.Client()
local_mqtt_client.on_connect = on_connect
local_mqtt_client.on_message = on_message
local_mqtt_client.connect(LOCAL_MQTT_BROKER, LOCAL_MQTT_PORT)
local_mqtt_client.loop_start()

# Create an MQTT client instance for remote MQTT
remote_mqtt_client = mqtt.Client()
remote_mqtt_client.username_pw_set(REMOTE_MQTT_USERNAME, REMOTE_MQTT_PASSWORD)
remote_mqtt_client.connect(REMOTE_MQTT_BROKER, REMOTE_MQTT_PORT)

# Function to generate a random 8-character alphanumeric key for each entry
def generate_random_key():
    import string
    import secrets
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(8))



# Function to check for rising edges
def check_rising_edge():
    global baseline_pm25

    baseline_data = []
    start_time = time.time()
    baseline_finished = False
    relay_state = GPIO.LOW  # Initialize relay state to off
    log_timer = time.time()  # Initialize the log timer
    log_interval = 60  # Log data every 60 seconds

    # Track whether it's time to collect baseline or monitor for rising edges
    collecting_baseline = True

    while True:
        current_time = time.time()

        if collecting_baseline:
            # Collect baseline data
            data = mqtt_values
            data["pm2.5"] = float(data["pm2.5"])  # Use the global MQTT value for pm2.5
            print(f"Received MQTT values: {data}")

            baseline_data.append(data["pm2.5"])

            if current_time - start_time >= BASELINE_DURATION:
                if not baseline_finished:
                    # Calculate the baseline value as the average
                    baseline_pm25 = sum(baseline_data) / len(baseline_data)
                    print(f"Baseline PM2.5: {baseline_pm25} µg/m³")
                    baseline_finished = True

                # Transition to the next phase
                start_time = current_time
                collecting_baseline = False

        else:
            # Monitor for rising edges
            data = mqtt_values
            data["pm2.5"] = float(data["pm2.5"])  # Use the global MQTT value for pm2.5
            print(f"Received MQTT values: {data}")

            if data["pm2.5"] > baseline_pm25 * (1 + BASELINE_THRESHOLD):
                print(f"Rising edge detected! PM2.5: {data['pm2.5']} µg/m³")
                GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn on the relay
                relay_state = GPIO.HIGH
            else:
                GPIO.output(RELAY_PIN, GPIO.LOW)  # Turn off the relay
                relay_state = GPIO.LOW

            # Log the data (including relay state) to the JSON file
            log_data(data, relay_state)

            # Check Wi-Fi connectivity and publish to remote MQTT based on Google search result
            try:
                # Send an HTTP GET request to Google to check Wi-Fi connectivity
                response = requests.get(google_search_url, timeout=timeout)

                if response.status_code // 100 == 2:
                    print("Connected to Wi-Fi. Google search succeeded")

                    # Publish data to the remote MQTT broker
                    data_to_publish = {
                        "timestamp": int(current_time),
                        **data,
                        "relay_state": relay_state,
                        "status": "Connected to Wi-Fi"
                    }
                    remote_mqtt_client.publish(REMOTE_MQTT_TOPIC, json.dumps(data_to_publish))
                else:
                    print("Google search failed. Wi-Fi may not be connected")

                    # Add your action here if the connection is not successful
            except requests.RequestException:
                print("Failed to perform the Google search. Wi-Fi may not be connected")

                # Add your action here if the request itself fails (e.g., network issue)

        # Wait for a while before checking again
        time.sleep(10)

if __name__ == "__main__":
    try:
        create_json_file()
        check_rising_edge()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected. Code is stopped.")
