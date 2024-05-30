import sqlite3
from datetime import datetime, timedelta

DATABASE_NAME = 'your_database_name.db'  # Replace with your actual database name

MQTT_BROKER = "10.42.0.1"
MQTT_PORT = 1883
MQTT_USERNAME = "SAPPHIRE"
MQTT_PASSWORD = "SAPPHIRE"

client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.on_publish = on_publish
client.connect(BROKER_ADDRESS, MQTT_PORT, 60)

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
    current_time = datetime.now()
    ten_minutes_ago = current_time - timedelta(minutes=10)
    older_than_10_minutes = {}
    
    for table, timestamp in latest_values.items():
        if timestamp:
            timestamp_datetime = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            older_than_10_minutes[table] = timestamp_datetime < ten_minutes_ago
            
        else:
            older_than_10_minutes[table] = None
    
    return older_than_10_minutes

# Example usage
latest_timestamps = get_latest_timestamp()
timestamps_check = check_timestamps_older_than_10_minutes(latest_timestamps)
print(timestamps_check)
