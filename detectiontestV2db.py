import time
import sys
from sps30 import SPS30, SPS30Exception
import Adafruit_BME280
from datetime import datetime
import sqlite3

# Constants
DATABASE_FILE_PATH = 'detectiontest.db'
WINDOW_SIZE = 20  # Number of readings to consider

# Database connection
try:
    connection = sqlite3.connect(DATABASE_FILE_PATH)
    cursor = connection.cursor()
except sqlite3.Error as e:
    print(f"Error connecting to database: {str(e)}")
    sys.exit(1)

# Initialize sensors
try:
    sps = SPS30(1)
except SPS30Exception as e:
    print(f"Error initializing SPS30 sensor: {str(e)}")
    sys.exit(1)

try:
    bme280 = Adafruit_BME280.BME280(address=0x77)
except Exception as e:
    print(f"Error initializing BME280 sensor: {str(e)}")
    sys.exit(1)

# Data storage
pm25_values = []
timestamp_values = []

def fetch_last_20_rows_columns():
    """Fetch the last 20 rows of PM2.5 and timestamp from the database."""
    try:
        cursor.execute("SELECT pm25, timestamp FROM detectiontestV2 ORDER BY rowid DESC LIMIT 20")
        rows = cursor.fetchall()
        for pm2_5, timestamp in rows:
            pm25_values.append(pm2_5)
            timestamp_values.append(timestamp)
    except sqlite3.Error as e:
        print(f"Error fetching data from database: {str(e)}")

def is_between_5am_and_6am():
    """Check if the current time is between 5 AM and 6 AM."""
    current_time = int(datetime.now().strftime('%H%M'))
    return 500 <= current_time <= 559

def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9 / 5) + 32

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
            return 10  # Default to 10 if no baseline values are found
    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")
        return 10  # Default to 10 in case of a database error

def check_rising_edge():
    """Check for a rising edge in PM2.5 levels and update the database."""
    baseline_pm25 = read_baseline_value()

    # Ensure baseline is at least 10
    if baseline_pm25 < 10:
        baseline_pm25 = 10

    try:
        temperature_celsius = bme280.read_temperature()
        temperature = celsius_to_fahrenheit(temperature_celsius)
        humidity = bme280.read_humidity()
    except Exception as e:
        print(f"Error reading BME280 sensor data: {str(e)}")
        return

    try:
        sps.read_measured_values()
        data = sps.dict_values['pm2p5']
    except SPS30Exception as e:
        print(f"Error reading SPS30 sensor data: {str(e)}")
        return

    current_time = time.time()
    one_hour_ago = current_time - 3600
    fetch_last_20_rows_columns()

    if len(pm25_values) >= WINDOW_SIZE and all(timestamp >= one_hour_ago for timestamp in timestamp_values):
        threshold = 1.25
        relay_state = 'ON' if all(data_point > threshold * baseline_pm25 for data_point in pm25_values) else 'OFF'
    else:
        print(f"Not enough data points ({len(pm25_values)}) out of {WINDOW_SIZE}). Skipping rising edge calculation.")
        relay_state = 'OFF'

    try:
        cursor.execute('''INSERT INTO detectiontestV2 (key, timestamp, pm25, temperature, humidity, baselinepm25, relaystate) 
                          VALUES (?, ?, ?, ?, ?, ?, ?)''', (1, int(time.time()), data, temperature, humidity, baseline_pm25, relay_state))
    except sqlite3.Error as e:
        print(f"Error inserting data into database: {str(e)}")

if __name__ == "__main__":
    try:
        if is_between_5am_and_6am():
            sys.exit()
        else:
            check_rising_edge()
            connection.commit()
            connection.close()
    except KeyboardInterrupt:
        try:
            sps.stop_measurement()
        except SPS30Exception as e:
            print(f"Error stopping SPS30 measurement: {str(e)}")
        print("\nKeyboard interrupt detected. SPS30 turned off.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        try:
            connection.close()
        except sqlite3.Error as e:
            print(f"Error closing the database connection: {str(e)}")

