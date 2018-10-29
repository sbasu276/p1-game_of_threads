import sys
import socket
import threading
from cache import Cache
from persistent import Persistent
from utils import parse_req, call_api
import signal
import time
import pickle

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

        self.interval = 10
        self.start = 5
    
    def run_server(self):
        self.sock.listen(5)
        tot_time = 0
        req = 0
        first = True
        log = []
        while True:

            start = time.time()
            if req:
                if first:
                    tot_time = 0
                    first = False
                log.append((tot_time, req))
                if req >= 1000.0:
                    with open('mts.log', 'ab') as f:
                        pickle.dump(log, f)
                    log = []
                    req = 0
                    tot_time = 0

            client_sock, address = self.sock.accept()
            pthread = threading.Thread(target = self.thread_handler, \
                                       args = (client_sock,address))
            pthread.start()
            req += 1
            #last = time.time()
            tot_time = tot_time + (time.time() - start) 



    
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
        resp = call_api(req, self.cache, self.persistent, self.lock)
        client_sock.send(resp.encode('utf-8'))
        self.cache.show()
        client_sock.close()


def handler(signum, frame):
    print("SIGHANDLER")
    with open('multi_threded_server_1.log', 'a') as f:
        f.write(str(measure.requests)+"\n")
    measure.requests = 0

if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    cache_size = int(sys.argv[3])
    db_name = sys.argv[4]
    start = 0
    interval = 1 
    signal.setitimer(signal.ITIMER_REAL, start, interval)
    signal.signal(signal.SIGALRM, handler)
    # No sanity check for input
    server = MultiThreadedServer(host, port, cache_size, db_name)
    server.run_server()
