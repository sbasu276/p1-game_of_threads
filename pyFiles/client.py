from time import sleep
import sys
import socket

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(server_address)

    def send_data(self, message):
            # Send data
            self.sock.send(message)
            print("Request Sent: ", message)
            data = self.sock.recv(1024).decode('utf-8')
            print("Response Received: ",data)
            return data

if __name__ == "__main__":
    # Connect the socket to the port where the server is listening
    port = int(sys.argv[1])
    seed = int(sys.argv[2])
    server_address = ('localhost', port)

    client = Client(server_address, port)
    #client.send_data("GET xxx\n".encode('utf-8'))
    #client.send_data("DELETE Soumen Basu\n".encode('utf-8'))
    #client.send_data("INSERT Timmy Zhu\n".encode('utf-8'))
    #client.send_data("PUT Ram Mohan1\n".encode('utf-8'))
    #client.send_data("GET Ram\n".encode('utf-8'))
    resp = '0'
    for count in range(1000):
      client.send_data(("PUT Key"+str(seed)+" "+str(int(resp)+1)+" \n").encode('utf-8'))
      resp = client.send_data(("GET Key"+str(seed)+"\n").encode('utf-8'))
    #client.send_data("".encode('utf-8'))
