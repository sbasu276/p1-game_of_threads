import sys
import socket
import threading
from cache import Cache
from persistent import Persistent
from utils import parse_req, get, put, delete

class MultiThreadedServer(object):
    def __init__(self, host, port, cache_size, db_name):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.cache = Cache(cache_size)
        self.persistent = Persistent(db_name)
        self.lock = threading.Lock()

    def run_server(self):
        self.sock.listen(5)
        while True:
            client_sock, address = self.sock.accept()
            pthread = threading.Thread(target = self.thread_handler, \
                                       args = (client_sock,address))
            pthread.start()
    
    def thread_handler(self, client_sock, address):
        size = 1024
        data = ""
        print("in handler")
        while True:
            transfer = client_sock.recv(size)
            data = data + transfer.decode('utf-8')
            if '\n' in transfer.decode('utf-8'):
                break
        req = parse_req(data)
        if req.op == 'GET':
            self.lock.acquire()
            value = get(req.key, self.cache, self.persistent)
            self.lock.release()
            if value is None:
                value = "NOT FOUND"
            #TODO send in batches.
            client_sock.send(value.encode('utf-8'))
        elif req.op in ['PUT', 'INSERT']:
            self.lock.acquire()
            put(req.key, req.value, self.cache, self.persistent)
            self.lock.release()
            client_sock.send("ACK".encode('utf-8'))
        elif req.op == 'DELETE':
            self.lock.acquire()
            delete(req.key, self.cache, self.persistent)
            self.lock.release()
            client_sock.send("ACK".encode('utf-8'))
        else:
            client_sock.send("WRONG OPERATION".encode('utf-8'))

        client_sock.close()

if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    cache_size = int(sys.argv[3])
    db_name = sys.argv[4]
    # No sanity check for input
    server = MultiThreadedServer(host, port, cache_size, db_name)
    server.run_server()
