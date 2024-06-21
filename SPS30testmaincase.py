import time
import sqlite3
from sps30 import SPS30

# Function to initialize the SQLite database
def initialize_db():
    conn = sqlite3.connect('air_quality.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS air_quality
                 (timestamp TEXT, pm2_5 REAL)''')
    conn.commit()
    conn.close()

# Function to log PM2.5 data to the SQLite database
def log_data(pm2_5):
    conn = sqlite3.connect('air_quality.db')
    c = conn.cursor()
    c.execute("INSERT INTO air_quality (timestamp, pm2_5) VALUES (datetime('now'), ?)", (pm2_5,))
    conn.commit()
    conn.close()

# Function to read data from the SPS30 sensor continuously
def read_sps30():
    sensor = SPS30(1)  # 1 indicates the I2C bus number
    sensor.start_measurement()
    time.sleep(2)  # Wait for the first measurement to be ready

    try:
        while True:
            data = sensor.get_measurement()
            if data:
                pm2_5 = data['pm2.5']
                print(f"PM2.5 Level: {pm2_5} µg/m³")
                log_data(pm2_5)
            time.sleep(1)  # Read data every second
    except KeyboardInterrupt:
        print("Measurement stopped by user.")
    finally:
        sensor.stop_measurement()

if __name__ == "__main__":
    initialize_db()
    read_sps30()
