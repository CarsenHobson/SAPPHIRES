import sqlite3
import paho.mqtt.client as mqtt
import ast

# MQTT settings
MQTT_BROKER = 'broker.hivemq.com'  # Example broker
MQTT_PORT = 1883
MQTT_TOPIC_PREFIX = 'example/topic/'  # Topic prefix for each table

# SQLite database path
DB_PATH = '/mnt/data/new_mqtt_data.db'

# Create tables in new database
def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS table1 (
            column1 TEXT,  -- Adjust columns and types as per your data
            column2 TEXT   -- Adjust columns and types as per your data
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS table2 (
            column1 TEXT,  -- Adjust columns and types as per your data
            column2 TEXT   -- Adjust columns and types as per your data
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS table3 (
            column1 TEXT,  -- Adjust columns and types as per your data
            column2 TEXT   -- Adjust columns and types as per your data
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS table4 (
            column1 TEXT,  -- Adjust columns and types as per your data
            column2 TEXT   -- Adjust columns and types as per your data
        )
    ''')
    conn.commit()
    conn.close()

# Insert data into the SQLite database
def insert_data_to_db(table_name, data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO {table_name} (column1, column2) VALUES (?, ?)", data)
    conn.commit()
    conn.close()

# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        tables = ['table1', 'table2', 'table3', 'table4']  # Replace with your actual table names
        for table in tables:
            topic = f"{MQTT_TOPIC_PREFIX}{table}"
            client.subscribe(topic)
    else:
        print(f"Failed to connect, return code {rc}\n")

# MQTT on_message callback
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    data = ast.literal_eval(payload)  # Convert string back to tuple
    table_name = msg.topic.split('/')[-1]
    insert_data_to_db(table_name, data)
    print(f"Inserted data into {table_name}: {data}")

# Main function to setup MQTT client and start loop
def main():
    create_tables()
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == '__main__':
    main()
