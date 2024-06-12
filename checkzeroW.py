import sqlite3
import time
import paho.mqtt.client as mqtt

DATABASE_NAME = 'mqtt_data.db'
MQTT_BROKER = "10.42.0.1"
MQTT_PORT = 1883
MQTT_USERNAME = "SAPPHIRE"
MQTT_PASSWORD = "SAPPHIRE"

def on_publish(client, userdata, result):
    pass

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.on_publish = on_publish
client.connect(MQTT_BROKER, MQTT_PORT, 60)

def get_latest_timestamp():
    query_template = "SELECT timestamp FROM {} ORDER BY timestamp DESC LIMIT 1"
    tables = ["ZeroW1", "ZeroW2", "ZeroW3", "ZeroW4"]
    latest_values = {}
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        for table in tables:
            cursor.execute(query_template.format(table))
            result = cursor.fetchone()
            latest_values[table] = result[0] if result else None
    
    return latest_values

def check_timestamps_older_than_10_minutes(latest_values):
    current_time = int(time.time())
    ten_minutes_ago = current_time - 600
    older_than_10_minutes = {}
    for table, timestamp in latest_values.items():
        if timestamp is not None:
            older_than_10_minutes[table] = timestamp < ten_minutes_ago
        else:
            older_than_10_minutes[table] = False
    
    return older_than_10_minutes

def reset_mqtt_by_number(table_number):
    table_mapping = {
        1: "ZeroW1",
        2: "ZeroW2",
        3: "ZeroW3",
        4: "ZeroW4"
    }
    table = table_mapping.get(table_number)
    if table:
        latest_values = get_latest_timestamp()
        older_than_10_minutes = check_timestamps_older_than_10_minutes(latest_values)
        if older_than_10_minutes.get(table, False):
            client.publish('Reset4', 'reboot', qos=1)
            print(f"Reset{table_number}")
        else:
            print(f"{table} does not need reset")
    else:
        print("Invalid table number. Please provide a number between 1 and 4.")

if __name__ == '__main__':
    for i in range(1, 5):
        reset_mqtt_by_number(i)




