import smbus
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: Data=%(message)s, Unix Time=%(unix_time)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="SDP810test.log",  # Specify the log file name
    filemode="a"  # Use 'a' to append to an existing file, 'w' to overwrite
)

def log_data_value(data_value):
    unix_time = int(time.time())  # Get the current Unix time
    logging.info(data_value, extra={"unix_time": unix_time})


bus=smbus.SMBus(1) #The default i2c bus
address=0x25
bus.write_i2c_block_data(address, 0x3F, [0xF9]) #Stop any cont measurement of the sensor
time.sleep(0.8)


#Start Continuous Measurement (5.3.1 in Data sheet)
print ("(Start Continuous Measurement (5.3.1 in Data sheet)")

##Command code (Hex)        Temperature compensation            Averaging
##0x3603                    Mass flow                           Average  till read
##0x3608                    Mass flow None                      Update rate 0.5ms
##0x3615                    Differential pressure               Average till read
##0x361E                    Differential pressure None          Update rate 0.5ms

 
bus.write_i2c_block_data(address, 0x36, [0X03]) # The command code 0x3603 is split into two arguments, cmd=0x36 and [val]=0x03
print ("Taking 1 readings of 9 bites each. See table in section 5.3.1 of datasheet for meaning of each bite")
for x in range (0, 1):    
    time.sleep(2)
    reading=bus.read_i2c_block_data(address,0,9)
    print (reading)


while True:    
    time.sleep(2)
    reading=bus.read_i2c_block_data(address,0,9)
    pressure_value=reading[0]+float(reading[1])/255
    if pressure_value>=0 and pressure_value<128:
        differential_pressure=pressure_value*240/256 #scale factor adjustment
    elif pressure_value>128 and pressure_value<=256:
        differential_pressure=-(256-pressure_value)*240/256 #scale factor adjustment
    elif pressure_value==128:
        differential_pressure=99999999 #Out of range
    print("Diffirential Pressure: "+str(differential_pressure)+" PA")
    log_data_value(differential_pressure)

    
