import time
import paho.mqtt.client as mqtt
from smbus2 import SMbus
import Adafruit_BME280
from sps30 import SPS30
import board
import busio

broker_address = "10.42.0.1"
mqtt_topic = "ZeroW"
client = mqtt.Client()

bme280 = Adafruit_BME280.BME280(address=0x77)

sps30 = SPS30(port=1)

client.connect(broker_address, 1883, 60)
client.loop_start()


def celsius_to_fahrenheit(celsius):
    return (celsius * 9 / 5) + 32


try:
    sps30.start_measurement()
    while True:
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

        client.publish(mqtt_topic, str(sensor_data))
        print(sensor_data)
        time.sleep(5)

except KeyboardInterrupt:
    sps.stop_measurement()
    print("\nKeyboard interrupt detected. SPS30 and BME280 turned off.")
