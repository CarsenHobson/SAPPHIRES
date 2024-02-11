import time
import network
import RPi.GPIO as GPIO

# Set up GPIO
LED_PIN = 17  # Change this to the actual GPIO pin you're using
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print(f"Connecting to WiFi {ssid}")
        wlan.connect(ssid, password)

        while not wlan.isconnected():
            pass

    print("Connected to WiFi")

def main():
    # Replace 'YourWiFiSSID' and 'YourWiFiPassword' with your actual Wi-Fi credentials
    wifi_ssid = 'YourWiFiSSID'
    wifi_password = 'YourWiFiPassword'

    connect_to_wifi(wifi_ssid, wifi_password)

    # Blink the LED to indicate successful Wi-Fi connection
    for _ in range(3):
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(LED_PIN, GPIO.LOW)
        time.sleep(1)

    # Keep the LED on as an indication that Wi-Fi is connected
    GPIO.output(LED_PIN, GPIO.HIGH)

    try:
        while True:
            # Your main program logic goes here
            pass

    except KeyboardInterrupt:
        # Cleanup on keyboard interrupt (Ctrl+C)
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.cleanup()

if __name__ == "__main__":
    main()
