import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

# Define the MQTT broker and topic
broker_address = "10.42.0.1"
topic = "ZeroW1"

# GPIO setup
GPIO.setmode(GPIO.BCM)
RELAY_PIN = 14
GPIO.setup(RELAY_PIN, GPIO.OUT)

# Ensure the relay is initially off
GPIO.output(RELAY_PIN, GPIO.LOW)

# Callback function to handle incoming messages
def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8").strip()
    print(f"Received message: '{payload}'")
    
    try:
        pm25_value = float(payload)
        print(f"PM2.5 Value: {pm25_value} µg/m³")
        
        # Control the relay based on PM2.5 value
        if pm25_value > 50.0:
            GPIO.output(RELAY_PIN, GPIO.HIGH)
            print("Relay turned ON")
        else:
            GPIO.output(RELAY_PIN, GPIO.LOW)
            print("Relay turned OFF")
    except ValueError:
        print("Received message is not a valid floating-point number.")

# Callback function to confirm subscription
def on_subscribe(client, userdata, mid, granted_qos):
    print(f"Subscribed to topic with QoS {granted_qos[0]}")

# Setup the MQTT client
client = mqtt.Client()

# Attach callback functions
client.on_message = on_message
client.on_subscribe = on_subscribe

# Connect to the broker
client.connect(broker_address)

# Subscribe to the topic
client.subscribe(topic)

# Start the MQTT loop (use loop_forever to ensure it runs continuously)
client.loop_start()

# Keep the script running indefinitely
try:
    while True:
        time.sleep(1)  # Sleep to reduce CPU usage
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()
    client.loop_stop()  # Stop the loop gracefully
    client.disconnect()  # Disconnect from the broker
