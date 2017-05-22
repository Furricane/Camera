#!/usr/bin/python
import configparser
import globals

# # Read path to log file
# LOG_PATH = parser.get('config', 'log_path')
# LOG_FILENAME = parser.get('config', 'log_filename')+'.log'


def read(path, section):
    Config = configparser.ConfigParser()
    Config.optionxform = str # Otherwise config parser will convert everything to lower case
    Config.read(path)

    if globals.VerboseLogging:
        print('Reading '+section+' from configuration file')
    tempdict ={}
    options = Config.options(section)
    for option in options:
        try:
            #print Config.get(section, option)
            tempdict[option] = Config.get(section, option)
            #print option,tempdict[option]
        except:
            print("exception on %s!" % option)
            tempdict[option] = None
        #print option, tempdict[option]
    return tempdict
