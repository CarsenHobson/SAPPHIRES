import time
import os
import json
import ast
import logging
import secrets
import string
import paho.mqtt.client as mqtt

# MQTT broker settings (Consider moving these to a configuration file)
LOCAL_MQTT_BROKER = "10.42.0.1"
LOCAL_MQTT_PORT = 1883
LOCAL_MQTT_TOPICS = ["ZeroW1", "ZeroW2", "ZeroW3", "ZeroW4"]

# File paths for JSON data log
LOG_FILE_PATHS = {
    "ZeroW1": "Data1.json",
    "ZeroW2": "Data2.json",
    "ZeroW3": "Data3.json",
    "ZeroW4": "Data4.json"
}
ERROR_LOG_FILE = "error_log.json"

# Initialize global variables
mqtt_values = {"pm2.5": 0, "temperature": 0, "humidity": 0}

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def create_json_files():
    """Create JSON files if they do not exist."""
    for path in LOG_FILE_PATHS.values():
        if not os.path.exists(path):
            with open(path, "w") as json_file:
                json_file.write("[]")
    if not os.path.exists(ERROR_LOG_FILE):
        with open(ERROR_LOG_FILE, "w") as error_file:
            error_file.write("[]")

def log_data(data, log_file_path):
    """Log data to the specified JSON file."""
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
        logging.error(f"Error writing to JSON file {log_file_path}: {e}")

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    """Handle MQTT subscription acknowledgment."""
    if reason_code_list[0].is_failure:
        logging.warning(f"Broker rejected subscription: {reason_code_list[0]}")
    else:
        logging.info(f"Broker granted QoS: {reason_code_list[0].value}")

def on_connect(client, userdata, flags, reason_code, properties):
    """Handle MQTT connection event."""
    logging.info(f"Connected with result code {reason_code}")
    client.subscribe([(topic, 0) for topic in LOCAL_MQTT_TOPICS])

def on_message(client, userdata, msg):
    """Handle incoming MQTT messages."""
    global mqtt_values

    try:
        data_str = msg.payload.decode("utf-8")
        data_dict = ast.literal_eval(data_str)
        logging.info(f"Received MQTT values: {data_dict}")

        if "PM2.5" in data_dict:
            mqtt_values["pm2.5"] = data_dict["PM2.5"]
        if "Temperature (F)" in data_dict:
            mqtt_values["temperature"] = data_dict["Temperature (F)"]
        if "Humidity (%)" in data_dict:
            mqtt_values["humidity"] = data_dict["Humidity (%)"]

        logging.info(f"Updated MQTT values: {mqtt_values}")

        log_file_path = LOG_FILE_PATHS.get(msg.topic)
        if log_file_path:
            log_data(mqtt_values, log_file_path)

    except Exception as e:
        error_message = f"Error processing MQTT message: {e}"
        log_error(error_message, "Raspberry Pi Zero Ws" if msg.topic in LOCAL_MQTT_TOPICS else "Main Raspberry Pi")

def log_error(error_message, error_origin):
    """Log errors to a JSON file."""
    current_time = int(time.time())
    error_entry = {
        "timestamp": current_time,
        "error_message": error_message,
        "error_origin": error_origin
    }
    try:
        with open(ERROR_LOG_FILE, "a") as error_file:
            error_file.write(json.dumps(error_entry) + "\n")
    except Exception as e:
        logging.error(f"Error writing to error log file: {e}")

def generate_random_key():
    """Generate a random 8-character alphanumeric key."""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(8))

def main():
    """Main function to run the MQTT client."""
    create_json_files()

    local_mqtt_client = mqtt.Client()
    local_mqtt_client.username_pw_set("SAPPHIRE", "SAPPHIRE")
    local_mqtt_client.on_connect = on_connect
    local_mqtt_client.on_message = on_message

    try:
        local_mqtt_client.connect(LOCAL_MQTT_BROKER, LOCAL_MQTT_PORT)
        local_mqtt_client.loop_start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt detected. Stopping.")
    finally:
        local_mqtt_client.loop_stop()
        local_mqtt_client.disconnect()

if __name__ == "__main__":
    main()
