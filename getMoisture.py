#!/usr/bin/python
 
import spidev
import time
import RPi.GPIO as GPIO
import datetime
import time

#je potreba nastavit SPI na raspberry

#GPIO
GPIO.setmode(GPIO.BOARD)
pin = 11
GPIO.setup(pin,GPIO.OUT)
GPIO.output(pin,True)

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)
 
# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data
 
# Function to convert data to voltage level,
# rounded to specified number of decimal places.
def ConvertVolts(data,places):
  volts = (data * 3.3) / float(1023)
  volts = round(volts,places)
  return volts
 
 
  temp = ((data * 330)/float(1023))-50
  temp = round(temp,places)
  return temp
 
# Define sensor channels
moisture_1_channel = 0
moisture_2_channel = 1
 
# Define delay between readings
delay = 1
 

time.sleep(5)

d = datetime.datetime.now()
# Read the light sensor data
moisture_1_level = ReadChannel(moisture_1_channel)
moisture_1_volts = ConvertVolts(moisture_1_level,2)
moisture_2_level = ReadChannel(moisture_2_channel)
moisture_2_volts = ConvertVolts(moisture_2_level,2)
 
  
  
#GPIO.output(pin,True)
# Print out results
line = d.strftime("%Y-%m-%d %H:%M:%S,")+str(moisture_1_level)+","+str(moisture_1_volts)+","+str(moisture_2_level)+ "," +str(moisture_2_volts)+"\n"
#print(line)
#print("1 = "+str(moisture_1_level)+ " - " +str(moisture_1_volts))
#print("2 = "+str(moisture_2_level)+ " - " +str(moisture_2_volts))

p = os.path.dirname(os.path.abspath(__file__)).strip("/").split('/')
dataPath = "/"+p[0]+"/"+p[1]+"/meteor-Data"
with open(dataPath+"/moisture.csv", "a") as f:
    f.write(line)
# Wait before repeating loop
GPIO.output(pin,False) 
GPIO.cleanup()
