# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import numpy as np
from numpy import genfromtxt
#import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker
#from scipy.interpolate import spline
#from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.interpolate import Rbf

file = "test.csv"

temp = genfromtxt(file, delimiter=",",usecols=range(1,2))
convertfunc = lambda x: datetime.strptime(x.decode("utf-8"), '%Y.%m.%d %H:%M')
dates = genfromtxt(file, delimiter=",",usecols=range(0,1),converters={0:convertfunc})
diffTime = dates-dates[0]
diffSeconds = np.zeros(len(diffTime))
for x in range(0,len(diffTime)):
    diffSeconds[x] = diffTime[x].seconds

def to_time(x, position):
    d = dates[0]+timedelta(0,(float)(x))
    return d.strftime('%H:%M')
    
#p = np.poly1d(np.polyfit(diffSeconds, temp, 9))
#p30 = np.poly1d(np.polyfit(diffSeconds, temp, 11))
#xp = np.linspace(diffSeconds[0], diffSeconds[len(diffSeconds)-1], 1000)
xnew = np.linspace(diffSeconds.min(),diffSeconds.max(),1000)
#power_smooth = spline(diffSeconds,temp,xnew)
#f2 = InterpolatedUnivariateSpline(diffSeconds, temp)
f3 = Rbf(diffSeconds, temp)

fig = plt.figure()
#fig.patch.set_facecolor('white')
ax = fig.add_subplot(1,1,1) 
ax.plot(diffSeconds,temp,'+',xnew,f3(xnew))
#ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
tickLabels = matplotlib.ticker.FuncFormatter(to_time)
XTicks = [i*1 for i in range(60*60,(int)(diffSeconds.max()+60),60*60*2)]
ax.set_xticks(XTicks)
ax.xaxis.set_major_formatter(tickLabels)
fig.autofmt_xdate()
fig.savefig('graph.svg', transparent=True)