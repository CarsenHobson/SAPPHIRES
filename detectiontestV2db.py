import time
import json
import sys
from sps30 import SPS30
import Adafruit_BME280
from datetime import datetime
import sqlite3

connection = sqlite3.connect('detectiontest.db')
cursor = connection.cursor()

# Initialize SPS30 sensor
sps = SPS30(1)

# Initialize BME280 sensor
bme280 = Adafruit_BME280.BME280(address=0x77)

# Define constants
BASELINE_FILE_PATH = "baseline_value.json"
LOG_FILE_PATH = "main.json"
WINDOW_SIZE = 20  # Number of readings to consider
BASELINE_THRESHOLD1 = 0.5
BASELINE_THRESHOLD2 = 0.25

pm25_values = []
timestamp_values = []

def fetch_last_20_rows_columns():
    cursor.execute("SELECT pm25, timestamp FROM detectiontestV2 ORDER BY rowid DESC LIMIT 20")

    rows = cursor.fetchall()
    
    for row in rows:
        pm25, timestamp = row
        pm25_values.append(pm25)
        timestamp_values.append(timestamp)
        

def is_between_5am_and_6am():
    # Get the current time in HHMM format
    current_time = int(datetime.now().strftime('%H%M'))

    # Check if it's between 05:00 and 05:59
    if 500 <= current_time <= 559:
        return True  # It's between 5 AM and 6 AM
    else:
        return False  # It's not between 5 AM and 6 AM



# Function to convert BME temp to Fahrenheit
def celsius_to_fahrenheit(celsius):
    return (celsius * 9 / 5) + 32


# Function to generate a random 8-character alphanumeric key for each entry
def generate_random_key():
    import string
    import secrets
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(8))


# Function to read baseline value from a file
def read_baseline_value():
    try:
        with open(BASELINE_FILE_PATH, "r") as baseline_file:
            baseline_data = json.load(baseline_file)
            return baseline_data.get("baseline_pm25", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0


# Function to setup the SPS30 sensor
def setup_sps30():
    sps.start_measurement()
    time.sleep(2)


def check_rising_edge():
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
        if len(pm25_values) >= WINDOW_SIZE and all(timestamp >= one_hour_ago for timestamp in timestamp_values):
            if all(data_point > 1.25 * baseline_pm25 for data_point in pm25_values):
                print(f"All last {WINDOW_SIZE} readings were above the baseline. Turning on relay.")
                relay_state = 'ON'
            else:
                relay_state = 'OFF'

            cursor.execute('''INSERT INTO detectiontestV2 VALUES(1, ?, ?, ?, ?, ?, ?)''', (int(time.time()), data, temperature, humidity, baseline_pm25, relay_state))


        else:
            print(f"Not enough data points ({len(pm25_values)}) out of {WINDOW_SIZE}). Skipping rising edge calculation.")
            relay_state = 'OFF'
            
            
            cursor.execute('''INSERT INTO detectiontestV2 VALUES(1, ?, ?, ?, ?, ?, ?)''', (int(time.time()), data, temperature, humidity, baseline_pm25, relay_state))

    if baseline_pm25 <= 10:

        if len(pm25_values) >= WINDOW_SIZE and all(timestamp >= one_hour_ago for timestamp in timestamp_values):                
       
            if all(data_point > 1.5 * baseline_pm25 for data_point in pm25_values):
                relay_state = 'ON'
        
            else:
            
                relay_state = 'OFF'
                cursor.execute('''INSERT INTO detectiontestV2 VALUES(1, ?, ?, ?, ?, ?, ?)''', (int(time.time()), data, temperature, humidity, baseline_pm25, relay_state))



        else:
            print( f"Not enough data points ({len(pm25_values)}) out of {WINDOW_SIZE}). Skipping rising edge calculation.")
            relay_state = 'OFF'
            cursor.execute('''INSERT INTO detectiontestV2 VALUES(1, ?, ?, ?, ?, ?, ?)''', (int(time.time()), data, temperature, humidity, baseline_pm25, relay_state))


    


if __name__ == "__main__":
    try:
        if is_between_5am_and_6am():
            sys.exit()
        else:
            setup_sps30()
            check_rising_edge()
            connection.commit()
            connection.close()
            sps.stop_measurement()
            
    except KeyboardInterrupt:
        sps.stop_measurement()
        print("\nKeyboard interrupt detected. SPS30 turned off.")
