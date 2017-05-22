# Spawn a Python Watchdog Client Subprocess 
# http://stackoverflow.com/questions/1708835/python-socket-receive-incoming-packets-always-have-a-different-size
import gmail
import socketcomm         
import time 
import globals

Unconnected = True
MainProcessIsAlive = True
HeartBeatRefreshed = False
HeartBeatTimerFlag = False #True when in timer
client = None

def WatchDog(HostAddress, HostPort):
    global client
    global Unconnected
    while Unconnected:
        connectedstatus = False
        client, connectedstatus = socketcomm.CreateClient(HostAddress, HostPort)
        print('Trying to establish Watchdog connection')
        print('connectedstatus = %s' % (str(connectedstatus)))
        if connectedstatus:
            Unconnected = False
            print('Watchdog connection established')
        else:
            time.sleep(60)
    WatchDogMonitor()

def WatchDogTimer():
    global HeartBeatTimerFlag
    global HeartBeatRefreshed
    global MainProcessIsAlive
    HeartBeatRefreshed = False
    time.sleep(120)
    if not HeartBeatRefreshed:
        print('MAINPROCESSALIVE=False')
        MainProcessIsAlive = False
    HeartBeatTimerFlag = False

def WatchDogMonitor():
    global HeartBeatTimerFlag
    global HeartBeatRefreshed
    global MainProcessIsAlive

    while True:
        if not HeartBeatTimerFlag:
            HeartBeatTimerFlag = True
            if not MainProcessIsAlive:
                print("Homecontrol has failed")
                gmail.SendText("Homecontrol has failed!")
                gmail.SendMail("Homecontrol has failed!","Homecontrol Watchdog")
                break
            #print('Spawning timer thread')
            globals.RunThreaded(WatchDogTimer)
        data = client.read()
        if data != b"":
            data = data.decode()
            data = data.strip()
            print("Message Received:", data)
            if 'Homecontrol is alive' in data:
                #print('REFRESHED=True')
                if not HeartBeatRefreshed:
                    HeartBeatRefreshed = True

    client.close_socket()

if __name__ == "__main__":
    client = WatchDog('localhost', 54321)
