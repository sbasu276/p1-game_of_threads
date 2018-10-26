from time import sleep
import sys
import socket

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def send_data(self, message):
        try:
            self.sock.connect(server_address)
            self.sock.setblocking(0)
            # Send data
            self.sock.send(message)
            """
            amount_received = 0
            amount_expected = len(message)
            while amount_received < amount_expected:
                #sleep(1)
                data = self.sock.recv(2)
                amount_received += len(data)
                print >>sys.stderr, 'received "%s"' % data
            """
        finally:
            print >>sys.stderr, 'closing socket'
            self.sock.close()

if __name__ == "__main__":
    # Connect the socket to the port where the server is listening
    port = int(sys.argv[1])
    server_address = ('localhost', port)
    print "connecting to %s port %s"%(server_address, port)

    client = Client(server_address, port)
    data = "THIS IS A SAMPLE I/O MESSAGE WHICH WILL SLEEP\n"*1024*10
    client.send_data(data)


