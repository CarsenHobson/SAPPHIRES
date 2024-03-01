import time
import RPi.GPIO as GPIO
import json
import os
import paho.mqtt.client as mqtt
import requests
import ast

# MQTT broker settings
LOCAL_MQTT_BROKER = "10.42.0.1"
LOCAL_MQTT_PORT = 1883
LOCAL_MQTT_TOPIC1 = "ZeroW1"
LOCAL_MQTT_TOPIC2 = "ZeroW2"
LOCAL_MQTT_TOPIC3 = "ZeroW3"
LOCAL_MQTT_TOPIC4 = "ZeroW4"

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
LOG_FILE_PATH1 = "Data1.json"
LOG_FILE_PATH2 = "Data2.json"
LOG_FILE_PATH3 = "Data3.json"
LOG_FILE_PATH4 = "Data4.json"

# Initialize global variables
mqtt_values = {"pm2.5": 0, "temperature": 0, "humidity": 0}

# Create the JSON files if they don't exist
def create_json_files():
    for path in [LOG_FILE_PATH1, LOG_FILE_PATH2, LOG_FILE_PATH3, LOG_FILE_PATH4]:
        if not os.path.exists(path):
            with open(path, "w") as json_file:
                json_file.write("[]")

# Function to log data (including relay state) to the JSON file
def log_data(data, log_file_path):
    current_time = int(time.time())
    entry_with_timestamp_and_key = {
        "timestamp": current_time,
        "key": generate_random_key(),
        **data,
    }
    try:
        with open(log_file_path, "a") as json_file:
            json_file.write(json.dumps(entry_with_timestamp_and_key) + "\n")
    except Exception as e:
        print(f"Error writing to JSON file: {str(e)}")

# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe([(LOCAL_MQTT_TOPIC1, 0), (LOCAL_MQTT_TOPIC2, 0), (LOCAL_MQTT_TOPIC3, 0), (LOCAL_MQTT_TOPIC4, 0)])

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

        # Determine the appropriate log file based on the topic
        if msg.topic == LOCAL_MQTT_TOPIC1:
            log_data(mqtt_values, LOG_FILE_PATH1)
        elif msg.topic == LOCAL_MQTT_TOPIC2:
            log_data(mqtt_values, LOG_FILE_PATH2)
        elif msg.topic == LOCAL_MQTT_TOPIC3:
            log_data(mqtt_values, LOG_FILE_PATH3)
        elif msg.topic == LOCAL_MQTT_TOPIC4:
            log_data(mqtt_values, LOG_FILE_PATH4)

    except ValueError:
        pass


# Function to generate a random 8-character alphanumeric key for each entry
def generate_random_key():
    import string
    import secrets
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(8))

if __name__ == "__main__":
    try:
        create_json_files()
        local_mqtt_client = mqtt.Client()
        local_mqtt_client.on_connect = on_connect
        local_mqtt_client.on_message = on_message
        local_mqtt_client.connect(LOCAL_MQTT_BROKER, LOCAL_MQTT_PORT)
        local_mqtt_client.loop_start()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected. Code is stopped.")
