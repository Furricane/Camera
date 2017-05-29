#!/usr/bin/python
#!/usr/bin/env python
import os, sys
os.chdir('/home/pi/Camera/') # Change working directory
sys.path.append('/home/pi/PythonUtilities')
import socketcomm


#print(os.getcwd())

HostAddress = '192.168.1.92'
HostPort = 44444



def NotifyHost(HostAddress, HostPort):
    connectedstatus = False
    client, connectedstatus = socketcomm.CreateClient(HostAddress, HostPort)
    print('connectedstatus = %s' % (str(connectedstatus)))
    if connectedstatus:
        print('connection established')
        client.write('MotionDetected')
    else:
        print("unconnected")

NotifyHost(HostAddress, HostPort)








