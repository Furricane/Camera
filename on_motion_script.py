#!/usr/bin/python
#!/usr/bin/env python
import os, sys
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
for capturefile in dirlist:
    print(capturefile.decode())
    GoogleDrive.UploadFile('/home/pi/Camera/Capture/',capturefile.decode(), folder)







