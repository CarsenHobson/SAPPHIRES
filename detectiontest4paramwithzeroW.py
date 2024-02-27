import time
import RPi.GPIO as GPIO
import json
from datetime import datetime
import paho.mqtt.client as mqtt
import requests
import ast
import sys

# Initialize GPIO for relay control
RELAY_PIN = 19
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

# Define constants
BASELINE_FILE_PATH = "baseline_value.json"
LOG_FILE_PATH1 = "main1.json"
LOG_FILE_PATH2 = "main2.json"
LOG_FILE_PATH3 = "main3.json"
LOG_FILE_PATH4 = "main4.json"
WINDOW_SIZE = 10  # Number of readings to consider
BASELINE_THRESHOLD1 = 0.1
BASELINE_THRESHOLD2 = 0.2
BASELINE_THRESHOLD3 = 0.3
BASELINE_THRESHOLD4 = 0.4

# Define the URL to perform the Google search
google_search_url = "https://www.google.com"

# Define a timeout for the request (in seconds)
timeout = 5

# MQTT broker settings
LOCAL_MQTT_BROKER = "10.42.0.1"
LOCAL_MQTT_PORT = 1883
LOCAL_MQTT_TOPIC = "ZeroW"

REMOTE_MQTT_BROKER = "10.42.0.1"
REMOTE_MQTT_PORT = 1883
REMOTE_MQTT_TOPIC = "Maindata"
REMOTE_MQTT_USERNAME = "SAPPHIRE"
REMOTE_MQTT_PASSWORD = "SAPPHIRE"

# Initialize global variables
mqtt_values = {"pm2.5": 0, "temperature": 0, "humidity": 0}
baseline_pm25 = 0

def is_between_5am_and_6am():
    # Get the current time in HHMM format
    current_time = int(datetime.now().strftime('%H%M'))

    # Check if it's between 05:00 and 05:59
    if 500 <= current_time <= 559:
        return True  # It's between 5 AM and 6 AM
    else:
        return False  # It's not between 5 AM and 6 AM

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(LOCAL_MQTT_TOPIC)
# MQTT on_message callback
def on_message(client, userdata, msg):
    global mqtt_values

    try:
        data_str = msg.payload.decode("utf-8")  # Convert the MQTT message to a string
        data_dict = ast.literal_eval(data_str)  # Safely evaluate the string as a dictionary
        print(f"Received MQTT values: {data_dict}")

        if "PM2.5" in data_dict:
            mqtt_values["pm2.5"] = data_dict["PM2.5"]
        if "Temperature (F)" in data_dict:
            mqtt_values["temperature"] = data_dict["Temperature (F)"]
        if "Humidity (%)" in data_dict:
            mqtt_values["humidity"] = data_dict["Humidity (%)"]
    except ValueError:
        pass

# Create an MQTT client instance for local MQTT
local_mqtt_client = mqtt.Client()
local_mqtt_client.on_connect = on_connect
local_mqtt_client.on_message = on_message
local_mqtt_client.connect(LOCAL_MQTT_BROKER, LOCAL_MQTT_PORT)
local_mqtt_client.loop_start()

# Create an MQTT client instance for remote MQTT
remote_mqtt_client = mqtt.Client()
remote_mqtt_client.username_pw_set(REMOTE_MQTT_USERNAME, REMOTE_MQTT_PASSWORD)
remote_mqtt_client.connect(REMOTE_MQTT_BROKER, REMOTE_MQTT_PORT)

#Function to convert BME temp to Fahrenheit
def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) +32

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

# Function to log data to the first JSON file
def log_data1(pm2_5, relay_state, temperature, humidity, baseline_pm25):
    try:
        with open(LOG_FILE_PATH1, "a") as json_file:
            entry_with_timestamp_and_key = {
                "timestamp": int(time.time()),  # Add UNIX timestamp
                "key": generate_random_key(),  # Generate a new random key for each entry
                "pm2_5": pm2_5,
                "relay_state": relay_state,
                "temperature": temperature,
                "humidity": humidity,
                "baseline_pm25": baseline_pm25
            }
            json_file.write(json.dumps(entry_with_timestamp_and_key) + "\n")
    except Exception as e:
        print(f"Error writing to JSON file: {str(e)}")

