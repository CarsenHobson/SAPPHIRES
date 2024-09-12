import time
import sys
import sqlite3
from datetime import datetime
import RPi.GPIO as GPIO

# Constants
DATABASE_FILE_PATH = 'pm25_data.db'  # Using the same database from the first code
WINDOW_SIZE = 20  # Number of readings to consider
RELAY_PIN = 14  # GPIO pin to control

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

# Ensure the relay is initially off
GPIO.output(RELAY_PIN, GPIO.LOW)

# Database connection
try:
    connection = sqlite3.connect(DATABASE_FILE_PATH)
    cursor = connection.cursor()
except sqlite3.Error as e:
    print(f"Error connecting to database: {str(e)}")
    sys.exit(1)

# Data storage
pm25_values = []
timestamp_values = []

def fetch_last_20_rows_columns():
    """Fetch the last 20 rows of PM2.5 and timestamp from the pm25_data table."""
    try:
        cursor.execute("SELECT pm25_value, timestamp FROM pm25_data ORDER BY id DESC LIMIT 20")
        rows = cursor.fetchall()
        pm25_values.clear()
        timestamp_values.clear()
        for pm25_value, timestamp in rows:
            pm25_values.append(pm25_value)
            timestamp_values.append(timestamp)
    except sqlite3.Error as e:
        print(f"Error fetching data from database: {str(e)}")

def read_baseline_value():
    """Read the baseline PM2.5 value from the database."""
    try:
        cursor.execute("SELECT baseline_pm2_5 FROM BaselineValue ORDER BY timestamp DESC LIMIT 5")
        rows = cursor.fetchall()
        if len(rows) > 1:
            baseline_values = [row[0] for row in rows]
            average_baseline_values = sum(baseline_values) / len(baseline_values)
            latest_baseline = baseline_values[0]
            valid_baseline_values = [value for value in baseline_values[1:] if value <= 1.5 * baseline_values[1]]

            if latest_baseline > 1.5 * average_baseline_values:
                if valid_baseline_values:
                    previous_baseline = valid_baseline_values[0]
                else:
                    previous_baseline = baseline_values[1]
                print("Latest baseline value is too high, using the previous valid baseline value.")
                return 7.5
            else:
                return latest_baseline
        elif len(rows) == 1:
            return rows[0][0]
        else:
            return 7.5  # Default to 7.5 if no baseline values are found
    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")
        return 7.5  # Default to 7.5 in case of a database error

def check_rising_edge():
    """Check for a rising edge in PM2.5 levels, update the database, and control GPIO."""
    baseline_pm25 = read_baseline_value()

    # Ensure baseline is at least 7.5
    if baseline_pm25 < 7.5:
        baseline_pm25 = 7.5

    fetch_last_20_rows_columns()

    current_time = time.time()
    one_hour_ago = current_time - 3600

    if len(pm25_values) >= WINDOW_SIZE and all(float(datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").timestamp()) >= one_hour_ago for timestamp in timestamp_values):
        threshold = 1.25
        relay_state = 'ON' if all(data_point > threshold * baseline_pm25 for data_point in pm25_values) else 'OFF'
    else:
        print(f"Not enough data points ({len(pm25_values)}) out of {WINDOW_SIZE}. Skipping rising edge calculation.")
        relay_state = 'OFF'

    # Control the GPIO based on relay state
    if relay_state == 'ON':
        GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn on relay
        print("Relay turned ON")
    else:
        GPIO.output(RELAY_PIN, GPIO.LOW)  # Turn off relay
        print("Relay turned OFF")

    # Insert the relay state into the pm25_data table
    try:
        cursor.execute('''UPDATE pm25_data SET relaystate = ? WHERE id = (SELECT MAX(id) FROM pm25_data)''', (relay_state,))
        connection.commit()
    except sqlite3.Error as e:
        print(f"Error updating relay state in the database: {str(e)}")

if __name__ == "__main__":
    try:
        check_rising_edge()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        # Cleanup GPIO and close database connection
        GPIO.cleanup()
        connection.close()
