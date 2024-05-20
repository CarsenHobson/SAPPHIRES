import time
import paho.mqtt.client as mqtt
import Adafruit_BME280
from sps30 import SPS30
import subprocess
import logging

# Set up logging
logging.basicConfig(filename='/path/to/your/logfile.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

# Configuration
MQTT_USERNAME = "SAPPHIRE"
MQTT_PASSWORD = "SAPPHIRE"
BROKER_ADDRESS = "10.42.0.1"
MQTT_TOPIC = "ZeroW"
MQTT_ERROR_TOPIC = "ZeroW/error"
BME280_ADDRESS = 0x77
SPS30_PORT = 1
IWCONFIG_PATH = '/sbin/iwconfig'

# Initialize sensors and MQTT client
def init_sensors():
    bme280_sensor = Adafruit_BME280.BME280(address=BME280_ADDRESS)
    sps30_sensor = SPS30(port=SPS30_PORT)
    return bme280_sensor, sps30_sensor

def init_mqtt_client():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_publish = on_publish
    client.connect(BROKER_ADDRESS, 1883, 60)
    return client

def on_publish(client, userdata, result):
    pass

# Convert Celsius to Fahrenheit
def celsius_to_fahrenheit(celsius):
    return (celsius * 9 / 5) + 32

# Get WiFi signal strength
def get_wifi_strength():
    try:
        result = subprocess.run([IWCONFIG_PATH], capture_output=True, text=True)
        output_lines = result.stdout.split('\n')
        for line in output_lines:
            if 'Signal level=' in line:
                signal_strength = line.split('Signal level=')[-1].split(' ')[0]
                signal_strength_dbm = int(signal_strength.replace('dBm', ''))
                max_signal_strength = -30  # dBm
                min_signal_strength = -100  # dBm
                signal_strength_percentage = max(
                    0, min(100, (signal_strength_dbm - min_signal_strength) /
                           (max_signal_strength - min_signal_strength) * 100))
                return signal_strength_percentage
    except Exception as e:
        error_message = f"Error getting WiFi strength: {e}"
        logging.error(error_message)
        return error_message

# Read sensor data
def read_sensors(bme280, sps30):
    try:
        sps30.read_measured_values()
        pm25 = sps30.dict_values['pm2p5']

        temperature_celsius = bme280.read_temperature()
        temperature_fahrenheit = celsius_to_fahrenheit(temperature_celsius)
        humidity = bme280.read_humidity()

        sensor_data = {
            "PM2.5": pm25,
            "Temperature (F)": temperature_fahrenheit,
            "Humidity (%)": humidity,
        }

        wifi_strength = get_wifi_strength()
        if isinstance(wifi_strength, int):
            sensor_data["WiFi Strength (dBm)"] = wifi_strength
        else:
            logging.warning(wifi_strength)

        return sensor_data
    except Exception as e:
        error_message = f"Error reading sensors: {e}"
        logging.error(error_message)
        return error_message

# Publish sensor data or error message
def publish_data(client, topic, data):
    try:
        client.publish(topic, str(data), qos=1)
        logging.info(f"Published data to {topic}: {data}")
    except Exception as e:
        error_message = f"Error publishing data: {e}"
        logging.error(error_message)

# Main function
def main():
    bme280, sps30 = init_sensors()
    client = init_mqtt_client()

    try:
        while True:
            sensor_data = read_sensors(bme280, sps30)
            if isinstance(sensor_data, dict):
                publish_data(client, MQTT_TOPIC, sensor_data)
            else:
                publish_data(client, MQTT_ERROR_TOPIC, sensor_data)
            time.sleep(60)  # Wait for 1 minute before the next read
    except KeyboardInterrupt:
        sps30.stop_measurement()
        logging.info("Keyboard interrupt detected. SPS30 and BME280 turned off.")
    except Exception as e:
        error_message = f"An error occurred: {e}"
        logging.error(error_message)
        publish_data(client, MQTT_ERROR_TOPIC, error_message)
    finally:
        sps30.stop_measurement()

if __name__ == "__main__":
    main()


