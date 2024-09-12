import paho.mqtt.client as mqtt
import os
import time

# MQTT settings
MQTT_BROKER = "10.42.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "Reset2"

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        client.subscribe(MQTT_TOPIC)
        print("Connected and subscribed to topic")

def on_message(client, userdata, message):
    if message.payload.decode() == "reboot":
        print("Reboot message received. Rebooting...")
        os.system('sudo reboot')

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")

def on_unsubscribe(client, userdata, mid, reason_code_list, properties):
    if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
        print("Unsubscribe succeeded")
    else:
        print(f"Broker replied with failure: {reason_code_list[0]}")

if __name__ == "__main__":
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_unsubscribe = on_unsubscribe

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    # Wait for59 seconds to receive the message
    time.sleep(59)

    client.loop_stop()
    client.disconnect()
