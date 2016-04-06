#!/usr/bin/python
#should be executed each hour with cron
#12 * * * * /path/getTemperaturesForecast.py
import xml.etree.ElementTree as ET
import urllib
import urllib.request
import datetime
from numpy import genfromtxt
import os.path

forwardForecastHours = 9;
bacwardForecastHours = 18;
lat = 50.5970683;
lon = 15.3604894;
msl = 345;
now = datetime.datetime.now()

#read last data
dataPath = "/home/john/meteor-Data"
file = "forecast.csv"
fileOldForecast = now.strftime("oldForecasts-%Y-%m")+".csv"
data = []
if os.path.isfile(dataPath+"/"+file) :
    convertfunc = lambda x: (datetime.datetime.strptime(x.decode("utf-8"), '%Y-%m-%d %H:%M:%S'))
    data = genfromtxt(dataPath+"/"+file, delimiter=",",usecols=range(0,3),converters={0:convertfunc,2:convertfunc})

url = "http://api.met.no/weatherapi/locationforecast/1.9/?lat="+str(lat)+";lon="+str(lon)+";msl="+str(msl)
f = urllib.request.urlopen(url)
tree = ET.parse(f)
root = tree.getroot()

newData = []
f.close()
for time in root.iter('time'):
    if(time.get('from') == time.get('to')):
        t = datetime.datetime.strptime(time.get('from'),"%Y-%m-%dT%H:%M:%SZ")
        if(t < (now + datetime.timedelta(0,forwardForecastHours*60*60))):
            newData.append([t,time.find('location').find('temperature').get('value')])

f = open(dataPath+"/"+file,'w')
if len(data) == 0:
    for y in range(0,len(newData)):
        row = newData[y][0].strftime("%Y-%m-%d %H:%M:%S,")+str(newData[y][1])+","+now.strftime("%Y-%m-%d %H:%M:%S")+"\n"
        f.write(row)
else:
    lastStoredI = len(newData)-1
    for i in range(0,len(data)):
        if(data[i][0] > (now - datetime.timedelta(0,bacwardForecastHours*60*60))):
            d1 = data[i][0]
            t = data[i][1]
            d2 = data[i][2]
            for y in range(0,len(newData)):
                if(d1 == newData[y][0]):
                    t = newData[y][1]
                    d2 = now
                    lastStoredI = y
            row = d1.strftime("%Y-%m-%d %H:%M:%S,")+str(t)+","+d2.strftime("%Y-%m-%d %H:%M:%S")+"\n"
            f.write(row)
        else:
            f2 = open(dataPath+"/"+fileOldForecast,'a')
            row = data[i][0].strftime("%Y-%m-%d %H:%M:%S,")+str(data[i][1])+","+data[i][2].strftime("%Y-%m-%d %H:%M:%S")+"\n"
            f2.write(row)
            f2.close()
    for y in range(lastStoredI+1,len(newData)):
        row = newData[y][0].strftime("%Y-%m-%d %H:%M:%S,")+str(newData[y][1])+","+now.strftime("%Y-%m-%d %H:%M:%S")+"\n"
        f.write(row) 
f.close()