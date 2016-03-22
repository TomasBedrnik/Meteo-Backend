# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import numpy as np
from numpy import genfromtxt
import matplotlib.pyplot as plt
import matplotlib.ticker
from scipy.interpolate import Rbf

dataPath = "/mnt/zbytek/tmp"
now = datetime.now()
file = now.strftime("%Y-%m-%d")+".csv"

with open(dataPath+"/"+file) as f:
    firstDate = datetime.strptime(f.read(19), '%Y-%m-%d %H:%M:%S')
    
convertfunc = lambda x: (float)((datetime.strptime(x.decode("utf-8"), '%Y-%m-%d %H:%M:%S')-firstDate).seconds)
data = genfromtxt(dataPath+"/"+file, delimiter=",",usecols=range(0,4),converters={0:convertfunc})


def to_time(x, position):
    d = firstDate+timedelta(0,(float)(x))
    return d.strftime('%H:%M')
    
maxT = data[:,0].max()
minT = data[:,0].min()
xnew = np.linspace(minT,maxT,1000)
temperature = Rbf(data[:,0], data[:,1])
humidity = Rbf(data[:,0], data[:,2])

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
ax2 = ax1.twinx()
ax1.plot(xnew,temperature(xnew),'g')
ax2.plot(xnew,humidity(xnew),color='b')

tickLabels = matplotlib.ticker.FuncFormatter(to_time)
XTicks = [i*1 for i in range(60*60,(int)(maxT+60),60*60*2)]
ax1.set_xticks(XTicks)
ax1.set_xlim(0,maxT)
ax1.xaxis.set_major_formatter(tickLabels)
ax1.set_ylabel("Temperature [°C]")
ax2.set_ylabel("Humidity [%]")
ax2.set_ylim(0,105)
fig.autofmt_xdate()
fig.savefig('graph.svg', transparent=True)