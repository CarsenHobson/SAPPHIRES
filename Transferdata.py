import sqlite3
import paho.mqtt.client as mqtt

# MQTT settings
MQTT_BROKER = '10.42.0.1'  # Example broker
MQTT_PORT = 1883
MQTT_TOPIC_PREFIX = 'Transfer data'  # Topic prefix for each table

# SQLite database path
DB_PATH = '/home/Mainhub/mqtt_data.db'

# Fetch data from a specific table in the SQLite database
def fetch_data_from_table(table_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Publish data to MQTT topic
def publish_data(client, table_name, data):
    for row in data:
        payload = str(row)  # Convert row data to string
        topic = f"{MQTT_TOPIC_PREFIX}{table_name}"
        client.publish(topic, payload)
        print(f"Published to {topic}: {payload}")

# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        tables = ['ZeroW1', 'ZeroW2', 'ZeroW3', 'ZeroW4']  # Replace with your actual table names
        for table in tables:
            data = fetch_data_from_table(table)
            publish_data(client, table, data)
    else:
        print(f"Failed to connect, return code {rc}\n")

# Main function to setup MQTT client and start loop
def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == '__main__':
    main()
