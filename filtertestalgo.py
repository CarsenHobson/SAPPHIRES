import time
import sys
from datetime import datetime
import sqlite3

# Constants
DATABASE_FILE_PATH = 'pm25_data.db'
WINDOW_SIZE = 20  # Number of readings to consider

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
    """Fetch the last 20 rows of PM2.5 and timestamp from the database."""
    global pm25_values, timestamp_values
    pm25_values.clear()
    timestamp_values.clear()

    try:
        cursor.execute("SELECT pm25_value, timestamp FROM pm25_data ORDER BY rowid DESC LIMIT 20")
        rows = cursor.fetchall()
        for pm25_value, timestamp in rows:
            pm25_values.append(pm25_value)
            # Assuming the timestamp is a string in the format 'YYYY-MM-DD HH:MM:SS'
            timestamp_unix = time.mktime(datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").timetuple())
            timestamp_values.append(timestamp_unix)
    except sqlite3.Error as e:
        print(f"Error fetching data from database: {str(e)}")


def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9 / 5) + 32


def read_baseline_value():
    """Read the baseline PM2.5 value from the database."""
    try:
        cursor.execute("SELECT baseline FROM pm25_data ORDER BY timestamp DESC LIMIT 5")
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
            return 7.5  # Default if no baseline values are found
    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")
        return 7.5  # Default in case of a database error


def check_rising_edge():
    """Check for a rising edge in PM2.5 levels and update the database."""
    baseline_pm25 = read_baseline_value()

    # Ensure baseline is at least 7.5
    if baseline_pm25 < 7.5:
        baseline_pm25 = 7.5

    current_time = time.time()
    one_hour_ago = current_time - 3600
    fetch_last_20_rows_columns()

    if len(pm25_values) >= WINDOW_SIZE and all(timestamp >= one_hour_ago for timestamp in timestamp_values):
        threshold = 1.25
        relay_state = 'ON' if all(data_point > threshold * baseline_pm25 for data_point in pm25_values) else 'OFF'
    else:
        print(f"Not enough data points ({len(pm25_values)} out of {WINDOW_SIZE}). Skipping rising edge calculation.")
        relay_state = 'OFF'

    try:
        cursor.execute('''INSERT INTO pm25_data (filter_state) 
                          VALUES (?)''', (relay_state,))
    except sqlite3.Error as e:
        print(f"Error inserting data into database: {str(e)}")


if __name__ == "__main__":
    try:
        check_rising_edge()
        connection.commit()
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        try:
            connection.close()
        except sqlite3.Error as e:
            print(f"Error closing the database connection: {str(e)}")
