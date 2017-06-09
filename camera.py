#!/usr/bin/python
#!/usr/bin/env python
import os, sys
os.chdir('/home/pi/Camera/') # Change working directory
from subprocess import Popen, PIPE
import time
import threading
sys.path.append('/home/pi/PythonUtilities')
sys.path.append('/home/pi/Camera/Logfiles')
import LogHelper
from LogHelper import logging
import globals
from datetime import datetime
from datetime import timedelta
import gmail
import schedule
import watchdog
import GoogleDrive
import socketcomm


DebugMode = False
SchedulerPresent = False
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
LogHelper.Init('Camera1', logfilepath='./Logfiles')

# Spawn a watchdog process to notify if the main process fails
if WatchDogRemote:
    watchdog.CreateHost('192.168.1.92',54321, 'Camera1')
    globals.RunThreaded(watchdog.AcceptConnections)
    globals.RunThreaded(watchdog.SendWatchdogHeartbeat)
    if MutualWatchDog:
        globals.RunThreaded(watchdog.WatchDog, ('192.168.1.91', 12345, 'HomeControl'))

def CreateMotionHost(HostAddress, HostPort):
    global MotionHost
    global MotionHostConnectedStatus
    MotionHost, connectedstatus = socketcomm.CreateHost(HostAddress, HostPort)
    print("creating motion host with port",HostPort)
    while True:
        try:
            MotionHost.AcceptConnection()
            print("Motion Connection accepted!")
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

    print("executing on motion events - " + zonemsg)
    #dirlist = listdir_shell('/home/pi/Camera/Capture/', '-t')[:10]
    dirlist = GetDirectoryFileList('/home/pi/Camera/Capture/',numitems=10)
    #jpgdirlist = listdir_shell('/home/pi/Camera/Capture/', '*.jpg -t')[:1]
    jpgdirlist= GetDirectoryFileList('/home/pi/Camera/Capture/',extfilter='*.jpg',numitems=1)
    print("Starting notify loop")
    #gmail.SendMail("Camera Motion Detected","Camera Motion Detected "+zonemsg)
    print(jpgdirlist)
    gmail.SendMail2("Camera Motion Detected Upload","Camera Motion Detected Upload"+zonemsg,jpgdirlist, path='/home/pi/Camera/Capture/')
    folder = GoogleDrive.CreateFolder('CameraTest')
    filelist, ids = GoogleDrive.GetFileList('CameraTest')

    for capturefile in dirlist:
        if capturefile in filelist:
            print("Duplicate file, not uploading: ", capturefile)
        else:
            GoogleDrive.UploadFile('/home/pi/Camera/Capture/',capturefile, folder)


def ScheduleEvents():
    """ Put constant scheduled events here (i.e. things that should happen every day).
    # Variable events go in the recurringScheduleEvent function """

def OnceDailyRecurringScheduleEvents():
    print("Executing OnceDailyRecurringScheduleEvents ")

    now = datetime.now()

def TwiceDailyRecurringScheduleEvents():
    """ Send Log out to Email """
    gmail.SendMail(logger.console.ReturnLog())

if SchedulerPresent:
    # Starting run
    print("Starting Scheduled Events")
    schedule.every().day.at("11:58").do(globals.RunThreaded, OnceDailyRecurringScheduleEvents)
    logging.info('Scheduling Event: OnceDailyRecurringScheduleEvents at 11:58')
    schedule.every().day.at("11:59").do(globals.RunThreaded, TwiceDailyRecurringScheduleEvents)
    schedule.every().day.at("23:59").do(globals.RunThreaded, TwiceDailyRecurringScheduleEvents)
    logging.info('Scheduling Events: TwiceDailyRecurringScheduleEvents at 11:59 and 23:59')
    # Plan to run at noon every day
    OnceDailyRecurringScheduleEvents()

    ScheduleEvents()

TestRunOnce = True
print("Starting main loop")
while True:
    
    if not MotionHostCreated:
        MotionHostCreated = True
        print("creating new motion host")
        globals.RunThreaded(CreateMotionHost,['192.168.1.92', MotionPort])

    message = ''

    if MotionHostConnectedStatus:
        message = HostListen()
        if message != '':
            print("Message Recieved = ",message)
            if 'MotionDetected' in message:
                MotionHostCreated = False
                MotionHostConnectedStatus = False
                MotionHost.close_socket()
                if message == 'MotionDetected':
                    OnMotionDetectedEvent()
                else:
                    zone = message[-1]
                    print("zone=", zone)
                    OnMotionDetectedEvent(zone)
    if globals.VerboseLogging:
        now = datetime.now()

    if TestRunOnce:
        TestRunOnce = False

    # Run scheduler
    if SchedulerPresent:
        schedule.run_pending()








