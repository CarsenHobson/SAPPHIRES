import paho.mqtt.client as mqtt
import time
import sqlite3
from datetime import datetime

# Define the MQTT broker and topic
broker_address = "10.42.0.1"
topic = "ZeroW1"

# SQLite setup
db_file = 'pm25_data.db'


def init_db():
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Create a table to store PM2.5 data if it doesn't already exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pm25_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            pm25_value REAL NOT NULL
        )
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()


# Function to insert data into the database
def insert_data(pm25_value):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Insert the PM2.5 value and timestamp into the database
    cursor.execute('''
        INSERT INTO pm25_data (timestamp, pm25_value)
        VALUES (?, ?)
    ''', (timestamp, pm25_value))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


# Callback function to handle incoming messages
def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8").strip()
    print(f"Received message: '{payload}'")

    try:
        pm25_value = float(payload)
        print(f"PM2.5 Value: {pm25_value} µg/m³")

        # Store the PM2.5 value in the database
        insert_data(pm25_value)

    except ValueError:
        print("Received message is not a valid floating-point number.")


# Callback function to confirm subscription
def on_subscribe(client, userdata, mid, granted_qos):
    print(f"Subscribed to topic with QoS {granted_qos[0]}")


# Setup the MQTT client
client = mqtt.Client()

# Attach callback functions
client.on_message = on_message
client.on_subscribe = on_subscribe

# Connect to the broker
client.connect(broker_address)

# Subscribe to the topic
client.subscribe(topic)

# Initialize the SQLite database
init_db()

# Start the MQTT loop (use loop_forever to ensure it runs continuously)
client.loop_start()

time.sleep(59)

client.loop_stop()

