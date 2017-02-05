#!/usr/bin/python2
#should be executed each minute with cron
#*/1 * * * * /path/getTemperatures.py
#system time has tobe rigt -> start after NTP time sync

import datetime
import os
import glob
import time
#Adafruit_DHT has to be installed -> https://github.com/adafruit/Adafruit_Python_DHT.git
import Adafruit_DHT

#Adafruit_BMP has to be installed -> https://github.com/adafruit/Adafruit_Python_BMP.git
import Adafruit_BMP.BMP085 as BMP085

import inspect

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
os.system('modprobe i2c-bcm2708')
os.system('modprobe i2c-dev')

pin = 27
humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, pin)
d = datetime.datetime.now()

def read_temp_raw(device_file):
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp(device_file):
    lines = read_temp_raw(device_file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(device_file)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

#85 is default temperature it send for first touch -> it is ignored in graph
temperature1 = 85;
temperature2 = 85;
#Hardcode address -> will work if one of them isnt working
path = '/sys/bus/w1/devices/28-8000000355d4/w1_slave'
if os.path.isfile(path) :
    temperature1 = read_temp(path);
path = '/sys/bus/w1/devices/28-800000035d9a/w1_slave'
if os.path.isfile(path) :
    temperature2 = read_temp(path);

#base_dir = '/sys/bus/w1/devices/'
#if(len(glob.glob(base_dir + '28*')) >= 2):
#  device_folder_1 = glob.glob(base_dir + '28*')[0]
#  device_folder_2 = glob.glob(base_dir + '28*')[1]
#  device_file_1 = device_folder_1 + '/w1_slave'
#  device_file_2 = device_folder_2 + '/w1_slave'
#  temperature1 = read_temp(device_file_1);
#  temperature2 = read_temp(device_file_2);


sensor = BMP085.BMP085()
temp = sensor.read_temperature()
pressure = sensor.read_pressure()

#print 'Temp = {0:0.2f} *C'.format(temp)
#print 'Pressure = {0:0.2f} Pa'.format(pressure)
filename = d.strftime("%Y-%m-%d")+".csv"
dataString = d.strftime("%Y-%m-%d %H:%M:%S,"+str(temperature)+","+str(humidity)+","+str(temperature1)+","+str(temperature2)+","+str(temp)+","+str(pressure))
p = os.path.dirname(os.path.abspath(__file__)).strip("/").split('/')
dataPath = "/"+p[0]+"/"+p[1]+"/meteor-Data"

#create dir if not exists 
if not(os.path.isdir(dataPath)):
    makedirs(dataPath)

with open(dataPath+"/"+filename, "a") as f:
    f.write(dataString+"\n")

#path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#os.chdir(path)
#os.system(os.path.join(path, 'uploadToDrive.py') + " -add "+filename+" data \""+dataString+"\"")
