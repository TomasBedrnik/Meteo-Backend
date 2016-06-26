#!/usr/bin/python
#should be executed every 15 minutes with cron
#4,19,34,49 5-22 * * * /path/preloadImages.py
import shutil
import requests
from datetime import datetime
from os import makedirs
from PIL import Image
import sys
import os.path
import glob
#import inspect

if(len(sys.argv) != 2 and len(sys.argv) != 1):
    print("-1");
    sys.exit("Wrong number of parameters ("+str(len(sys.argv))+")")

imageDir = "/tmp/Meteo-Backend/images"
first = False

if(len(sys.argv) == 2 and sys.argv[1] == "-first"):
    first = True

now = datetime.now()
camImages = [3126,2099,2113,2111,3095,3096,317,174,326,434]
print(str(len(camImages)))

#with firt run = run from Meteo-Frontend, check number of downloaded images -> if is equal to expected val., exit
if(first == True):
  if(len(camImages) == len(glob.glob(imageDir+"/*"))):
    sys.exit();  

if os.path.isdir(imageDir):
    shutil.rmtree(imageDir)
makedirs(imageDir)

for i in range(0,len(camImages)):
    if(i < 6):
        imageURL = "http://www.holidayinfo.cz/hol3_data.php?type=panoimg_last&camid="+str(camImages[i])+"&dt="+now.strftime("%Y%m%d%H%M%S");
    else:
        imageURL = "http://www.webcamlive.cz/camera_image.php?idCamera="+str(camImages[i])
    response = requests.get(imageURL, stream=True)
    with open(imageDir+"/img"+str(i)+".jpg", "wb") as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response
    if(camImages[i] == 2113):#Horni misecky -> crop
        img = Image.open(imageDir+"/img"+str(i)+".jpg")
        width = 2000
        height = 1080
        top = 0
        left = 2300
        box = (left, top, left+width, top+height)
        area = img.crop(box)
        area.save(imageDir+"/img"+str(i)+".jpg", 'jpeg')
        img.close()

#path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#os.chdir(path)
#for i in range(0,len(camImages)):        
#    os.system(os.path.join(path, 'uploadToDrive.py') + " -replace img"+str(i)+".jpg images "+imageDir+"/img"+str(i)+".jpg")