import RPi.GPIO as GPIO
import time

on_button = 18
off_button = 19
off_time_button = 20


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(on_button,GPIO.IN)
GPIO.setup(off_button,GPIO.IN)
GPIO.setup(off_time_button,GPIO.IN)

#Function to run the system when the green button is pressed
def run_system():
    
    while True:
        print("\rThe system is running. Press the red button to turn the system off indefenitely. Press the yellow button to turn off the system for a specific time")
        time.sleep(1)  # Sleep for 1 second before updating the message

#Function to stop the systen when the red button is pressed
def shutdown_system_indefintely():
    
    while True:
        print("\rThe system is off. User manually shut off the system")
        time.sleep(1)  # Sleep for 1 second before updating the message
        
def shutdown_system_specified_time():
    
        
        User_input_time = input("Please enter the time you want the system to shutdown for in minutes: ")
        
        for i in range(User_input_time):
            
            print("\rThe system is off for {i} minutes")
            
            i-1
            time.sleep(1)


while True:
    
    print("\rStart the system with the green button")
    time.sleep(1)  # Sleep for 1 second before updating the message
    
    
    if GPIO.input(on_button,GPIO.HIGH):
    
        run_system()
    
    elif GPIO.input(off_button, GPIO.HIGH):
    
        shutdown_system()
        
    elif GPIO.input(off_time_button,GPIO.HIGH):
        
        shutdown_system_specified_time()
    
    
