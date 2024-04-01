import smbus
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: Data=%(message)s, Unix Time=%(unix_time)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="SDP810test.log",
    filemode="a"
)

def log_data_value(data_value):
    unix_time = int(time.time())
    logging.info(data_value, extra={"unix_time": unix_time})

bus = smbus.SMBus(1)
address = 0x25
bus.write_i2c_block_data(address, 0x3F, [0xF9])
time.sleep(0.8)

bus.write_i2c_block_data(address, 0x36, [0x03])

while True:
    time.sleep(0.5)  # Adjust sleep time as needed for fastest possible reading
    reading = bus.read_i2c_block_data(address, 0, 9)
    pressure_value = reading[0] + float(reading[1]) / 255
    if pressure_value >= 0 and pressure_value < 128:
        differential_pressure = pressure_value * 240 / 256
    elif pressure_value > 128 and pressure_value <= 256:
        differential_pressure = -(256 - pressure_value) * 240 / 256
    elif pressure_value == 128:
        differential_pressure = 99999999
    log_data_value(differential_pressure)
