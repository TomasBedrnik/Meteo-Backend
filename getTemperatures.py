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

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

pin = 27
humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, pin)
d = datetime.datetime.now()

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

with open("/home/john/meteor-Data/"+d.strftime("%Y-%m-%d")+".csv", "a") as f:
    f.write(d.strftime("%Y-%m-%d %H:%M:%S,"+str(temperature)+","+str(humidity)+","+str(read_temp())+"\n"))
