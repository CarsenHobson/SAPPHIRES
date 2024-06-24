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


# SQLite database path
DB_PATH = '/Users/carsenhobson/downloads/detectiontestnew.db'

# Create tables in the new database
def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table} (
            column1 INTEGER,  -- Adjust columns and types as per your data
            column2 REAL,
            column3 REAL,
            column4 REAL,
            column5 REAL,
            column6 REAL,
            column7 STRING
        )
    ''')
    conn.commit()
    conn.close()

# Insert data into the appropriate SQLite database table
def insert_data_to_db(table_name, data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(f"INSERT INTO {table_name} (column1, column2, column3, column4, column5, column6, column7) VALUES (?, ?, ?, ?, ?, ?, ?)", data)
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
    data = ast.literal_eval(payload)  # Convert string back to tuple


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
