#!/usr/bin/python
#!/usr/bin/env python
import os, sys
from subprocess import Popen, PIPE
import time
import threading
sys.path.append('/home/pi/PythonUtilities')
sys.path.append('/home/pi/Camera/Logfiles')
import logger
from logger import logging
import globals
from datetime import datetime
from datetime import timedelta
import gmail
import schedule
import watchdog


DebugMode = False
SchedulerPresent = False
WatchDogLocal = False
WatchDogRemote = True
MutualWatchDog = True

globals.VerboseTexting = False
globals.VerboseLogging = True
globals.VerboseModuleLogging = False


#Start Log
logger.CreateLog('Camera1', logpath='./Logfiles')

# Spawn a watchdog process to notify if the main process fails
if WatchDogRemote:
    watchdog.CreateHost('192.168.1.92',54321, 'Camera1')
    globals.RunThreaded(watchdog.AcceptConnections)
    globals.RunThreaded(watchdog.SendWatchdogHeartbeat)
    if MutualWatchDog:
        globals.RunThreaded(watchdog.WatchDog, ('192.168.1.91', 12345, 'HomeControl'))


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
    if globals.VerboseLogging:
        now = datetime.now()

    if TestRunOnce:
        TestRunOnce = False

    # Run scheduler
    if SchedulerPresent:
        schedule.run_pending()








