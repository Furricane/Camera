from datetime import datetime
import time
import queue
import schedule
import threading


NestAway = False
ElkZoneStatusRefreshed = False
ElkOutputStatusRefreshed = False
ElkPLCStatusRefreshed = False
ElkRTCRefreshed = False
ElkInitComplete = False
ElkWaitingOnCommandFlag = False
ElkWaitingOnCommand = ''
ElkReceivedSerialData = False
ElkZoneChangedFlag = False
ElkLastSerialDataTime = None
ElkZoneChangeList=[]
ElkOutputChangeList=[]
ElkArmed = False
ElkArmedStateChangedFlag = False
ElkAlarm = False
ElkAlarmStateChangedFlag = False

ElkQueue= queue.Queue()

HueBulbChangedFlag = False

RecurringTimerSet = False
AlarmTriggeredFlag = False

LogFilename = 'Logfile'

Zone = {}
Output = {}
trigger = {}

HueSession = None

MaxHomeCalendarEventList=[]
MaxHomeCalendarEvent = False
HomeAutomationCalendarWakeEventList=[]
HomeAutomationCalendarWakeEvent = False

CalService = None
CalPageToken = None

VerboseLogging = False
VerboseTexting = False
VerboseModuleLogging = False

daylist = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

def printGlobals():
    print('NestAway = '+str(NestAway))
    for key in trigger:
        trigger[key].info()


def RunThreaded(job_func, arguments='',threadname='Unnamed'):
    """ Creates a new thread to run the passed function """
    job_thread = threading.Thread(target=job_func,args=arguments,name=threadname)
    job_thread.start()
    return job_thread

def RunThreadedAndCancel(job_func, arguments=''):
    """ Used to run a scheduled task just one time, and in a new thread  """
    job_thread = threading.Thread(target=job_func,args=arguments)
    job_thread.start()
    return schedule.CancelJob