# Function to log data to the second JSON file
def log_data2(pm2_5, relay_state, temperature, humidity, baseline_pm25):
    try:
        with open(LOG_FILE_PATH2, "a") as json_file:
            entry_with_timestamp_and_key = {
                "timestamp": int(time.time()),  # Add UNIX timestamp
                "key": generate_random_key(),  # Generate a new random key for each entry
                "pm2_5": pm2_5,
                "relay_state": relay_state,
                "temperature": temperature,
                "humidity": humidity,
                "baseline_pm25": baseline_pm25
            }
            json_file.write(json.dumps(entry_with_timestamp_and_key) + "\n")
    except Exception as e:
        print(f"Error writing to JSON file: {str(e)}")
        
# Function to log data to the third JSON file
def log_data3(pm2_5, relay_state, temperature, humidity, baseline_pm25):
    try:
        with open(LOG_FILE_PATH3, "a") as json_file:
            entry_with_timestamp_and_key = {
                "timestamp": int(time.time()),  # Add UNIX timestamp
                "key": generate_random_key(),  # Generate a new random key for each entry
                "pm2_5": pm2_5,
                "relay_state": relay_state,
                "temperature": temperature,
                "humidity": humidity,
                "baseline_pm25": baseline_pm25
            }
            json_file.write(json.dumps(entry_with_timestamp_and_key) + "\n")
    except Exception as e:
        print(f"Error writing to JSON file: {str(e)}")

# Function to log data to the fourth JSON file
def log_data4(pm2_5, relay_state, temperature, humidity, baseline_pm25):
    try:
        with open(LOG_FILE_PATH4, "a") as json_file:
            entry_with_timestamp_and_key = {
                "timestamp": int(time.time()),  # Add UNIX timestamp
                "key": generate_random_key(),  # Generate a new random key for each entry
                "pm2_5": pm2_5,
                "relay_state": relay_state,
                "temperature": temperature,
                "humidity": humidity,
                "baseline_pm25": baseline_pm25
            }
            json_file.write(json.dumps(entry_with_timestamp_and_key) + "\n")
    except Exception as e:
        print(f"Error writing to JSON file: {str(e)}")
