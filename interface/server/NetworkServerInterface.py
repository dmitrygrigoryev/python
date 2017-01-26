import threading
import socket
# OBSERVERVABLE  
class NetworkServerInterface(threading.Thread):
    """
        Class for network connection in another thread
        NetworkServerInterface - Observable object for QueueManager observer
        
        CONSTRUCTOR:
                interface = NetworkServerInterface('2727')
                
        PROPERTIES:
                self.web_port = web_port
                self.observers = []
                
        METHODS:
                def __init__():
                def register():
                def notify_observers():
                def close():
    """
    def __init__(self,web_port):
        threading.Thread.__init__(self)
        self.web_port = web_port
        self.observers = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def run(self):
        self.server_socket.bind(('10.50.70.173', 2727))
        self.server_socket.listen(10)
        while True:
            channel, details = self.server_socket.accept()
            data = channel.recv(1024)
            # a = data.split('::')
            if data:
               self.notify_observers(data)
               if data=='exit':
                    break
    def register(self,observer):
        self.observers.append(observer)
    def notify_observers(self,msg):
        for observer in self.observers:
            observer.recv_message(msg)
    def close(self):
        self.server_socket.close()
        