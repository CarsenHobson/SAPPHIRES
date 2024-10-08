import time
import json
import sys
from sps30 import SPS30
import Adafruit_BME280
from datetime import datetime
# Initialize GPIO for relay control
RELAY_PIN = 19
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

# Initialize SPS30 sensor
sps = SPS30(1)

# Initialize BME280 sensor
bme280 = Adafruit_BME280.BME280(address=0x77)

# Define constants
BASELINE_FILE_PATH = "baseline_value.json"
LOG_FILE_PATH = "main.json"
WINDOW_SIZE = 10  # Number of readings to consider
BASELINE_THRESHOLD1 = 0.5
BASELINE_THRESHOLD2 = 0.25


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


# Function to log data to the JSON file
def log_data(pm2_5, relay_state, temperature, humidity, baseline_pm25):
    try:
        with open(LOG_FILE_PATH, "a") as json_file:
            entry_with_timestamp_and_key = {
                "key": 1
                "timestamp": int(time.time()), 
                "pm2_5": pm2_5,
                "relay_state": relay_state,
                "temperature": temperature,
                "humidity": humidity,
                "baseline_pm25": baseline_pm25
            }
            json_file.write(json.dumps(entry_with_timestamp_and_key) + "\n")
    except Exception as e:
        print(f"Error writing to JSON file: {str(e)}")


# Function to setup the SPS30 sensor
def setup_sps30():
    sps.start_measurement()
    time.sleep(2)


def check_rising_edge():
    relay_state = GPIO.LOW
    baseline_pm25 = read_baseline_value()
    temperature_celsius = bme280.read_temperature()
    temperature = celsius_to_fahrenheit(temperature_celsius)
    humidity = bme280.read_humidity()
    sps.read_measured_values()
    data = sps.dict_values['pm2p5']
    pm2_5_values = []
    timestamp_values = []
    current_time = time.time()
    one_hour_ago = current_time - 3600
    try:
        with open(LOG_FILE_PATH, 'r') as file:
            for line in file:
                try:
                    json_data = json.loads(line)
                    pm2_5_values.append(json_data["pm2_5"])
                    timestamp_values.append(json_data["timestamp"])
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    # Handle the error as needed
            Last_10_PM25 = pm2_5_values[-20:]
            Last_10_timestamps =  timestamp_values[-20:]
            
            if baseline_pm25 >= 10:
                if len(pm2_5_values) >= WINDOW_SIZE and all(timestamp >= one_hour_ago for timestamp in Last_10_timestamps):
                    if all(data_point > 1.25 * baseline_pm25 for data_point in Last_10_PM25):
                        print(f"All last {WINDOW_SIZE} readings were above the baseline. Turning on relay.")
                        GPIO.output(RELAY_PIN, GPIO.HIGH)
                        relay_state = 'ON'
                    else:
                        GPIO.output(RELAY_PIN, GPIO.LOW)
                        relay_state = 'OFF'

                    log_data(data, relay_state, temperature, humidity, baseline_pm25)

                else:
                    print(
                        f"Not enough data points ({len(Last_10_PM25)} out of {WINDOW_SIZE}). Skipping rising edge calculation.")
                    relay_state = 'OFF'
                    log_data(data, relay_state, temperature, humidity, baseline_pm25)
        
            if baseline_pm25 <= 10:
              
              if len(pm2_5_values) >= WINDOW_SIZE and all(timestamp >= one_hour_ago for timestamp in Last_10_timestamps):                
                   
                  if all(data_point > 1.5 * baseline_pm25 for data_point in Last_10_PM25):
                      print(f"All last {WINDOW_SIZE} readings were above the baseline. Turning on relay.")
                      GPIO.output(RELAY_PIN, GPIO.HIGH)
                      relay_state = 'ON'
                  else:
                      GPIO.output(RELAY_PIN, GPIO.LOW)
                      relay_state = 'OFF'

                  log_data(data, relay_state, temperature, humidity, baseline_pm25)

              else:
                  print( f"Not enough data points ({len(Last_10_PM25)} out of {WINDOW_SIZE}). Skipping rising edge calculation.")
                  relay_state = 'OFF'
                  log_data(data, relay_state, temperature, humidity, baseline_pm25)
    except FileNotFoundError:
        print(f"Error: File not found - {LOG_FILE_PATH}")


if __name__ == "__main__":
    try:
        if is_between_5am_and_6am():
            sys.exit()
        else:
            sps = SPS30(1)
            sps.stop_measurement()
            setup_sps30()
            check_rising_edge()
            sps.stop_measurement()

    except KeyboardInterrupt:
        sps.stop_measurement()
        print("\nKeyboard interrupt detected. SPS30 turned off.")



