#Reading the Sensirion SDP810 125PA (or 500PA will need modification) sensor
#Dev by JJ SlabbertSDP810_example
#Code tested with Python 2.7
#Run sudo i2cdetect -y 1 in the terminal, to see if the sensor is connected. it will show address 25
#Check the datasheet at https://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/0_Datasheets/Differential_Pressure/Sensirion_Differential_Pressure_Sensors_SDP8xx_Digital_Datasheet.pdf
#The sensor i2c address is 0x25 (Not user Programable).
#I have no formal electronics, physics or programing education, code should be tested before critical applications
#Code should be compatable with sdp810, sdp800 sdp811 and sdp801
import smbus
import time

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

# We will use command code 0x3603 (Mass flow, Average  till read)
#the smbus write_i2c_block_data function have 3 arguments, addr=the i2c address, cmd and [val]. cmd and val is derived from the 
#Command code in Hex
#We will take 5 readings now
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
        diffirential_pressure=pressure_value*240/256 #scale factor adjustment
    elif pressure_value>128 and pressure_value<=256:
        diffirential_pressure=-(256-pressure_value)*240/256 #scale factor adjustment
    elif pressure_value==128:
        diffirential_pressure=99999999 #Out of range
    print("Diffirential Pressure: "+str(diffirential_pressure)+" PA")


    
