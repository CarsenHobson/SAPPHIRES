import RPi.GPIO as GPIO
import csv
import time
from datetime import datetime
from sps30 import SPS30

# Setup GPIO
GPIO.setmode(GPIO.BCM)
button_pin = 23
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Setup SPS30
sps = SPS30(1)
sps.start_measurement()

logging = False

def toggle_logging():
    global logging
    logging = not logging
    if logging:
        print("Logging started")
    else:
        print("Logging stopped")

def log_data():
    if logging:
        sps.read_measured_values()
        pm25 = sps.dict_values['pm2p5']
        if pm25 is not None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{timestamp}: PM2.5={pm25}")
            # Log data to CSV file
            with open('pm25_data.csv', mode='a') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, pm25])

# Setup button event detection
GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=lambda x: toggle_logging(), bouncetime=300)

try:
    while True:
        log_data()
        time.sleep(1)  # Adjust the logging frequency as needed
except KeyboardInterrupt:
    GPIO.cleanup()
