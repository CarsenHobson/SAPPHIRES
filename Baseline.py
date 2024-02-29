import json
import time
from sps30 import SPS30

# File path for baseline value
BASELINE_FILE_PATH = "baseline_value.json"
BASELINE_DATA_FILE = "Baselinedata.json"

sps = SPS30(1)
# Function to setup the SPS30 sensor
def setup_sps30():
    sps.start_measurement()
    time.sleep(2)

def update_baseline_value(baseline_value):
    try:
        timestamp = int(time.time())
        with open(BASELINE_FILE_PATH, "w") as baseline_file:
            json.dump({"timestamp": timestamp, "baseline_pm25": baseline_pm25}, baseline_file)
        print("Baseline value updated in the file.")
        sps.stop_measurement()
    except Exception as e:
        print(f"Error updating baseline value: {str(e)}")

def log_data(pm2_5):
    try:
        with open(BASELINE_DATA_FILE, "a") as json_file:
            entry_with_timestamp_and_key = {
                "timestamp": int(time.time()),  # Add UNIX timestamp
                "pm2_5": pm2_5,
            }
            json_file.write(json.dumps(entry_with_timestamp_and_key) + "\n")
    except Exception as e:
        print(f"Error writing to JSON file: {str(e)}")

# Function to perform baseline measurement and update the file
def perform_baseline(baseline_duration=3600):  # Set the baseline duration in seconds
    baseline_data = []
    global baseline_pm25
    sps = SPS30(1)
    setup_sps30()
    pm2_5_values = []
    print(f"Performing baseline measurement for {baseline_duration} seconds...")

    start_time = time.time()

    while time.time() - start_time < baseline_duration:
        
        sps.read_measured_values()
        data = sps.dict_values['pm2p5']
        log_data(data)
        time.sleep(30)
    try:
        with open(BASELINE_DATA_FILE, 'r') as file:
            for line in file:
                try:
                    json_data = json.loads(line)
                    pm2_5_values.append(json_data["pm2_5"])
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    # Handle the error as needed
            
            Last_20_PM25 = pm2_5_values[-120:]
    
            baseline_pm25 = sum(Last_20_PM25) / 120

            print(f"Baseline PM2.5: {baseline_pm25} µg/m³")

            update_baseline_value(baseline_pm25)
        
    except Exception as e:
        print(f"{str(e)}")

if __name__ == "__main__":
    try:
        perform_baseline()
    except KeyboardInterrupt:
        sps.stop_measurement()
        print("\nKeyboard interrupt detected. SPS30 turned off.")
   

