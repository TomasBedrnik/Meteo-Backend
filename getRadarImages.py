#!/usr/bin/python
#should be executed every 10 minutes with cron
#5,15,25,35,45,55 * * * * /path/getRadarImages.py
import shutil
import requests
from datetime import datetime
from os import makedirs
from PIL import Image
import sys
import os.path
import time

if(len(sys.argv) != 2 and len(sys.argv) != 1):
    print("-1");
    sys.exit("Wrong number of parameters ("+str(len(sys.argv))+")")

imageDir = "/tmp/Meteo-Backend/radarImages"
now = datetime.utcnow()
if(len(sys.argv) == 2):
  tmp = now.strftime("%Y%m%d")
  now = datetime.strptime(tmp+sys.argv[1], '%Y%m%d%H%M')
elif(len(sys.argv) == 3):
  imageDir = sys.argv[2]
  tmp = now.strftime("%Y%m%d")
  now = datetime.strptime(tmp+sys.argv[1], '%Y%m%d%H%M')

if (os.path.isdir(imageDir) == False):
  makedirs(imageDir)

minutes = int(now.strftime("%M"))//10*10;
imageURLRadar = "http://radar.bourky.cz/data/pacz2gmaps.z_max3d."+now.strftime("%Y%m%d.%H")+str(minutes).zfill(2)+".0.png";
imageURLLightning = "http://radar.bourky.cz/data/celdn/pacz2gmaps.blesk."+now.strftime("%Y%m%d.%H")+str(minutes).zfill(2)+".png";

response = requests.get(imageURLLightning, stream=True)
with open(imageDir+"/lightning"+now.strftime("%Y%m%d.%H")+str(minutes).zfill(2)+".png", "wb") as out_file:
  shutil.copyfileobj(response.raw, out_file)
del response

response = requests.get(imageURLRadar, stream=True)
with open(imageDir+"/radar"+now.strftime("%Y%m%d.%H")+str(minutes).zfill(2)+".png", "wb") as out_file:
  shutil.copyfileobj(response.raw, out_file)
del response

now = time.time()
for f in os.listdir(imageDir):
  f = os.path.join(imageDir, f)
  if os.stat(f).st_mtime < now - 2*60*60:
    if os.path.isfile(f):
      os.remove(os.path.join(imageDir, f))
