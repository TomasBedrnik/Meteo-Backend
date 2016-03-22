# -*- coding: utf-8 -*-
#This has to be replaced with your own image sources

#THIS SCRIPT IS PERIDIOCALLY RUN BY METEO-FRONTEND
#WITH 1 PARAMETER - PATH TO STORE IMAGES
#HAS TO WRITE NUMBER OF IMAGES TO OUTPUT
#IMAGES HAS TO BE NAMED: img0.jpg, img1.jpg ... img10.jpg
import shutil
import requests
from datetime import datetime
from os import makedirs
from PIL import Image
import sys

if(len(sys.argv) != 2 and len(sys.argv) != 1):
    print("-1");
    sys.exit("Wrong number of parameters ("+str(len(sys.argv))+")")

if(len(sys.argv) == 1):
    imageDir = "/tmp/Meteo-Backend/images"
else:
    imageDir = sys.argv[1]

shutil.rmtree(imageDir)
makedirs(imageDir)

now = datetime.now()
camImages = [3126,2099,2113,2111,3095,3096,526,317,174,326,434]
#camImages = []
print(str(len(camImages)))

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