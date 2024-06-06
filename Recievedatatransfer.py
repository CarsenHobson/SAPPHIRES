import sqlite3
import paho.mqtt.client as mqtt
import ast

# MQTT settings
MQTT_BROKER = '10.42.0.1'  # Example broker
MQTT_PORT = 1883
MQTT_TOPIC = 'Transfer Data'  # Replace with your topic

# SQLite database path
DB_PATH = '/home/data/data.db'

# Create table in new database
def create_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data (
            column1 TEXT,  -- Adjust columns and types as per your data
            column2 TEXT   -- Adjust columns and types as per your data
        )
    ''')
    conn.commit()
    conn.close()

# Insert data into the SQLite database
def insert_data_to_db(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO data (column1, column2) VALUES (?, ?)", data)
    conn.commit()
    conn.close()

# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
    else:
        print("Failed to connect, return code %d\n", rc)

# MQTT on_message callback
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    data = ast.literal_eval(payload)  # Convert string back to tuple
    insert_data_to_db(data)
    print(f"Inserted data: {data}")

# Main function to setup MQTT client and start loop
def main():
    create_table()
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == '__main__':
    main()
