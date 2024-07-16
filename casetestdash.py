import time
import json
import tkinter as tk
from sps30 import SPS30
import sys
import sqlite3
import paho.mqtt.client as mqtt

sps = SPS30(1)

DATABASE_FILE = "casetest.db"

# MQTT Configuration
MQTT_BROKER = "10.42.0.1"
MQTT_PORT = 1883
MQTT_TOPIC1 = "No case"
MQTT_TOPIC2 = "Small case"

# Function to setup the SQLite database
def setup_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS main_case (
                        timestamp INTEGER,
                        pm2_5 REAL
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS small_case (
                        timestamp INTEGER,
                        pm2_5 REAL
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS no_case (
                        timestamp INTEGER,
                        pm2_5 REAL
                    )''')
    conn.commit()
    conn.close()

# Function to log data to the SQLite database
def log_data(table, pm2_5):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {table} (timestamp, pm2_5) VALUES (?, ?)", (int(time.time()), pm2_5))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error writing to SQLite database: {str(e)}")

# Function to setup the SPS30 sensor

# Function to update PM2.5 value in GUI
def update_pm25_label():
    sps.read_measured_values()
    data = sps.dict_values['pm2p5']
    log_data("main_case", data)
    pm25_label1.config(text=f"PM2.5 (Main case): {data} µg/m³")
    pm25_label1.after(1000, update_pm25_label)  # Update every 1000ms (1 second)

# Callback when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe([(MQTT_TOPIC1, 0), (MQTT_TOPIC2, 0)])

# Callback when a PUBLISH message is received from the server
def on_message(client, userdata, msg):
    data = float(msg.payload.decode())
    if msg.topic == MQTT_TOPIC1:
        log_data("no_case", data)
        pm25_label2.config(text=f"PM2.5 (No case): {data} µg/m³")
    elif msg.topic == MQTT_TOPIC2:
        log_data("small_case", data)
        pm25_label3.config(text=f"PM2.5 (Small case): {data} µg/m³")

if __name__ == "__main__":
    try:
        setup_database()
        setup_sps30()

        # Create Tkinter window
        window = tk.Tk()
        window.title("PM2.5 Dashboard")

        # Get screen width and height
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Set window size and position
        window.geometry(f"{screen_width}x{screen_height}+0+0")

        # Create labels to display PM2.5 data
        pm25_label1 = tk.Label(window, text="", font=("Arial", 36))
        pm25_label1.pack(expand=True, fill=tk.BOTH)

        pm25_label2 = tk.Label(window, text="", font=("Arial", 36))
        pm25_label2.pack(expand=True, fill=tk.BOTH)

        pm25_label3 = tk.Label(window, text="", font=("Arial", 36))
        pm25_label3.pack(expand=True, fill=tk.BOTH)

        # Start updating PM2.5 value in GUI
        update_pm25_label()

        # Setup MQTT client
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()

        # Run Tkinter event loop
        window.mainloop()

    except KeyboardInterrupt:
        sps.stop_measurement()
        sys.exit()
        print("\nKeyboard interrupt detected. SPS30 turned off.")
