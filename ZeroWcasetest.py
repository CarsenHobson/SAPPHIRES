import time
import sqlite3
import threading
import logging
from sps30 import SPS30

# Configure logging
logging.basicConfig(filename='air_quality_log.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')

# Function to initialize the SQLite database
def initialize_db():
    try:
        conn = sqlite3.connect('air_quality.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS air_quality
                     (timestamp TEXT, pm2_5 REAL)''')
        conn.commit()
        conn.close()
        logging.info("Database initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")

# Function to log PM2.5 data to the SQLite database
def log_data(pm2_5):
    try:
        conn = sqlite3.connect('air_quality.db')
        c = conn.cursor()
        c.execute("INSERT INTO air_quality (timestamp, pm2_5) VALUES (datetime('now'), ?)", (pm2_5,))
        conn.commit()
        conn.close()
        logging.info(f"Logged PM2.5 data: {pm2_5}")
    except Exception as e:
        logging.error(f"Error logging data: {e}")

# Function to read data from the SPS30 sensor continuously
def read_sps30():
    sensor = SPS30(1)  # 1 indicates the I2C bus number
    sensor.start_measurement()
    time.sleep(2)  # Wait for the first measurement to be ready

    try:
        while True:
            sensor.read_measured_values()
            data = sensor.dict_values['pm2p5']
            if data is not None:
                pm2_5 = data
                log_data(pm2_5)
            time.sleep(0.5)  # Update every 0.5 seconds
    except KeyboardInterrupt:
        logging.info("Measurement stopped by user.")
    except Exception as e:
        logging.error(f"Error reading from SPS30 sensor: {e}")
    finally:
        pass

# Function to fetch the latest PM2.5 data from the SQLite database
def fetch_latest_data():
    try:
        conn = sqlite3.connect('air_quality.db')
        c = conn.cursor()
        c.execute("SELECT pm2_5 FROM air_quality ORDER BY timestamp DESC LIMIT 1")
        data = c.fetchone()
        conn.close()
        return data[0] if data else None
    except Exception as e:
        logging.error(f"Error fetching latest data: {e}")
        return None

# Initialize the SQLite database
initialize_db()

# Start the data reading thread
threading.Thread(target=read_sps30, daemon=True).start()

# Keep the main thread alive
try:
    while True:
        latest_data = fetch_latest_data()
        if latest_data is not None:
            print(f"Latest PM2.5 Level: {latest_data:.10f} µg/m³")
        else:
            print("No data available")
        time.sleep(1)  # Print the latest data every second
except KeyboardInterrupt:
    logging.info("Main thread stopped by user.")
except Exception as e:
    logging.error(f"Error in the main thread: {e}")
