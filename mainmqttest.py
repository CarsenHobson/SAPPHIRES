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

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    # Since we subscribed only for a single channel, reason_code_list contains
    # a single entry
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")
# MQTT on_connect callback
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
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

        print(f"Updated MQTT values: {mqtt_values}")

        # Determine the appropriate log file based on the topic
        if msg.topic == LOCAL_MQTT_TOPIC1:
            log_data(mqtt_values, LOG_FILE_PATH1)
        elif msg.topic == LOCAL_MQTT_TOPIC2:
            log_data(mqtt_values, LOG_FILE_PATH2)
        elif msg.topic == LOCAL_MQTT_TOPIC3:
            log_data(mqtt_values, LOG_FILE_PATH3)
        elif msg.topic == LOCAL_MQTT_TOPIC4:
            log_data(mqtt_values, LOG_FILE_PATH4)

    except Exception as e:
        error_message = f"Error processing MQTT message: {e}"

        # Determine if the error is from the main Raspberry Pi or the Raspberry Pi Zero Ws
        if msg.topic in [LOCAL_MQTT_TOPIC1, LOCAL_MQTT_TOPIC2, LOCAL_MQTT_TOPIC3, LOCAL_MQTT_TOPIC4]:
            error_origin = "Raspberry Pi Zero Ws"
        else:
            error_origin = "Main Raspberry Pi"

        # Log the error message along with the origin
        log_error(error_message, error_origin)

# Function to log errors to a JSON file
def log_error(error_message, error_origin):
    current_time = int(time.time())
    error_entry = {
        "timestamp": current_time,
        "error_message": error_message,
        "error_origin": error_origin
    }
    try:
        with open("error_log.json", "a") as error_file:
            error_file.write(json.dumps(error_entry) + "\n")
    except Exception as e:
        print(f"Error writing to error log file: {str(e)}")



# Function to generate a random 8-character alphanumeric key for each entry
def generate_random_key():
    import string
    import secrets
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(8))
if __name__ == "__main__":
    try:
        create_json_files()
        local_mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        local_mqtt_client.username_pw_set("SAPPHIRE", "SAPPHIRE")
        local_mqtt_client.on_connect = on_connect
        local_mqtt_client.on_message = on_message
        local_mqtt_client.connect(LOCAL_MQTT_BROKER, LOCAL_MQTT_PORT)

        # Start the MQTT client loop in a non-blocking manner
        local_mqtt_client.loop_start()

        # Sleep for a specified duration to allow time for processing messages
        time.sleep(20)  # You can adjust this sleep duration as needed

    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected. Code is stopped.")
    finally:
        local_mqtt_client.loop_stop()
        local_mqtt_client.disconnect()
