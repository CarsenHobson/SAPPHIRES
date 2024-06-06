import paho.mqtt.client as mqtt
import sqlite3
import ast

MQTT_BROKER = "10.42.0.1"
MQTT_PORT = 1883

def on_publish(client, userdata, result):
    pass

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_publish = on_publish
client.connect(MQTT_BROKER, MQTT_PORT, 60)

client.publish('Initiate Transfer', 'Start', qos=1)

TOPICS_TABLES = {
    'Transfer dataZeroW1': 'dataZeroW1',
    'Transfer dataZeroW2': 'dataZeroW2',
    'Transfer dataZeroW3': 'dataZeroW3',
    'Transfer dataZeroW4': 'dataZeroW4'
}

# SQLite database path
DB_PATH = '/Users/carsenhobson/downloads/new_mqtt_data.db'

# Create tables in the new database
def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for table in TOPICS_TABLES.values():
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table} (
                column1 INTEGER,  -- Adjust columns and types as per your data
                column2 TEXT,
                column3 REAL,
                column4 REAL,
                column5 REAL,
                column6 REAL
            )
        ''')
    conn.commit()
    conn.close()

# Insert data into the appropriate SQLite database table
def insert_data_to_db(table_name, data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(f"INSERT INTO {table_name} (column1, column2, column3, column4, column5, column6) VALUES (?, ?, ?, ?, ?, ?)", data)
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

# MQTT on_connect callback
def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("Connected to MQTT Broker!")
        for topic in TOPICS_TABLES.keys():
            client.subscribe(topic)
    else:
        print(f"Failed to connect, return code {rc}")

# MQTT on_message callback
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    topic = msg.topic
    table_name = TOPICS_TABLES.get(topic)

    if table_name:
        try:
            data = ast.literal_eval(payload)  # Convert string back to tuple
            if isinstance(data, tuple) and len(data) == 6:
                insert_data_to_db(table_name, data)
                print(f"Inserted data into {table_name}: {data}")
            else:
                print(f"Invalid data format: {data}")
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing data: {e}")
    else:
        print(f"No matching table for topic: {topic}")

# Main function to setup MQTT client and start loop
def main():
    create_tables()
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == '__main__':
    main()
