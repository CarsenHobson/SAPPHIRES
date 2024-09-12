import time
import paho.mqtt.client as mqtt
import board
from adafruit_bme280 import basic as adafruit_bme280
from sps30 import SPS30
import logging
import subprocess

mqtt_username = "SAPPHIRE"
mqtt_password = "SAPPHIRE"
broker_address = "10.42.0.1"
mqtt_topic = "ZeroW2"


logging.basicConfig(filename='/home/zerow2/logfile.log',level=logging.DEBUG, format='%(asctime)s %(message)')

def on_publish(client, userdata, result):
    pass

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(mqtt_username, mqtt_password)
client.on_publish = on_publish
client.connect(broker_address, 1883, 60)


i2c = board.I2C()  # uses board.SCL and board.SDA
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

sps30 = SPS30(port=1)


def celsius_to_fahrenheit(celsius):
    return (celsius * 9 / 5) + 32

def get_wifi_strength():
    try:
        result = subprocess.run(['/usr/sbin/iwconfig'], capture_output=True, text=True)
        output_lines = result.stdout.split('\n')
        
        for line in output_lines:
            if 'Signal level=' in line:
                signal_strength = line.split('Signal level=')[-1].split(' ')[0]
                signal_strength_dbm = int(signal_strength.replace('dBm', ''))
                max_signal_strength = -30
                min_signal_strength = -100
                signal_strength_percentage = max(0, min(100, (signal_strength_dbm - min_signal_strength)/(max_signal_strength - min_signal_strength)*100))
                return signal_strength_percentage
    except Exception as e:
        logging.error(f"Error getting wifi strength: {e}")


try:
    sps30.read_measured_values()

    pm25 = sps30.dict_values['pm2p5']

    temperature_celsius = bme280.temperature
    temperature = celsius_to_fahrenheit(temperature_celsius)
    humidity = bme280.humidity

    sensor_data = {
        "PM2.5": pm25,
        "Temperature (F)": temperature,
        "Humidity (%)": humidity,
    }

    wifi_strength = get_wifi_strength()
    if wifi_strength is not None:
        sensor_data["Wifi Strength"] = wifi_strength
    else:
        logging.warning("unable to retrieve wifi strength")
        
        
    client.publish(mqtt_topic, str(sensor_data), qos=1)
    print(sensor_data)
  

except KeyboardInterrupt:
    sps.stop_measurement()
    print("\nKeyboard interrupt detected. SPS30 and BME280 turned off.")
except Exception as e:
    logging.error(f"An error occurred: {e}")
