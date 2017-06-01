#!/usr/bin/python
#!/usr/bin/env python
import os, sys
os.chdir('/home/pi/Camera/') # Change working directory
sys.path.append('/home/pi/PythonUtilities')
import socketcomm

#print(os.getcwd())

HostAddress = '192.168.1.92'
HostPort = 44444

def NotifyHost(HostAddress, HostPort, Message):
    connectedstatus = False
    client, connectedstatus = socketcomm.CreateClient(HostAddress, HostPort)
    print('connectedstatus = %s' % (str(connectedstatus)))
    if connectedstatus:
        print('connection established')
        client.write(Message)
    else:
        print("unconnected")

print("# of arguments= ", len(sys.argv))        

if len(sys.argv) == 1:
    Message = 'MotionDetected'
else:
    Message = 'MotionDetectedZone'+str(sys.argv[1])

NotifyHost(HostAddress, HostPort, Message)








