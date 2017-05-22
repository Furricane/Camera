# Spawn a Python Watchdog Subprocess 
# http://stackoverflow.com/questions/1708835/python-socket-receive-incoming-packets-always-have-a-different-size
import socketcomm
import time             

host = None

def CreateHost(HostAddress, HostPort):
    global host
    host, connectedstatus = socketcomm.CreateHost(HostAddress, HostPort)

def SendWatchdogHeartbeat(delay = 60):
    global host
    while True:
        message = "Homecontrol is alive\n" 
        host.write(message)
        time.sleep(delay)

def AcceptConnections():
    global host
    while True:
        try:
            host.AcceptConnection()
            print("Connection accepted!")
            break
        except BlockingIOError:
            pass

