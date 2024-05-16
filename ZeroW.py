import time
import paho.mqtt.client as mqtt
import Adafruit_BME280
from sps30 import SPS30
import subprocess

mqtt_username = "SAPPHIRE"
mqtt_password = "SAPPHIRE"
broker_address = "10.42.0.1"
mqtt_topic = "ZeroW"

def on_publish(client, userdata, result):
    pass

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(mqtt_username, mqtt_password)
client.on_publish = on_publish
client.connect(broker_address, 1883, 60)

bme280 = Adafruit_BME280.BME280(address=0x77)
sps30 = SPS30(port=1)

def celsius_to_fahrenheit(celsius):
    return (celsius * 9 / 5) + 32

def get_wifi_strength():
    # Execute the iwconfig command to get WiFi information
    result = subprocess.run(['iwconfig'], capture_output=True, text=True)
    output_lines = result.stdout.split('\n')

    # Find the line containing the signal strength
    for line in output_lines:
        if 'Signal level=' in line:
            # Extract the signal strength value in dBm
            signal_strength = line.split('Signal level=')[-1].split(' ')[0]
            # Convert signal strength to dBm
            signal_strength_dbm = int(signal_strength.replace('dBm', ''))
            # Convert dBm to percentage (example conversion)
            # Adjust reference values according to your network's characteristics
            max_signal_strength = -30  # dBm
            min_signal_strength = -100  # dBm
            signal_strength_percentage = (
                (signal_strength_dbm - min_signal_strength) /
                (max_signal_strength - min_signal_strength)
            ) * 100
            return signal_strength_percentage

    return None

try:
    sps30.read_measured_values()
    pm25 = sps30.dict_values['pm2p5']

    temperature_celsius = bme280.read_temperature()
    temperature = celsius_to_fahrenheit(temperature_celsius)
    humidity = bme280.read_humidity()

    sensor_data = {
        "PM2.5": pm25,
        "Temperature (F)": temperature,
        "Humidity (%)": humidity,
    }

    # Add WiFi Strength to sensor data
    wifi_strength = get_wifi_strength()
    if wifi_strength is not None:
        sensor_data["WiFi Strength (dBm)"] = wifi_strength
    else:
        print("Unable to retrieve WiFi strength.")

    client.publish(mqtt_topic, str(sensor_data), qos=1)
    print(sensor_data)
    
except KeyboardInterrupt:
    sps.stop_measurement()
    print("\nKeyboard interrupt detected. SPS30 and BME280 turned off.")

