import socket
import sys
import threading

class MultiThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            print "listening for client..."
            #client.settimeout(60)
            pthread = threading.Thread(target = self.thread_handler, args = (client,address))
            pthread.start()
    
    def thread_handler(self, client, address):
        size = 1024
        data = client.recv(size)
        while data:
            data = client.recv(size)
        print "ALL DONE!"
        client.close()

if __name__ == "__main__":
    while True:
        port_num = sys.argv[1]
        try:
            port_num = int(port_num)
            break
        except ValueError:
            pass

    server = MultiThreadedServer('',port_num)
    server.listen()
