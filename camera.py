#!/usr/bin/python
#!/usr/bin/env python
import os, sys
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

print("Python Version: %s.%s.%s" % sys.version_info[:3])
os.chdir('/home/pi/Camera/') # Change working directory

DebugMode = False
SchedulerPresent = True
WatchDogRemote = False
MutualWatchDog = False
MotionHost = True

globals.VerboseTexting = False
globals.VerboseLogging = True
globals.VerboseModuleLogging = False

MotionPort = 44444
MotionHostCreated = False
MotionHostConnectedStatus = False


#Start Log
log.init('Camera1', './Logfiles', './logger.ini')
#log.DisableModuleLogging()


# Spawn a watchdog process to notify if the main process fails
if WatchDogRemote:
    watchdog.create_host('192.168.1.92', 54321, 'Camera1')
    ThreadHelper.run_threaded(watchdog.accept_connections, threadname="WatchdogAcceptConnections")
    ThreadHelper.run_threaded(watchdog.send_watchdog_heartbeat, threadname="WatchdogHeartbeat")
    if MutualWatchDog:
        ThreadHelper.run_threaded(watchdog.watch_dog, '192.168.1.91', 12345, 'HomeControl',threadname="MutualWatchdog")


def create_motion_host(host_address, host_port):
    global MotionHost
    global MotionHostConnectedStatus
    MotionHost, connectedstatus = socketcomm.create_host(host_address, host_port)
    log.cyan("creating motion host with port: " + str(host_port))
    while True:
        try:
            MotionHost.accept_connection()
            log.cyan("Motion Connection accepted!")
            MotionHostConnectedStatus = True
            break
        except BlockingIOError:
            pass


def host_listen():
    global MotionHost
    data = MotionHost.read()
    #print(str(data))
    if data != b"":
        message = data.decode()
        message = message.strip()
        # print("Message Received:", message)
        return message
    else:
        return ''


def list_files(path, extension):
    return [f for f in os.listdir(path) if f.endswith(extension)]


def listdir_shell(path, *lsargs):
    p = Popen(('ls', path) + lsargs, shell=False, stdout=PIPE, close_fds=True)
    # for path in p.stdout.readlines():
    #    print(path.strip())
    # return [path.rstrip('\n') for path in p.stdout.readlines()]
    return [path.strip() for path in p.stdout.readlines()]


def get_directory_file_list(path='.', extfilter=None, numitems = None, mostrecent=True):
    command ='ls '+path
    if extfilter is None:
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


def on_motion_detected_event(zone=None):
    if zone == None:
        zonemsg = 'All'
    else:
         zonemsg = str(zone)
         gmail.SendText("Motion Detected Zone "+zonemsg)

    log.blue("executing on motion events - " + zonemsg)
    #dirlist = listdir_shell('/home/pi/Camera/Capture/', '-t')[:10]
    dirlist = get_directory_file_list('/home/pi/Camera/Capture/', numitems=10)
    #jpgdirlist = listdir_shell('/home/pi/Camera/Capture/', '*.jpg -t')[:1]
    jpgdirlist= get_directory_file_list('/home/pi/Camera/Capture/', extfilter='*.jpg', numitems=1)
    log.blue("Starting notify loop")
    #gmail.SendMail("Camera Motion Detected","Camera Motion Detected "+zonemsg)
    print(jpgdirlist)
    gmail.send_mail("Camera Motion Detected Upload", "Camera Motion Detected Upload"+zonemsg,jpgdirlist, path='/home/pi/Camera/Capture/')
    folder = GoogleDrive.create_folder('CameraTest')
    filelist, ids = GoogleDrive.get_file_list('CameraTest')

    for capturefile in dirlist:
        if capturefile in filelist:
            log.blue("Duplicate file, not uploading: "+ capturefile)
        else:
            GoogleDrive.upload_file('/home/pi/Camera/Capture/',capturefile, folder)


def delete_oldest_files(path='.', numdaystokeep=5):
    log.white("Deleting Old Items")
    command ='find '+path+' -mtime +'+str(numdaystokeep)+' -type f -delete'
    p = Popen(command, shell=True, stdout=PIPE, close_fds=True)


def schedule_events():
    """ Put constant scheduled events here (i.e. things that should happen every day).
    # Variable events go in the recurringScheduleEvent function """


def once_daily_recurring_events():
    log.yellow("Executing OnceDailyRecurringEvents ")

    now = datetime.now()
    delete_oldest_files('/home/pi/Camera/Capture/')


def twice_daily_recurring_events():
    """ Send Log out to Email """
    gmail.SendHTMLMail(log.ReturnHTMLLog())


if SchedulerPresent:
    # Starting run
    ThreadHelper.schedule_threaded_recurring_at_time("11:58", once_daily_recurring_events, color="yellow")
    ThreadHelper.schedule_threaded_recurring_at_time("11:59", twice_daily_recurring_events, color="yellow")
    ThreadHelper.schedule_threaded_recurring_at_time("23:59", twice_daily_recurring_events, color="yellow")
    # Plan to run at noon every day
    once_daily_recurring_events()

    schedule_events()

TestRunOnce = True
log.white("Starting main loop",True)
while True:

    if not MotionHostCreated:
        MotionHostCreated = True
        log.cyan("creating new motion host")
        ThreadHelper.run_threaded(create_motion_host, '192.168.1.92', MotionPort, threadname="MotionHost")

    message = ''

    if MotionHostConnectedStatus:
        message = host_listen()
        if message != '':
            log.blue("Message Recieved = "+message)
            if 'MotionDetected' in message:
                MotionHostCreated = False
                MotionHostConnectedStatus = False
                MotionHost.close_socket()
                if message == 'MotionDetected':
                    on_motion_detected_event()
                    #ThreadHelper.RunThreaded(OnMotionDetectedEvent,threadname="AllMotionDetectedEvent")
                    #globals.trigger['AllMotionDetected'].status = True
                else:
                    zone = message[-1]
                    log.blue("zone="+ zone)
                    on_motion_detected_event(zone)
                    #globals.trigger['ZoneMotionDetected'].status = True
                    #ThreadHelper.RunThreaded(OnMotionDetectedEvent, (zone,),threadname="ZoneMotionDetectedEvent")
                ThreadHelper.print_thread_number()
    if globals.VerboseLogging:
        now = datetime.now()

# Functions to execute whenever JustArrivedHome is set to True
    #globals.trigger['AllMotionDetected'].Test(textnotify=False, execiftriggered=OnMotionDetectedEvent)

    if TestRunOnce:
        TestRunOnce = False

    # Run scheduler
    if SchedulerPresent:
        schedule.run_pending()








