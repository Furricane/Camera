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


print("Starting nofify loop")
gmail.SendMail("Camera Motion Detected","Camera Motion Detected")









