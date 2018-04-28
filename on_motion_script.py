#!/usr/bin/python
#!/usr/bin/env python
import os, sys
import socketcomm
os.chdir('/home/pi/Camera/') # Change working directory
sys.path.append('/home/pi/PythonUtilities')


HostAddress = '192.168.1.92'
HostPort = 44444

def notify_host(host_address, host_port, message):
    connectedstatus = False
    client, connectedstatus = socketcomm.create_client(host_address, host_port)
    print('connectedstatus = %s' % (str(connectedstatus)))
    if connectedstatus:
        print('connection established')
        client.write(message)
    else:
        print("unconnected")

print("# of arguments= ", len(sys.argv))        

if len(sys.argv) == 1:
    Message = 'MotionDetected'
else:
    Message = 'MotionDetectedZone'+str(sys.argv[1])

notify_host(HostAddress, HostPort, Message)








