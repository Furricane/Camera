import time
from datetime import datetime
from datetime import timedelta
from LogHelper import logging
import configparser
import globals
import CFGFileHelper
import gmail
import ThreadHelper

triggercfgpath = './Triggers/triggers.ini'

class Trigger(object):
    'class for various triggers'
    name = ''
    status = False
    zone = 0  # 0 means all motion
    triggered = False
    cause = ''
    timelasttriggered = datetime.strptime('1Jan2000', '%d%b%Y')
    def __init__(self, name, zone=0):
        self.name = name
        self.status = False
        self.triggered = False
        self.zone = int(zone)
        self.info()
    def info(self):
        print(self.name+'.status='+str(self.status)+', zone='+str(self.zone)+', trig='+str(self.triggered)+', time='+str(self.timelasttriggered))
    def __str__(self):
        return (self.name)
    def ResettoDefaults(self):
        self.status = False
        self.triggered = False
        self.timelasttriggered = datetime.strptime('1Jan2000', '%d%b%Y')
    def Reset(self, delay=120):
        """ Resets a global trigger object status variable to False, after a delay """
        print('Resetting '+self.name+' status and triggered state to false')
        time.sleep(delay)
        self.status = False
        self.triggered = False
    def GetStatus(self, triggertocompare=None):
        ''' Returns the status of a trigger, or if a second trigger is given returns True if both status are true'''
        if triggertocompare == None:
            return self.status
        else:
            if self.status and globals.trigger[triggertocompare].status:
                return True
            else:
                return False
    def GetDelay(self, triggertocompare):
        ''' Returns the time in seconds between the timelasttriggered of the current object and
        the timelasttriggered of the triggertocompare object'''
        delay = (self.timelasttriggered - globals.trigger[triggertocompare].timelasttriggered)
        if globals.VerboseLogging:
            logging.info(self.name+str(self.timelasttriggered))
            logging.info(globals.trigger[triggertocompare].name+str(globals.trigger[triggertocompare].timelasttriggered))
            logging.info('  Delay='+str(delay))
        return delay
    def TestDelay(self, delay, lowerbound, upperbound):
        if (delay < timedelta(seconds=upperbound)) and (delay > timedelta(seconds = lowerbound)):
            return True
        else:
            return False
    def Test(self, textnotify=False, execiftriggered=None,settrueiftriggered=None, maxdelay=200, triggertocompare=None):
        if self.status and not self.triggered:
            self.triggered = True
            self.timelasttriggered = datetime.now()
            logging.info('globals.trigger['+self.name+'] = True')
            if execiftriggered != None:
                ThreadHelper.RunThreaded(execiftriggered)
            if textnotify:
                ThreadHelper.RunThreaded(gmail.SendText, (self.name,))
            ThreadHelper.RunThreaded(self.Reset, (600,))


# creates dictionaries in this format { str : str }
triggerdict = CFGFileHelper.read(triggercfgpath, 'triggers')

# Initial Trigger objects
globals.trigger = {}
for key in triggerdict:
    #print(key, 'corresponds to', triggerdict[key])
    globals.trigger[key] = Trigger(key, triggerdict[key])
