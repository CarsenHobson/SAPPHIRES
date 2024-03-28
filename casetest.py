import time
import json
from sps30 import SPS30

sps = SPS30(1)

LOG_FILE_PATH1 = "casetest.json"

# Function to log data to the first JSON file
def log_data1(pm2_5):
    try:
        with open(LOG_FILE_PATH1, "a") as json_file:
            entry_with_timestamp_and_key = {
                "timestamp": int(time.time()),  # Add UNIX timestamp
                "pm2_5": pm2_5,
            }
            json_file.write(json.dumps(entry_with_timestamp_and_key) + "\n")
    except Exception as e:
        print(f"Error writing to JSON file: {str(e)}")

# Function to setup the SPS30 sensor
def setup_sps30():
    sps.start_measurement()
    time.sleep(2)

if __name__ == "__main__":
    try:
        setup_sps30()
        while True:
            sps.read_measured_values()
            data = sps.dict_values['pm2p5']
            log_data1(data)
            time.sleep(1)

    except KeyboardInterrupt:
        sps.stop_measurement()
        print("\nKeyboard interrupt detected. SPS30 turned off.")

