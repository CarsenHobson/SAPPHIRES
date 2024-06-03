import time
import os
import ast
import logging
import secrets
import string
import sqlite3
import paho.mqtt.client as mqtt

# MQTT broker settings
LOCAL_MQTT_BROKER = "10.42.0.1"
LOCAL_MQTT_PORT = 1883
LOCAL_MQTT_TOPICS = ["ZeroW1", "ZeroW2", "ZeroW3", "ZeroW4"]
MQTT_USERNAME = "SAPPHIRE"
MQTT_PASSWORD = "SAPPHIRE"

# Initialize logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    handlers=[logging.FileHandler("app.log"),
                              logging.StreamHandler()])

# MQTT values
mqtt_values = {"pm2.5": 0, "temperature": 0, "humidity": 0, "Wifi Strength": 0}

# Database setup
DATABASE_NAME = "mqtt_data.db"
TABLES = {
    "ZeroW1": "CREATE TABLE IF NOT EXISTS ZeroW1 (timestamp INTEGER, key TEXT, pm25 REAL, temperature REAL, humidity REAL, wifi_strength REAL)",
    "ZeroW2": "CREATE TABLE IF NOT EXISTS ZeroW2 (timestamp INTEGER, key TEXT, pm25 REAL, temperature REAL, humidity REAL, wifi_strength REAL)",
    "ZeroW3": "CREATE TABLE IF NOT EXISTS ZeroW3 (timestamp INTEGER, key TEXT, pm25 REAL, temperature REAL, humidity REAL, wifi_strength REAL)",
    "ZeroW4": "CREATE TABLE IF NOT EXISTS ZeroW4 (timestamp INTEGER, key TEXT, pm25 REAL, temperature REAL, humidity REAL, wifi_strength REAL)"
}
ERROR_LOG_TABLE = "CREATE TABLE IF NOT EXISTS error_log (timestamp INTEGER, error_message TEXT, error_origin TEXT)"

def setup_database():
    """Setup the SQLite database and create tables."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    for table_query in TABLES.values():
        cursor.execute(table_query)
    cursor.execute(ERROR_LOG_TABLE)
    conn.commit()
    conn.close()

def log_data(data, table_name):
    """Log data to the specified SQLite table."""
    current_time = int(time.time())
    entry_with_timestamp_and_key = (
        current_time,
        generate_random_key(),
        data.get("pm2.5", 0),
        data.get("temperature", 0),
        data.get("humidity", 0),
        data.get("Wifi Strength", 0),
    )
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {table_name} (timestamp, key, pm25, temperature, humidity, wifi_strength) VALUES (?, ?, ?, ?, ?, ?)", entry_with_timestamp_and_key)
        conn.commit()
        conn.close()
        logging.info(f"Inserted data into {table_name}: {entry_with_timestamp_and_key}")
    except Exception as e:
        logging.error(f"Error writing to database table {table_name}: {e}")

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    """Handle MQTT subscription acknowledgment."""
    if reason_code_list[0].is_failure:
        logging.warning(f"Broker rejected subscription: {reason_code_list[0]}")
    else:
        logging.info(f"Broker granted QoS: {reason_code_list[0].value}")

def on_connect(client, userdata, flags, reason_code):
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
        if "Wifi Strength" in data_dict:
            mqtt_values["Wifi Strength"] = data_dict["Wifi Strength"]
        logging.info(f"Updated MQTT values: {mqtt_values}")

        table_name = msg.topic
        if table_name in TABLES:
            log_data(mqtt_values, table_name)

    except Exception as e:
        error_message = f"Error processing MQTT message: {e}"
        log_error(error_message, "Raspberry Pi Zero Ws" if msg.topic in LOCAL_MQTT_TOPICS else "Main Raspberry Pi")

def log_error(error_message, error_origin):
    """Log errors to the SQLite database."""
    current_time = int(time.time())
    error_entry = (current_time, error_message, error_origin)
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO error_log (timestamp, error_message, error_origin) VALUES (?, ?, ?)", error_entry)
        conn.commit()
        conn.close()
        logging.info(f"Logged error: {error_entry}")
    except Exception as e:
        logging.error(f"Error writing to error log database: {e}")

def generate_random_key():
    """Generate a random 8-character alphanumeric key."""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(8))

def retry_connect(client, max_retries=5):
    """Retry MQTT connection with exponential backoff."""
    delay = 1
    for attempt in range(max_retries):
        try:
            client.connect(LOCAL_MQTT_BROKER, LOCAL_MQTT_PORT)
            return
        except Exception as e:
            logging.error(f"MQTT connection attempt {attempt + 1} failed: {e}")
            time.sleep(delay)
            delay *= 2
    logging.error("Max retries reached. Exiting.")
    exit(1)

def main():
    """Main function to run the MQTT client."""
    setup_database()

    local_mqtt_client = mqtt.Client()
    local_mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    local_mqtt_client.on_connect = on_connect
    local_mqtt_client.on_message = on_message

    retry_connect(local_mqtt_client)

    try:
        local_mqtt_client.loop_start()
        # Allow time for processing messages
        time.sleep(20)  # You can adjust this sleep duration as needed
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt detected. Stopping.")
    finally:
        local_mqtt_client.loop_stop()
        local_mqtt_client.disconnect()

if __name__ == "__main__":
    main()

