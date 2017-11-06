#!/usr/bin/python
#!/usr/bin/env python
import os, sys
os.chdir('/home/pi/Camera/') # Change working directory
from subprocess import Popen, PIPE
import time
#import threading
sys.path.append('/home/pi/PythonUtilities')
sys.path.append('/home/pi/Camera/Logfiles')
import LogHelper as log
from LogHelper import logging
import globals
from datetime import datetime
from datetime import timedelta
import gmail
import schedule
import watchdog
import GoogleDrive
import socketcomm
import ThreadHelper


DebugMode = False
SchedulerPresent = True
WatchDogRemote = True
MutualWatchDog = True
MotionHost = True

globals.VerboseTexting = False
globals.VerboseLogging = True
globals.VerboseModuleLogging = False

MotionPort = 44444
MotionHostCreated = False
MotionHostConnectedStatus = False
#Start Log
loghandle = log.Init('Camera1', logfilepath='./Logfiles')
log.DisableModuleLogging()


# Spawn a watchdog process to notify if the main process fails
if WatchDogRemote:
    watchdog.CreateHost('192.168.1.92',54321, 'Camera1')
    ThreadHelper.RunThreaded(watchdog.AcceptConnections,threadname="WatchdogAcceptConnections")
    ThreadHelper.RunThreaded(watchdog.SendWatchdogHeartbeat,threadname="WatchdogHeartbeat")
    if MutualWatchDog:
        ThreadHelper.RunThreaded(watchdog.WatchDog, '192.168.1.91', 12345, 'HomeControl',threadname="MutualWatchdog")

def CreateMotionHost(HostAddress, HostPort):
    global MotionHost
    global MotionHostConnectedStatus
    MotionHost, connectedstatus = socketcomm.CreateHost(HostAddress, HostPort)
    log.cyan("creating motion host with port: "+str(HostPort))
    while True:
        try:
            MotionHost.AcceptConnection()
            log.cyan("Motion Connection accepted!")
            MotionHostConnectedStatus = True
            break
        except BlockingIOError:
            pass

def HostListen():
    global MotionHost
    data = MotionHost.read()
    #print(str(data))
    if data != b"":
        message = data.decode()
        message = message.strip()
        #print("Message Received:", message)
        return message
    else:
        return ''

def listFiles(path, extension):
    return [f for f in os.listdir(path) if f.endswith(extension)]

def listdir_shell(path, *lsargs):
    p = Popen(('ls', path) + lsargs, shell=False, stdout=PIPE, close_fds=True)
    #for path in p.stdout.readlines():
    #    print(path.strip())
    #return [path.rstrip('\n') for path in p.stdout.readlines()]
    return [path.strip() for path in p.stdout.readlines()]

def GetDirectoryFileList(path='.', extfilter=None, numitems = None, mostrecent=True):
    command ='ls '+path
    if extfilter == None:
        command += '*.*'
    else:
        command += extfilter
    if mostrecent:
        command += ' -t'
    p = Popen(command, shell=True, stdout=PIPE, close_fds=True)
    dirlist = []
    for path in p.stdout.readlines():
        #print(path)
        path = path.decode()
        path = os.path.basename(path)
        x = path.strip()
        #print(x)
        #x = x.decode()
        dirlist.append(x)
    #dirlist = [path.strip() for path in p.stdout.readlines()]
    #dirlist = [item.decode() for item in dirlist]
    if numitems != None:
        dirlist = dirlist[:numitems]
    #print(dirlist)
    return dirlist


