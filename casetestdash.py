import time
import json
import tkinter as tk
from sps30 import SPS30
import sys

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

# Function to update PM2.5 value in GUI
def update_pm25_label():
    sps.read_measured_values()
    data = sps.dict_values['pm2p5']
    log_data1(data)
    pm25_label.config(text=f"PM2.5: {data} µg/m³")
    pm25_label.after(1000, update_pm25_label)  # Update every 1000ms (1 second)

if __name__ == "__main__":
    try:
        setup_sps30()

        # Create Tkinter window
        window = tk.Tk()
        window.title("PM2.5 Dashboard")

        # Get screen width and height
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Set window size and position
        window.geometry(f"{screen_width}x{screen_height}+0+0")

        # Create label to display PM2.5 data
        pm25_label = tk.Label(window, text="", font=("Arial", 36))
        pm25_label.pack(expand=True, fill=tk.BOTH)

        # Start updating PM2.5 value in GUI
        update_pm25_label()

        # Run Tkinter event loop
        window.mainloop()

    except KeyboardInterrupt:
        sps.stop_measurement()
        sys.exit()
        print("\nKeyboard interrupt detected. SPS30 turned off.")
