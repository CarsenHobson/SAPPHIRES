import sqlite3
import paho.mqtt.client as mqtt

# MQTT settings
MQTT_BROKER = '10.42.0.1'  # Example broker
MQTT_PORT = 1883
MQTT_TOPIC = 'Transfer Data'  # Replace with your topic

# SQLite database path
DB_PATH = '/home/Mainhub/mqtt_data.db'

# Fetch data from the SQLite database
def fetch_data_from_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM data")  # Replace 'data' with your table name
    rows = cursor.fetchall()
    conn.close()
    return rows

# Publish data to MQTT topic
def publish_data(client, data):
    for row in data:
        payload = str(row)  # Convert row data to string
        client.publish(MQTT_TOPIC, payload)
        print(f"Published: {payload}")

# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        data = fetch_data_from_db()
        publish_data(client, data)
    else:
        print("Failed to connect, return code %d\n", rc)

# Main function to setup MQTT client and start loop
def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == '__main__':
    main()
