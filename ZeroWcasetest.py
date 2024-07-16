import time
import threading
from sps30 import SPS30
import paho.mqtt.client as mqtt

broker_address = "10.42.0.1"
mqtt_topic = "No case"

def on_publish(client, userdata, result):
    pass

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_publish = on_publish
client.connect(broker_address, 1883, 60)

# Function to read data from the SPS30 sensor continuously
def read_sps30():
    sensor = SPS30(1)  # 1 indicates the I2C bus number
    time.sleep(2)  # Wait for the first measurement to be ready

    try:
        while True:
            sensor.read_measured_values()
            data = sensor.dict_values['pm2p5']
            if data is not None:
                pm2_5 = data
                print(f"Read PM2.5 data: {pm2_5}")
            time.sleep(0.5)  # Update every 0.5 seconds
    except KeyboardInterrupt:
        pass
    except Exception as e:
        pass
    finally:
        pass

# Start the data reading thread
threading.Thread(target=read_sps30, daemon=True).start()

# Keep the main thread alive
try:
    while True:
        # This would normally fetch and print the latest data, but since we're not using a database:
        print("Fetching latest data is disabled. Please check sensor readout.")
        time.sleep(1)  # Print the latest data every second
        client.publish(mqtt_topic, "No data", qos=1)
except KeyboardInterrupt:
    pass
except Exception as e:
    pass
