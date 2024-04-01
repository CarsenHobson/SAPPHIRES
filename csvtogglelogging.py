import RPi.GPIO as GPIO
import time
import csv

# Set up GPIO
button_pin = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# CSV file setup
csv_file = 'data_log.csv'
fieldnames = ['Timestamp', 'Data']
logging = False

def start_logging():
    global logging
    logging = True
    print("Logging started.")

def stop_logging():
    global logging
    logging = False
    print("Logging stopped.")

def write_to_csv(timestamp, data):
    with open(csv_file, mode='a') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow({'Timestamp': timestamp, 'Data': data})

def button_callback(channel):
    global logging
    if logging:
        stop_logging()
    else:
        start_logging()

# Add event listener for button press
GPIO.add_event_detect(button_pin, GPIO.FALLING, callback=button_callback, bouncetime=300)

try:
    while True:
        if logging:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            data = "Your data here"  # You need to replace this with your actual data source
            write_to_csv(timestamp, data)
            time.sleep(1)  # Adjust the sampling interval as needed
        else:
            time.sleep(0.1)  # Polling interval when not logging

except KeyboardInterrupt:
    GPIO.cleanup()
