import json
import uuid
import time
import tkinter as tk
from tkinter import StringVar
import threading
import RPi.GPIO as GPIO
from sps30 import SPS30
import Adafruit_BME280

# Initialize the SPS30 sensor
sps = SPS30(1)  # Use the appropriate I2C bus number
sps.begin()

# Initialize the BME280 sensor
bme280 = Adafruit_BME280.Adafruit_BME280_I2C()

# Define button GPIO pins
on_button = 18
off_button = 19
off_time_button = 20

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(on_button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(off_button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(off_time_button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Create a Tkinter window
root = tk.Tk()
root.title("GPIO Control")

# Define system states
IDLE = 0
RUNNING = 1
SHUTDOWN_INDEFINITE = 2
SHUTDOWN_SPECIFIED_TIME = 3

# Initialize the state
current_state = IDLE

# Create a StringVar to update the countdown label
countdown_var = StringVar()
countdown_var.set("")  # Initialize to an empty string

# Function to read data from both sensors
def read_sensor_data():
    # Read data from the SPS30 sensor
    sps_data = sps.read_measured_values()

    # Read data from the BME280 sensor
    bme280_data = {
        "TEMP": bme280.read_temperature(),
        "Humidity": bme280.read_humidity(),
        "pressure": bme280.read_pressure() / 100.0  # Pressure in hPa
    }

    return sps_data, bme280_data

# Function to create and save JSON data
def create_and_save_json(user_input_value, control_status):
    sps_data, bme280_data = read_sensor_data()

    # Generate a random key
    random_key = str(uuid.uuid4())

    # Create the JSON structure
    data = {
        random_key: {
            "device_id": "your_device_id_here",
            "categories": {
                "environment": {
                    "UNIX time": int(time.time()),
                    "SPS30": sps_data,
                    "TEMP": bme280_data["TEMP"],
                    "Humidity": bme280_data["Humidity"],
                    "pressure": bme280_data["pressure"]
                },
                "controls": {
                    "UNIX time": int(time.time()),
                    "user input": user_input_value,
                    "control status": control_status,
                    "intervention state": "intervention_state_data_here",
                    "feedback": "feedback_data_here"
                }
            }
        }
    }

    # Save the JSON data to a file
    with open("data.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

    print(f"JSON data saved to 'data.json' under the key: {random_key}")

# Function to run the system
def run_system():
    global current_state
    current_state = RUNNING
    status_label.config(text="The system is running.")
    countdown_var.set("")  # Clear the countdown
    create_and_save_json("user_input_data_here", "System is running")

# Function to stop the system indefinitely
def shutdown_system():
    global current_state
    current_state = SHUTDOWN_INDEFINITE
    status_label.config(text="The system is off. User manually shut off the system.")
    countdown_var.set("")  # Clear the countdown
    create_and_save_json("user_input_data_here", "System is off")

# Function to stop the system for a specified time
def shutdown_system_specified_time():
    try:
        user_input_time = int(input_entry.get())
        status_label.config(text=f"The system will be off for {user_input_time} minutes.")
        countdown_var.set(f"Time remaining: {user_input_time} minutes")  # Set the countdown

        # Pass the control status to the create_and_save_json function
        create_and_save_json(user_input_time, "System is off for a specified time")
        
        def shutdown_thread():
            global current_state  # Use the global keyword to modify the global variable
            time.sleep(user_input_time * 60)  # Convert minutes to seconds
            status_label.config(text="The specified time has elapsed. The system is back on.")
            countdown_var.set("")  # Clear the countdown
            current_state = RUNNING

        shutdown_thread = threading.Thread(target=shutdown_thread)
        shutdown_thread.start()
        
    except ValueError:
        status_label.config(text="Invalid input. Please enter a valid number of minutes.")
        countdown_var.set("")  # Clear the countdown

# Function to handle button clicks
def button_click(button_function):
    global current_state
    current_state = button_function()

# Create GUI elements
start_button = tk.Button(root, text="Start System", command=lambda: button_click(run_system))
stop_button = tk.Button(root, text="Stop System", command=lambda: button_click(shutdown_system))
input_label = tk.Label(root, text="Enter minutes:")
input_entry = tk.Entry(root)
time_button = tk.Button(root, text="Stop for Time", command=lambda: button_click(shutdown_system_specified_time))
status_label = tk.Label(root, text="")
countdown_label = tk.Label(root, textvariable=countdown_var)

# Arrange GUI elements using grid layout
start_button.grid(row=0, column=0)
stop_button.grid(row=0, column=1)
input_label.grid(row=1, column=0)
input
