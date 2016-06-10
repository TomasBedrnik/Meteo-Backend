#!/usr/bin/python2
# -*- coding: utf-8 -*-
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import sys

helpMessage = "Script for uploading files from metoestation to Google Drive\n\
For first run internet browser will pop up with login to you Google Drive account and file ~/mycreds.txt with auth. info is created\n\
\n\
Usage of this script:\n\
-add filename subFolderName \"text to add to end of file\"\n\
-replace filename subFolderName \\file\\to\\upload\\with\\path\n\
-h || --help\n\
use \"root\" for subFolderName if you want to upload to Meteo Root Dir"
if(len(sys.argv) != 5):
    print("Wrong number of parameters.")
    print(helpMessage)
    sys.exit()

gauth = GoogleAuth()
# Try to load saved client credentials
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")

drive = GoogleDrive(gauth)

def searchFolder(name,parentID):
    file_list = drive.ListFile({'q': "'"+parentID+"' in parents and trashed=false"}).GetList()
    for file1 in file_list:
        if(file1['mimeType'] == "application/vnd.google-apps.folder" and file1['title'] == name):
            return file1

    #Not found -> create it
    folder = drive.CreateFile({'title': name,"parents":  [{"kind": "drive#fileLink","id": parentID}],"mimeType": "application/vnd.google-apps.folder"})
    folder.Upload()
    return folder;

def searchTextFile(name,parentID):
    file_list = drive.ListFile({'q': "'"+parentID+"' in parents and trashed=false"}).GetList()
    for file1 in file_list:
        if(file1['title'] == name):
            return file1

    #Not found -> create it
    file1 = drive.CreateFile({'title': name, "parents":  [{"kind": "drive#fileLink","id": parentID}]})
    file1.SetContentString("")
    return file1;
    
def searchBinFile(name,parentID):
    file_list = drive.ListFile({'q': "'"+parentID+"' in parents and trashed=false"}).GetList()
    for file1 in file_list:
        if(file1['title'] == name):
            return file1

    #Not found -> create it
    file1 = drive.CreateFile({'title': name, "parents":  [{"kind": "drive#fileLink","id": parentID}]})
    return file1;

folderName = 'MeteoFiles'
folder = searchFolder(folderName,"root")

#TEXTFILE
if(sys.argv[1] == "-add"):
    print("ADDING")
    fileName = sys.argv[2]
    subFolderName = sys.argv[3]
    text = sys.argv[4]
    
    if(subFolderName == "root"):
        subFolder = folder
    else:
        subFolder = searchFolder(subFolderName,folder['id'])
        
    fileInstance = searchTextFile(fileName,subFolder['id'])
    content = fileInstance.GetContentString()
    fileInstance.SetContentString(content+text+"\n")
    fileInstance.Upload()
    
#IMAGE
elif(sys.argv[1] == "-replace"):
    fileName = sys.argv[2]
    subFolderName = sys.argv[3]
    filePath = sys.argv[4]
    
    if(subFolderName == "root"):
        subFolder = folder
    else:
        subFolder = searchFolder(subFolderName,folder['id'])

    fileInstance = searchBinFile(fileName,subFolder['id'])
    fileInstance.SetContentFile(filePath)
    fileInstance.Upload()

elif(sys.argv[1] == "-h" or sys.argv[1] == "--help" or sys.argv[1] == "-help"):
    print(helpMessage)
else:
    print("Wrong parameters.")
    print(helpMessage)