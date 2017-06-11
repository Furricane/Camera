from datetime import datetime
import time
import queue
import schedule
import threading


LogFilename = 'Logfile'

trigger = {}

VerboseLogging = False
VerboseTexting = False
VerboseModuleLogging = False

daylist = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

def printGlobals():
    print('NestAway = '+str(NestAway))
    for key in trigger:
        trigger[key].info()



