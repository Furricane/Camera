# Create a host or client socket connection
# http://stackoverflow.com/questions/1708835/python-socket-receive-incoming-packets-always-have-a-different-size
# tcp_echo_server.py
import socket
import time

class SocketComm():
    conn = None
    host = False
    connections = []
    HostAddress = 'localhost' #192.168.1.91'#"localconn"
    HostPort = 54321
    NUMCLIENTS = 1
    ConnectedStatus = False
    def __init__(self, HostAddress='localhost', HostPort=12345, host=True, NUMCLIENTS=1):
        self.host = host
        self.HostAddress = HostAddress
        self.HostPort = HostPort
        if host:
            try:
                self.NUMCLIENTS = NUMCLIENTS
                self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
                self.conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
                self.conn.setblocking(0)
                self.conn.bind((self.HostAddress, self.HostPort))
                self.conn.listen(self.NUMCLIENTS)  # how many clients it accepts
                print('Host socket creation successful')
                print('Address: %s, Port: %s' % (self.HostAddress, self.HostPort))
                self.ConnectedStatus = True
            except:
                print('Host socket creation unsuccessful')
        else:
            try:
                self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
                self.conn.connect((self.HostAddress, self.HostPort))
                self.conn.setblocking(0)
                print('Client socket creation successful')
                print('Address: %s, Port: %s' % (self.HostAddress, self.HostPort))
                self.ConnectedStatus = True
            except:
                print('Client socket creation unsuccessful')
    def __del__(self):
        if self.host:
            for i in reversed(range(len(self.connections))):
                self.close_socket(self.connections[i][0])
                self.connections.pop(i)
        self.close_socket(self.conn)
    def AcceptConnection(self):
        con,addr = self.conn.accept()
        print ('Got connection from',addr)
        self.connections.append((con, addr))
    def close_socket(self, connection=None):
        if connection == None:
            connection = self.conn
        try:
            connection.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            connection.close()
        except:
            pass

    def read(self):
        if self.host:
            for i in reversed(range(len(self.connections))):
                try:
                    data, sender = self.connections[i][0].recvfrom(1500)
                    return data
                except (BlockingIOError, socket.timeout, OSError):
                    pass
                except (ConnectionResetError, ConnectionAbortedError):
                    self.close_socket(self.connections[i][0])
                    self.connections.pop(i)
            return b''  # return empty if no data found
        else:
            try:
                data, sender = self.conn.recvfrom(1500)
                return data
            except (BlockingIOError, socket.timeout, AttributeError, OSError):
                return b''
            except (ConnectionResetError, ConnectionAbortedError, AttributeError):
                self.close_socket(self.conn)
                return b''           
    def write(self,data):
        if self.host:
            for i in reversed(range(len(self.connections))):
                try:
                    data =  bytes(data, 'UTF-8')
                    self.connections[i][0].sendto(data, self.connections[i][1])
                except (BlockingIOError, socket.timeout, OSError):
                    pass
                except (ConnectionResetError, ConnectionAbortedError):
                    self.close_socket(self.connections[i][0])
                    self.connections.pop(i)
        else:
            try:
                self.conn.sendto(data, (self.HostAddress, self.HostPort))
            except (ConnectionResetError, ConnectionAbortedError):
                self.close_socket(self.conn)           

def CreateHost(HostAddress, HostPort, NUMCLIENTS=1):
    x = SocketComm(HostAddress, HostPort, host=True, NUMCLIENTS=1)
    if x.ConnectedStatus:
        return x, True
    else:
        return x, False

def CreateClient(HostAddress, HostPort):
    x = SocketComm(HostAddress, HostPort, host=False)
    if x.ConnectedStatus:
        return x, True
    else:
        return x, False

