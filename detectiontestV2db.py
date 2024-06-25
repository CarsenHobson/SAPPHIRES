import time
import sys
from sps30 import SPS30
import Adafruit_BME280
from datetime import datetime
import sqlite3
import string
import secrets

# Constants
DATABASE_FILE_PATH = 'detectiontest.db'
LOG_FILE_PATH = "main.json"
WINDOW_SIZE = 20  # Number of readings to consider
BASELINE_THRESHOLD1 = 0.5
BASELINE_THRESHOLD2 = 0.25

# Database connection
connection = sqlite3.connect(DATABASE_FILE_PATH)
cursor = connection.cursor()

# Initialize sensors
sps = SPS30(1)
bme280 = Adafruit_BME280.BME280(address=0x77)

# Data storage
pm25_values = []
timestamp_values = []

def fetch_last_20_rows_columns():
    """Fetch the last 20 rows of PM2.5 and timestamp from the database."""
    cursor.execute("SELECT pm25, timestamp FROM detectiontestV2 ORDER BY rowid DESC LIMIT 20")
    rows = cursor.fetchall()
    for row in rows:
        pm2_5, timestamp = row
        pm25_values.append(pm2_5)
        timestamp_values.append(timestamp)

def is_between_5am_and_6am():
    """Check if the current time is between 5 AM and 6 AM."""
    current_time = int(datetime.now().strftime('%H%M'))
    return 500 <= current_time <= 559

def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9 / 5) + 32

def generate_random_key():
    """Generate a random key of 8 characters."""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(8))

def read_baseline_value():
    """Read the baseline PM2.5 value from the database."""
    try:
        cursor.execute("SELECT baseline_pm2_5 FROM BaselineValue ORDER BY timestamp DESC LIMIT 5")
        rows = cursor.fetchall()
        if len(rows) > 1:
            baseline_values = [row[0] for row in rows]
            latest_baseline = baseline_values[0]
            valid_baseline_values = [value for value in baseline_values[1:] if value <= 1.5 * baseline_values[1]]
            
            if latest_baseline > 1.5 * baseline_values[1]:
                if valid_baseline_values:
                    previous_baseline = valid_baseline_values[0]
                else:
                    previous_baseline = baseline_values[1]
                print("Latest baseline value is too high, using the previous valid baseline value.")
                return previous_baseline
            else:
                return latest_baseline
        elif len(rows) == 1:
            return rows[0][0]
        else:
            return 0
    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")
        return 0

def check_rising_edge():
    """Check for a rising edge in PM2.5 levels and update the database."""
    baseline_pm25 = read_baseline_value()
    temperature_celsius = bme280.read_temperature()
    temperature = celsius_to_fahrenheit(temperature_celsius)
    humidity = bme280.read_humidity()
    sps.read_measured_values()
    data = sps.dict_values['pm2p5']
    current_time = time.time()
    one_hour_ago = current_time - 3600
    fetch_last_20_rows_columns()

    if baseline_pm25 >= 10:
        process_data(data, temperature, humidity, baseline_pm25, one_hour_ago, 1.25)
    else:
        process_data(data, temperature, humidity, baseline_pm25, one_hour_ago, 1.5)

def process_data(data, temperature, humidity, baseline_pm25, one_hour_ago, threshold):
    """Process the data and insert into the database."""
    if len(pm25_values) >= WINDOW_SIZE and all(timestamp >= one_hour_ago for timestamp in timestamp_values):
        if all(data_point > threshold * baseline_pm25 for data_point in pm25_values):
            relay_state = 'ON'
        else:
            relay_state = 'OFF'
    else:
        print(f"Not enough data points ({len(pm25_values)}) out of {WINDOW_SIZE}). Skipping rising edge calculation.")
        relay_state = 'OFF'

    cursor.execute('''INSERT INTO detectiontestV2 (key, timestamp, pm25, temperature, humidity, baselinepm25, relaystate) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)''', (1, int(time.time()), data, temperature, humidity, baseline_pm25, relay_state))

if __name__ == "__main__":
    try:
        if is_between_5am_and_6am():
            sys.exit()
        else:
            check_rising_edge()
            connection.commit()
            connection.close()
    except KeyboardInterrupt:
        sps.stop_measurement()
        print("\nKeyboard interrupt detected. SPS30 turned off.")
