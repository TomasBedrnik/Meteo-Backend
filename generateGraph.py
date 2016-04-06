#!/usr/bin/python
#should be executed every 5 minutes with cron
#*/5 * * * * /path/generateGraph.py
import matplotlib
matplotlib.use('Agg')

from datetime import datetime, timedelta
import numpy as np
from numpy import genfromtxt
import matplotlib.pyplot as plt
from scipy.interpolate import Rbf
import sys
import shutil
from os import makedirs
import os.path

if(len(sys.argv) != 2 and len(sys.argv) != 1):
    print("-1");
    sys.exit("Wrong number of parameters ("+str(len(sys.argv))+")")

if(len(sys.argv) == 1):
    graphDir = "/tmp/Meteo-Backend/graph"
else:
    graphDir = sys.argv[1]

if os.path.isdir(graphDir):
    shutil.rmtree(graphDir)
makedirs(graphDir)

dataPath = "/mnt/zbytek/home/john/meteor-Data"
now = datetime.now()
yesterday = now - timedelta(1)

fileY = yesterday.strftime("%Y-%m-%d")+".csv"
fileT = now.strftime("%Y-%m-%d")+".csv"

with open(dataPath+"/"+fileY) as f:
    firstDate = datetime.strptime(f.read(19), '%Y-%m-%d %H:%M:%S')
    
convertfunc = lambda x: (float)((datetime.strptime(x.decode("utf-8"), '%Y-%m-%d %H:%M:%S')-firstDate).seconds + (datetime.strptime(x.decode("utf-8"), '%Y-%m-%d %H:%M:%S')-firstDate).days * 24*60*60)
dataY = genfromtxt(dataPath+"/"+fileY, delimiter=",",usecols=range(0,4),converters={0:convertfunc})
dataT = genfromtxt(dataPath+"/"+fileT, delimiter=",",usecols=range(0,4),converters={0:convertfunc})

dataForecast = genfromtxt(dataPath+"/forecast.csv", delimiter=",",usecols=range(0,2),converters={0:convertfunc})

#find index 24 hours back
index24 = 0
for i in range(0,len(dataY)):
    if (firstDate + timedelta(0,dataY[i,0])) < yesterday:
        index24 = i
    else:
        break
#data = np.concatenate((dataY,dataT),axis=0)
def to_time(x, position):
    d = firstDate+timedelta(0,(float)(x))
    return d.strftime('%H:%M')
    
minT = dataY[index24,0]
maxT = dataForecast[len(dataForecast)-1,0]


time = np.concatenate((dataY[index24:,0],dataT[:,0]),axis=0)
temperature = np.concatenate((dataY[index24:,1],dataT[:,1]),axis=0)
humidity = np.concatenate((dataY[index24:,2],dataT[:,2]),axis=0)
##THIS NEEDS LOT OF MEMORY - ON RASPBERRY PI = MEMORY ERROR
#xnew = np.linspace(minT,maxT,1000)
#temperature = Rbf(time, temperature)
#humidity = Rbf(a,c)
#ax1.plot(xnew,temperature(xnew),'g')
#ax2.plot(xnew,humidity(xnew),'b')

xnew = np.linspace(dataForecast[0,0],maxT,100)
forecast = Rbf(dataForecast[:,0],dataForecast[:,1])

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax2 = ax1.twinx()
ax1.plot(time,temperature,'g')
ax1.plot(dataForecast[:,0],dataForecast[:,1],'+r')
ax1.plot(xnew,forecast(xnew),'r')
ax2.plot(time,humidity,'b')

tickLabels = matplotlib.ticker.FuncFormatter(to_time)
XTicks = [i*1 for i in range(60*60,(int)(maxT+60),60*60*2)]
ax1.set_xticks(XTicks)
ax1.set_xlim(minT,maxT)
ax1.xaxis.set_major_formatter(tickLabels)
ax1.set_ylabel("Temperature [°C]")
ax2.set_ylabel("Humidity [%]")
ax2.set_ylim(0,105)
fig.autofmt_xdate()
fig.savefig(graphDir+'/graph1.svg', transparent=True)