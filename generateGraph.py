# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import numpy as np
from numpy import genfromtxt
import matplotlib.pyplot as plt
import matplotlib.ticker
from scipy.interpolate import Rbf
import sys
import shutil
from os import makedirs

if(len(sys.argv) != 2 and len(sys.argv) != 1):
    print("-1");
    sys.exit("Wrong number of parameters ("+str(len(sys.argv))+")")

if(len(sys.argv) == 1):
    graphDir = "/tmp/Meteo-Backend/graph"
else:
    graphDir = sys.argv[1]

makedirs(graphDir)
shutil.rmtree(graphDir)
makedirs(graphDir)

dataPath = "/mnt/zbytek/tmp"
now = datetime.now()
yesterday = now - timedelta(1)

fileY = yesterday.strftime("%Y-%m-%d")+".csv"
fileT = now.strftime("%Y-%m-%d")+".csv"

with open(dataPath+"/"+fileY) as f:
    firstDate = datetime.strptime(f.read(19), '%Y-%m-%d %H:%M:%S')
    
convertfunc = lambda x: (float)((datetime.strptime(x.decode("utf-8"), '%Y-%m-%d %H:%M:%S')-firstDate).seconds + (datetime.strptime(x.decode("utf-8"), '%Y-%m-%d %H:%M:%S')-firstDate).days * 24*60*60)
dataY = genfromtxt(dataPath+"/"+fileY, delimiter=",",usecols=range(0,4),converters={0:convertfunc})
dataT = genfromtxt(dataPath+"/"+fileT, delimiter=",",usecols=range(0,4),converters={0:convertfunc})

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
    
minT = dataY[index24:,0].min()
maxT = dataT[len(dataT)-1,0].max()

xnew = np.linspace(minT,maxT,1000)
temperature = Rbf(np.concatenate((dataY[index24:,0],dataT[:,0]),axis=0), np.concatenate((dataY[index24:,1],dataT[:,1]),axis=0))
humidity = Rbf(np.concatenate((dataY[index24:,0],dataT[:,0]),axis=0), np.concatenate((dataY[index24:,2],dataT[:,2]),axis=0))

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax2 = ax1.twinx()
ax1.plot(xnew,temperature(xnew),'g')
ax2.plot(xnew,humidity(xnew),'b')

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