def OnMotionDetectedEvent(zone=None):
    if zone == None:
        zonemsg = 'All'
    else:
         zonemsg = str(zone)
         gmail.SendText("Motion Detected Zone "+zonemsg)

    log.blue("executing on motion events - " + zonemsg)
    #dirlist = listdir_shell('/home/pi/Camera/Capture/', '-t')[:10]
    dirlist = GetDirectoryFileList('/home/pi/Camera/Capture/',numitems=10)
    #jpgdirlist = listdir_shell('/home/pi/Camera/Capture/', '*.jpg -t')[:1]
    jpgdirlist= GetDirectoryFileList('/home/pi/Camera/Capture/',extfilter='*.jpg',numitems=1)
    log.blue("Starting notify loop")
    #gmail.SendMail("Camera Motion Detected","Camera Motion Detected "+zonemsg)
    print(jpgdirlist)
    gmail.SendMail2("Camera Motion Detected Upload","Camera Motion Detected Upload"+zonemsg,jpgdirlist, path='/home/pi/Camera/Capture/')
    folder = GoogleDrive.CreateFolder('CameraTest')
    filelist, ids = GoogleDrive.GetFileList('CameraTest')

    for capturefile in dirlist:
        if capturefile in filelist:
            log.blue("Duplicate file, not uploading: "+ capturefile)
        else:
            GoogleDrive.UploadFile('/home/pi/Camera/Capture/',capturefile, folder)


def DeleteOldestFiles(path='.',numdaystokeep=5):
    log.white("Deleting Old Items")
    command ='find '+path+' -mtime +'+str(numdaystokeep)+' -type f -delete'
    p = Popen(command, shell=True, stdout=PIPE, close_fds=True)

def ScheduleEvents():
    """ Put constant scheduled events here (i.e. things that should happen every day).
    # Variable events go in the recurringScheduleEvent function """

def OnceDailyRecurringEvents():
    log.yellow("Executing OnceDailyRecurringEvents ")

    now = datetime.now()
    DeleteOldestFiles('/home/pi/Camera/Capture/')

def TwiceDailyRecurringEvents():
    """ Send Log out to Email """
    gmail.SendHTMLMail(log.ReturnHTMLLog())

if SchedulerPresent:
    # Starting run
    ThreadHelper.ScheduleThreadedRecurringAtTime("11:58",OnceDailyRecurringEvents, color="yellow")
    ThreadHelper.ScheduleThreadedRecurringAtTime("11:59",TwiceDailyRecurringEvents, color="yellow")
    ThreadHelper.ScheduleThreadedRecurringAtTime("23:59",TwiceDailyRecurringEvents, color="yellow")
    # Plan to run at noon every day
    OnceDailyRecurringEvents()

    ScheduleEvents()

TestRunOnce = True
log.white("Starting main loop",True)
while True:

    if not MotionHostCreated:
        MotionHostCreated = True
        log.cyan("creating new motion host")
        ThreadHelper.RunThreaded(CreateMotionHost,'192.168.1.92', MotionPort,threadname="MotionHost")

    message = ''

    if MotionHostConnectedStatus:
        message = HostListen()
        if message != '':
            log.blue("Message Recieved = "+message)
            if 'MotionDetected' in message:
                MotionHostCreated = False
                MotionHostConnectedStatus = False
                MotionHost.close_socket()
                if message == 'MotionDetected':
                    OnMotionDetectedEvent()
                    #ThreadHelper.RunThreaded(OnMotionDetectedEvent,threadname="AllMotionDetectedEvent")
                    #globals.trigger['AllMotionDetected'].status = True
                else:
                    zone = message[-1]
                    log.blue("zone="+ zone)
                    OnMotionDetectedEvent(zone)
                    #globals.trigger['ZoneMotionDetected'].status = True
                    #ThreadHelper.RunThreaded(OnMotionDetectedEvent, (zone,),threadname="ZoneMotionDetectedEvent")
                ThreadHelper.PrintThreadNumber()
    if globals.VerboseLogging:
        now = datetime.now()

# Functions to execute whenever JustArrivedHome is set to True
    #globals.trigger['AllMotionDetected'].Test(textnotify=False, execiftriggered=OnMotionDetectedEvent)

    if TestRunOnce:
        TestRunOnce = False

    # Run scheduler
    if SchedulerPresent:
        schedule.run_pending()








