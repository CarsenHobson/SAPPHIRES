import json
import time
from sps30 import SPS30

# File path for baseline value
BASELINE_FILE_PATH = "baseline_value.json"
BASELINE_DATA_FILE = "Baselinedata.json"
# Function to setup the SPS30 sensor
def setup_sps30():
    sps.start_measurement()
    time.sleep(2)

def log_data(pm2_5):
    try:
        with open(LOG_FILE_PATH, "a") as json_file:
            entry_with_timestamp_and_key = {
                "timestamp": int(time.time()),  # Add UNIX timestamp
                "pm2_5": pm2_5,
            }
            json_file.write(json.dumps(entry_with_timestamp_and_key) + "\n")
    except Exception as e:
        print(f"Error writing to JSON file: {str(e)}")

# Function to perform baseline measurement and update the file
def update_baseline_value(baseline_duration=3600):  # Set the baseline duration in seconds
    baseline_data = []

    print(f"Performing baseline measurement for {baseline_duration} seconds...")

    start_time = time.time()

    while time.time() - start_time < baseline_duration:
        sps.read_measured_values()
        data = sps.dict_values['pm2p5']
        log_data(data)
        if data:
            baseline_data.append(data)
        time.sleep(1)
    
    baseline_pm25 = sum(baseline_data) / len(baseline_data)

    print(f"Baseline PM2.5: {baseline_pm25} µg/m³")

    # Update the baseline value with timestamp in the file
    try:
        timestamp = int(time.time())
        with open(BASELINE_FILE_PATH, "w") as baseline_file:
            json.dump({"timestamp": timestamp, "baseline_pm25": baseline_pm25}, baseline_file)
        print("Baseline value updated in the file.")
    except Exception as e:
        print(f"Error updating baseline value: {str(e)}")

# Function to stop the SPS30 measurement
def stop_sps30():
    sps.stop_measurement()

if __name__ == "__main__":
    try:
        sps = SPS30(1)
        setup_sps30()
        update_baseline_value()
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        stop_sps30()
