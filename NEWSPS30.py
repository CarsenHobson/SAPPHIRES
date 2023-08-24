import RPi.GPIO as GPIO
import time
from sps30 import SPS30
from collections import deque
from datetime import datetime, timedelta

# Set up GPIO
RELAY_PIN = 25
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

# Initialize SPS30 sensor
sps = SPS30(port=1)  # Use port=1 for the default I2C interface

def setup_sps30():
    sps.start_measurement()
    time.sleep(2)  # Add a delay of 2 seconds before reading measured values

def read_sps30_data():
    sps.read_measured_values()
    pm25 = sps.dict_values['pm2p5']
    return pm25

def smooth_data(data, window_size):
    smoothed_data = []
    for i in range(len(data) - window_size + 1):
        window = data[i:i+window_size]
        smoothed_value = sum(window) / window_size
        smoothed_data.append(smoothed_value)
    return smoothed_data

# Historical data configuration
WINDOW_SIZE = 10  # Number of data points to consider for historical analysis
BASELINE_WINDOW_SIZE = 180  # Number of minutes to collect baseline data
BASELINE_RESET_INTERVAL = 3  # Number of days between baseline resets
baseline_data = []
is_baseline_collected = False
pm25_history = deque(maxlen=WINDOW_SIZE)  # Historical PM2.5 data

# Relay control configuration
UPPER_THRESHOLD = 10  # Threshold above baseline to trigger relay
LOWER_THRESHOLD = 5   # Threshold below baseline to turn off relay
relay_state = False    # Current state of the relay

# Data logging configuration
LOG_FILE = "SPS30Read.txt"
BASELINE_LOG_FILE = "SPS30Baseline.txt"

# Baseline reset configuration
baseline_reset_time = datetime.now() + timedelta(days=BASELINE_RESET_INTERVAL)

# Main loop
try:
    setup_sps30()
    start_time = time.time()
    baseline_start_time = start_time
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time

        # Check if it's time to reset the baseline
        if datetime.now() >= baseline_reset_time:
            is_baseline_collected = False
            baseline_data = []
            baseline_reset_time = datetime.now() + timedelta(days=BASELINE_RESET_INTERVAL)
            print("Baseline reset.")

        # Read PM2.5 data from SPS30 sensor
        pm25 = read_sps30_data()

        # Collect baseline data
        if not is_baseline_collected and elapsed_time <= BASELINE_WINDOW_SIZE * 60:
            baseline_data.append(pm25)
            with open(BASELINE_LOG_FILE, "a") as f:
                if len(baseline_data) == 1:
                    f.write("Timestamp | PM2.5\n")
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                log_entry = f"{timestamp} | {pm25}\n"
                f.write(log_entry)
            print("Collecting baseline data...")
        elif not is_baseline_collected:
            baseline = sum(baseline_data) / len(baseline_data)
            is_baseline_collected = True
            with open(BASELINE_LOG_FILE, "a") as f:
                f.write("\nBaseline value: {}\n".format(baseline))
            print("Baseline collection completed.")
            print("Baseline value:", baseline)

        # Apply smoothing to the PM2.5 data
        pm25_history.append(pm25)
        smoothed_pm25 = smooth_data(list(pm25_history), WINDOW_SIZE)

        # Check for rising and falling edges
        if is_baseline_collected:
            if pm25 > baseline + UPPER_THRESHOLD and all(x <= baseline for x in smoothed_pm25[-5:]):
                # Rising edge detected, turn on the relay
                relay_state = True
                GPIO.output(RELAY_PIN, GPIO.HIGH)
                print("Rising edge detected! Relay turned on.")
            elif pm25 < baseline - LOWER_THRESHOLD:
                # Falling edge detected, turn off the relay
                relay_state = False
                GPIO.output(RELAY_PIN, GPIO.LOW)
                print("Falling edge detected! Relay turned off.")

            # Log the data to the respective log files
            with open(LOG_FILE, "a") as f:
                if len(baseline_data) == 1:
                    f.write("Timestamp | PM2.5 | Baseline | Relay State\n")
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                log_entry = f"{timestamp} | {pm25} | {baseline} | {'ON' if relay_state else 'OFF'}\n"
                f.write(log_entry)

        # Print the PM2.5 value, baseline, and relay state
        print("PM2.5:", pm25)
        if is_baseline_collected:
            print("Baseline:", baseline)
        print("Relay State:", "ON" if relay_state else "OFF")

        # Wait for 5 seconds before the next reading
        time.sleep(5)

except KeyboardInterrupt:
    sps.stop_measurement()
    print("\nKeyboard interrupt detected. SPS30 turned off.")

    # Turn off the relay before exiting
    GPIO.output(RELAY_PIN, GPIO.LOW)

# Clean up GPIO
GPIO.cleanup()

