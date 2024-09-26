import time
import sqlite3
from sps30 import SPS30

sps = SPS30(1)

DATABASE_PATH = "indoor.db"

# Function to initialize the SQLite database
def initialize_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create a table for storing data if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sps30_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            pm2_5 REAL NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

# Function to log data to the SQLite database
def log_data_to_db(pm2_5):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Insert data into the table
        cursor.execute('''
            INSERT INTO sps30_data (timestamp, pm2_5)
            VALUES (?, ?)
        ''', (int(time.time()), pm2_5))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error writing to SQLite database: {str(e)}")

# Function to setup the SPS30 sensor
def setup_sps30():
    sps.start_measurement()
    time.sleep(2)

if __name__ == "__main__":
    try:
        # Initialize the database
        initialize_database()
        
        # Setup the SPS30 sensor
        setup_sps30()
        
        # Read sensor data once
        sps.read_measured_values()
        data = sps.dict_values['pm2p5']
        
        # Log the data to the SQLite database
        log_data_to_db(data)
        
        # Stop the sensor
        sps.stop_measurement()
        print("Data logged successfully and SPS30 turned off.")

    except KeyboardInterrupt:
        sps.stop_measurement()
        print("\nKeyboard interrupt detected. SPS30 turned off.")

