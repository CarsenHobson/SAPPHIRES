import sqlite3
import time
from sps30 import SPS30

# File paths for database
DATABASE_FILE_PATH = "detectiontest.db"

sps = SPS30(1)

# Function to setup the SPS30 sensor
def setup_sps30():
    sps.start_measurement()
    time.sleep(2)

def check_recent_event():
    try:
        conn = sqlite3.connect(DATABASE_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT relaystate FROM detectiontestV2 ORDER BY timestamp DESC LIMIT 60")
        states = cursor.fetchall()
        
        # Check if all the last 60 relaystate values are "ON"
        if all(state[0] == "ON" for state in states):
            print("All last 60 relaystate values are 'ON'. Exiting.")
            exit()  # or you might want to raise an exception or handle this in another way
    except Exception as e:
        print(f"Error checking recent event: {str(e)}")
    finally:
        conn.close()

# Function to initialize the database
def initialize_database():
    conn = sqlite3.connect(DATABASE_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS BaselineData (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            pm2_5 REAL NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS BaselineValue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            baseline_pm2_5 REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to update the baseline value in the database
def update_baseline_value(baseline_value):
    try:
        timestamp = int(time.time())
        conn = sqlite3.connect(DATABASE_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO BaselineValue (timestamp, baseline_pm2_5)
            VALUES (?, ?)
        ''', (timestamp, baseline_value))
        conn.commit()
        conn.close()
        print("Baseline value updated in the database.")
        sps.stop_measurement()
    except Exception as e:
        print(f"Error updating baseline value: {str(e)}")

# Function to log PM2.5 data into the database
def log_data(pm2_5):
    try:
        timestamp = int(time.time())
        conn = sqlite3.connect(DATABASE_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO BaselineData (timestamp, pm2_5)
            VALUES (?, ?)
        ''', (timestamp, pm2_5))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error writing to the database: {str(e)}")

# Function to perform baseline measurement and update the database
def perform_baseline(baseline_duration=3600):  # Set the baseline duration in seconds
    baseline_data = []
    global baseline_pm25
    sps = SPS30(1)
    setup_sps30()
    pm2_5_values = []
    print(f"Performing baseline measurement for {baseline_duration} seconds...")

    start_time = time.time()

    while time.time() - start_time < baseline_duration:
        sps.read_measured_values()
        data = sps.dict_values['pm2p5']
        log_data(data)
        time.sleep(30)
    try:
        conn = sqlite3.connect(DATABASE_FILE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT pm2_5 FROM BaselineData ORDER BY timestamp DESC LIMIT 120')
        rows = cursor.fetchall()
        Last_20_PM25 = [row[0] for row in rows]

        baseline_pm25 = sum(Last_20_PM25) / 120

        print(f"Baseline PM2.5: {baseline_pm25} µg/m³")

        update_baseline_value(baseline_pm25)

    except Exception as e:
        print(f"{str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    initialize_database()
    try:
        perform_baseline()
        check_recent_event()
    except KeyboardInterrupt:
        sps.stop_measurement()
        print("\nKeyboard interrupt detected. SPS30 turned off.")
