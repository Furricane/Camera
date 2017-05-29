#!/usr/bin/python
#!/usr/bin/env python
import os, sys
os.chdir('/home/pi/Camera/') # Change working directory
from subprocess import Popen, PIPE
import time
import threading
sys.path.append('/home/pi/PythonUtilities')
sys.path.append('/home/pi/Camera/Logfiles')
import globals
from datetime import datetime
from datetime import timedelta
import gmail
import GoogleDrive

#print(os.getcwd())


def listdir_shell(path, *lsargs):
    p = Popen(('ls', path) + lsargs, shell=False, stdout=PIPE, close_fds=True)
    #for path in p.stdout.readlines():
    #    print(path.strip())
    #return [path.rstrip('\n') for path in p.stdout.readlines()]
    return [path.strip() for path in p.stdout.readlines()]

dirlist = listdir_shell('/home/pi/Camera/Capture/', '-t')[:10]

print("Starting nofify loop")
gmail.SendMail("Camera Motion Detected","Camera Motion Detected")

folder = GoogleDrive.CreateFolder('CameraTest')
filelist, ids = GoogleDrive.GetFileList('CameraTest')

filelistnopaths=[]
for f in filelist:
    #print ("file ",f)
    path, filename = os.path.split(f)
    #print("path= ",path,"filename=",filename)
    filelistnopaths.append(filename)
    print("filename=",filename)

for capturefile in dirlist:
    print(capturefile.decode())
    if capturefile.decode() in filelistnopaths:
         print("Duplicate file, not uploading")
    else:
        GoogleDrive.UploadFile('/home/pi/Camera/Capture/',capturefile.decode(), folder)







