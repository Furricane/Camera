#!/usr/bin/python
try:
    import codecs
except ImportError:
    codecs = None
import logging.handlers
import time
import os
import globals
from configparser import SafeConfigParser

parser = SafeConfigParser()
parser.read('/home/pi/Camera/Utilities/logger.ini')

# Read path to log file
LOG_PATH = parser.get('config', 'log_path')

def WriteFormatted(datalist,columnwidthlist=[20]):
    forstring = ''
    datastring = ''
    if len(columnwidthlist) != len(datalist):
        columnwidth = columnwidthlist[0]
        for item in datalist:
            forstring += '{:'+str(columnwidth)+'} '
            datastring += item+','
    else:
        i = 0
        for item in datalist:
            forstring += '{:'+str(columnwidthlist[i])+'} '
            datastring += item+','
            i += 1
    datastring = datastring[:-1]
    #logging.info(datastring) # Send CSV data to logfile
    datatuple = tuple(datastring.split(','))
    printlogdata = forstring.format(*datatuple)
    #print(printlogdata) # Send nice data to console
    logging.info(printlogdata)

class MyTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self,dir_log):
        self.dir_log = dir_log
        filename = self.dir_log+'_'+time.strftime("%m%d%Y")+".log" #dir_log here MUST be with os.sep on the end
        logging.handlers.TimedRotatingFileHandler.__init__(self,filename, when='midnight', interval=1, backupCount=0, encoding=None)
    def doRollover(self):
        """
        TimedRotatingFileHandler remix - rotates logs on daily basis, and filename of current logfile is time.strftime("%m%d%Y")+".txt" always
        """
        self.stream.close()
        # get the time that this sequence started at and make it a TimeTuple
        t = self.rolloverAt - self.interval
        timeTuple = time.localtime(t)
        self.baseFilename = self.dir_log+'_'+time.strftime("%m%d%Y")+".log"
        if self.encoding:
            self.stream = codecs.open(self.baseFilename, 'w', self.encoding)
        else:
            self.stream = open(self.baseFilename, 'w')
        self.rolloverAt = self.rolloverAt + self.interval
    def ReturnLog(self):
        file=open(self.baseFilename)
        logtext = file.read()
        file.close()
        return logtext

globals.LogFilename = parser.get('config', 'log_filename')
console = MyTimedRotatingFileHandler(LOG_PATH+'/'+globals.LogFilename)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-4s %(message)s',
                    datefmt='%m/%d %H:%M:%S',
                    filemode='w')
# define a Handler which writes INFO messages or higher to the sys.stderr
#console = logging.StreamHandler()
#console = handlers.TimedRotatingFileHandler(filename=LOG_PATH+'/'+globals.LogFilename, when='midnight', interval=1)
console.setLevel(logging.INFO)
# set a format which is simpler for console use
# old formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
formatter = logging.Formatter('%(asctime)s %(levelname)-4s %(message)s',datefmt='%m/%d/%y %H:%M:%S',)
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

logging.info('Starting logfile.')

if not globals.VerboseModuleLogging:
# Turn off all the INFO logging in requests
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("schedule").setLevel(logging.WARNING)
    logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.WARNING)