def check_rising_edge():
    baseline_pm25 = read_baseline_value()
    pm2_5_values = []
    timestamp_values = []
    current_time = time.time()
    one_hour_ago = current_time - 1200
    data = mqtt_values
    data["pm2.5"] = float(data["pm2.5"])
    data["temperature"] = float(data["temperature"])
    data["humidity"] = float(data["humidity"])


    try:
        with open(LOG_FILE_PATH1, 'r') as file:
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
           
            if len(Last_10_PM25) >= WINDOW_SIZE and all(timestamp >= one_hour_ago for timestamp in Last_10_timestamps):
               
                if all(data_point > (1 + BASELINE_THRESHOLD1) * baseline_pm25 for data_point in Last_10_PM25):
                    print(f"All last {WINDOW_SIZE} readings were above the baseline. Turning on relay.")
                    #GPIO.output(RELAY_PIN, GPIO.HIGH)
                    relay_state1 = 'ON'
                
                else:
                    #GPIO.output(RELAY_PIN, GPIO.LOW)
                    relay_state1 = 'OFF'

                if all(data_point > (1 + BASELINE_THRESHOLD2) * baseline_pm25 for data_point in Last_10_PM25):
                    print(f"All last {WINDOW_SIZE} readings were above the baseline. Turning on relay.")
                    #GPIO.output(RELAY_PIN, GPIO.HIGH)
                    relay_state2 = 'ON'
                
                else:
                    #GPIO.output(RELAY_PIN, GPIO.LOW)
                    relay_state2 = 'OFF'
                
                if all(data_point > (1 + BASELINE_THRESHOLD3) * baseline_pm25 for data_point in Last_10_PM25):
                    print(f"All last {WINDOW_SIZE} readings were above the baseline. Turning on relay.")
                    #GPIO.output(RELAY_PIN, GPIO.HIGH)
                    relay_state3 = 'ON'
                
                else:
                    #GPIO.output(RELAY_PIN, GPIO.LOW)
                    relay_state3 = 'OFF'
                    
                if all(data_point > (1 + BASELINE_THRESHOLD4) * baseline_pm25 for data_point in Last_10_PM25):
                    print(f"All last {WINDOW_SIZE} readings were above the baseline. Turning on relay.")
                    #GPIO.output(RELAY_PIN, GPIO.HIGH)
                    relay_state4 = 'ON'
                
                else:
                    #GPIO.output(RELAY_PIN, GPIO.LOW)
                    relay_state4 = 'OFF'
                
                log_data1(data["pm2.5"], relay_state1, data["temperature"],  data["humidity"], baseline_pm25)
                log_data2(data["pm2.5"], relay_state2, data["temperature"],  data["humidity"], baseline_pm25)
                log_data3(data["pm2.5"], relay_state3, data["temperature"],  data["humidity"], baseline_pm25)
                log_data4(data["pm2.5"], relay_state4, data["temperature"],  data["humidity"], baseline_pm25)

                # Check Wi-Fi connectivity and publish to remote MQTT based on Google search result
                try:
                    # Send an HTTP GET request to Google to check Wi-Fi connectivity
                    response = requests.get(google_search_url, timeout=timeout)

                    if response.status_code // 100 == 2:
                        print("Connected to Wi-Fi. Google search succeeded")

                        # Publish data to the remote MQTT broker
                        data_to_publish = {
                            "timestamp": int(time.time()),
                            **data,
                            "relay state1": relay_state1,
                            "relay state2": relay_state2,
                            "relay state3": relay_state3,
                            "relay state4": relay_state4,
                            "status": "Connected to Wi-Fi"
                        }
                        remote_mqtt_client.publish(REMOTE_MQTT_TOPIC, json.dumps(data_to_publish))
                    else:
                        print("Google search failed. Wi-Fi may not be connected")


                except requests.RequestException:
                    print("Failed to perform the Google search. Wi-Fi may not be connected")


            
            else:
                print(f"Not enough data points ({len(Last_10_PM25)} out of {WINDOW_SIZE}). Skipping rising edge calculation.")
                relay_state1 = 'OFF'
                relay_state2 = 'OFF'
                relay_state3 = 'OFF'
                relay_state4 = 'OFF'
                log_data1(data["pm2.5"], relay_state1, data["temperature"], data["humidity"], baseline_pm25)
                log_data2(data["pm2.5"], relay_state2, data["temperature"], data["humidity"], baseline_pm25)
                log_data3(data["pm2.5"], relay_state3, data["temperature"], data["humidity"], baseline_pm25)
                log_data4(data["pm2.5"], relay_state4, data["temperature"], data["humidity"], baseline_pm25)

                # Check Wi-Fi connectivity and publish to remote MQTT based on Google search result
                try:
                    # Send an HTTP GET request to Google to check Wi-Fi connectivity
                    response = requests.get(google_search_url, timeout=timeout)

                    if response.status_code // 100 == 2:
                        print("Connected to Wi-Fi. Google search succeeded")

                        # Publish data to the remote MQTT broker
                        data_to_publish = {
                            "timestamp": int(time.time()),
                            **data,
                            "relay state1": relay_state1,
                            "relay state2": relay_state2,
                            "relay state3": relay_state3,
                            "relay state4": relay_state4,
                            "status": "Connected to Wi-Fi"
                        }
                        remote_mqtt_client.publish(REMOTE_MQTT_TOPIC, json.dumps(data_to_publish))
                    else:
                        print("Google search failed. Wi-Fi may not be connected")

                        # Add your action here if the connection is not successful
                except requests.RequestException:
                    print("Failed to perform the Google search. Wi-Fi may not be connected")


    except FileNotFoundError:
        print(f"Error: File not found - {LOG_FILE_PATH1}")
    
if __name__ == "__main__":
    try:
        if is_between_5am_and_6am():
            sys.exit()
        else:
            check_rising_edge()
       

    except KeyboardInterrupt:
        print("\nProgram stopped")

