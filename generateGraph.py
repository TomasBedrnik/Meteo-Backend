#!/usr/bin/python
#should be executed every 5 minutes with cron
#*/5 * * * * /path/generateGraph.py
import matplotlib.ticker
matplotlib.use('Agg')

from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import sys
import shutil
from os import makedirs
import os.path
import re
import urllib.request

yesterdayData = False;

if(len(sys.argv) != 2 and len(sys.argv) != 1):
    print("-1");
    sys.exit("Wrong number of parameters ("+str(len(sys.argv))+")")

if(len(sys.argv) == 1):
    graphDir = "/tmp/Meteo-Backend/graph"
else:
    graphDir = sys.argv[1]

dataPath = "/home/john/meteor-Data"
now = datetime.now()
yesterday = now - timedelta(1)

#get historical data from .csv files
fileY = yesterday.strftime("%Y-%m-%d")+".csv"
fileT = now.strftime("%Y-%m-%d")+".csv"

#get first time
if os.path.isfile(dataPath+"/"+fileY):
    with open(dataPath+"/"+fileY) as f:
        firstDate = datetime.strptime(f.read(19), '%Y-%m-%d %H:%M:%S')
else:
    with open(dataPath+"/"+fileT) as f:
        firstDate = datetime.strptime(f.read(19), '%Y-%m-%d %H:%M:%S')    
    
#convert function for reading time from .csv
convertfunc = lambda x: (float)((datetime.strptime(x.decode("utf-8"), '%Y-%m-%d %H:%M:%S')-firstDate).seconds + (datetime.strptime(x.decode("utf-8"), '%Y-%m-%d %H:%M:%S')-firstDate).days * 24*60*60)

if os.path.isfile(dataPath+"/"+fileY):
    dataY = np.genfromtxt(dataPath+"/"+fileY, delimiter=",",usecols=range(0,4),converters={0:convertfunc})
    yesterdayData = True;
dataT = np.genfromtxt(dataPath+"/"+fileT, delimiter=",",usecols=range(0,4),converters={0:convertfunc})

dataForecast = np.genfromtxt(dataPath+"/forecast.csv", delimiter=",",usecols=range(0,2),converters={0:convertfunc})

#find index 24 hours back
index24 = 0
if(yesterdayData):
    for i in range(0,len(dataY)):
        if (firstDate + timedelta(0,dataY[i,0])) < yesterday:
            index24 = i
        else:
            break
#function for displaying time in graph
def to_time(x, position):
    d = firstDate+timedelta(0,(float)(x))
    return d.strftime('%H:%M')

#get max and min time
if(yesterdayData):    
    minTime = dataY[index24,0]
else:
    minTime = dataT[0,0]
maxTime = dataForecast[len(dataForecast)-1,0]

if(yesterdayData):
    time = np.concatenate((dataY[index24:,0],dataT[:,0]),axis=0)
    temperature = np.concatenate((dataY[index24:,1],dataT[:,1]),axis=0)
    humidity = np.concatenate((dataY[index24:,2],dataT[:,2]),axis=0)
else:
    time = dataT[:,0]
    temperature = dataT[:,1]
    humidity = dataT[:,2]
##THIS NEEDS LOT OF MEMORY - ON RASPBERRY PI = MEMORY ERROR
#xnew = np.linspace(minTime,maxTime,1000)
#temperature = Rbf(time, temperature)
#humidity = Rbf(a,c)
#ax1.plot(xnew,temperature(xnew),'g')
#ax2.plot(xnew,humidity(xnew),'b')

#FORECAST FROM ALADIN
lat = 50.5970683;
lon = 15.3604894;
url = "http://aladinonline.androworks.org/get_data.php?latitude="+str(lat)+"&longitude="+str(lon);
response = urllib.request.urlopen(url)
html = response.read()
    
#TEMPERATURE FROM ALADIN
TEMPERATURE = re.search('\"TEMPERATURE":\[([^\[]+)\],',str(html))
TEMPERATURE_VAL = re.findall('([^,]+)',TEMPERATURE.group(1))

#PRECIPATION FROM ALADIN
PRECIPITATION_TOTAL = re.search('\"PRECIPITATION_TOTAL":\[([^\[]+)\],',str(html))
PRECIPITATION_TOTAL_VAL = re.findall('([^,]+)',PRECIPITATION_TOTAL.group(1))

#ALADIN TIME
forecastTimeIso = re.search('\"forecastTimeIso\":\"([^\"]+)\",',str(html))
timeBegString = forecastTimeIso.group(1)
maxTimeAladin = (now - firstDate).seconds + ((now - firstDate).days * 24*60*60) + 24*60*60;
aladinTime = []
for i in range(0,(len(TEMPERATURE_VAL))):
    tmpTime = (datetime.strptime(timeBegString, '%Y-%m-%d %H:%M:%S') + timedelta(0,i*60*60))
    tmp = (tmpTime - firstDate).seconds + ((tmpTime - firstDate).days * 24*60*60);
    if(tmp <= maxTimeAladin):
        aladinTime.append(tmp)

precipation = []
for i in range(0,(len(aladinTime))):
    precipation.append(float(PRECIPITATION_TOTAL_VAL[i]))
    
temperatureAladin = []
for i in range(0,(len(aladinTime))):
    temperatureAladin.append(float(TEMPERATURE_VAL[i]))

xAladin = np.linspace(dataForecast[0,0],maxTimeAladin,100)
aladinForecast = Rbf(aladinTime,temperatureAladin)

xForecast = np.linspace(dataForecast[0,0],maxTime,100)
forecast = Rbf(dataForecast[:,0],dataForecast[:,1])


fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
#ax1 = host_subplot(111, axes_class=AA.Axes)
ax2 = ax1.twinx()
ax3 = ax1.twinx()

#move Precipation axis
ax3.spines['right'].set_position(('axes', 1.15))

#add data
#temperatures
ax1.plot(time,temperature,'g')

ax1.plot(dataForecast[:,0],dataForecast[:,1],'+r')
ax1.plot(xForecast,forecast(xForecast),'r')
ax1.plot(aladinTime,temperatureAladin,'+m')
ax1.plot(xAladin,aladinForecast(xAladin),'m')
#humidity
ax2.plot(time,humidity,'b')
#precipation
ax3.bar(aladinTime,precipation,2500,color='#03FDFD')

tickLabels = matplotlib.ticker.FuncFormatter(to_time)
XTicks = [i*1 for i in range(60*60,(int)(maxTimeAladin+60),60*60*4)]
ax1.set_xticks(XTicks)
ax1.set_xlim(minTime,maxTimeAladin)
ax1.xaxis.set_major_formatter(tickLabels)
ax1.set_ylabel("Temperature [°C]")

ax2.set_xlim(minTime,maxTimeAladin)
ax3.set_xlim(minTime,maxTimeAladin)

ax3.set_ylim(0,max(precipation)*1.2)
ax3.set_ylabel("Precipation [mm/h]")
ax3.set
ax2.set_ylabel("Humidity [%]")
ax2.set_ylim(0,105)

#ax1.axis["bottom"].set_axis_direction("right")
fig.autofmt_xdate()

if os.path.isdir(graphDir):
    shutil.rmtree(graphDir)
makedirs(graphDir)

fig.savefig(graphDir+'/graph1.svg', transparent=True,bbox_inches='tight')