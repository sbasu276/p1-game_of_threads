from polling import PollingSocket
from cache import Cache
from persistent import Persistent
from queue import Queue
from utils import parse_req, add_response
import sys
from helper_threads import Thread, io_handler

class PollingServer:
    def __init__(self, host, port, cache_size, db_name, workers):
        self.host = host
        self.port = port
        self.cache = Cache(cache_size)
        self.persistent = Persistent(db_name)
        self.req_queue = Queue() # Unbounded queue
        self.resp_queue = Queue()
        self.pool = {}
        self.workers = workers #number of workers in thread pool
        self.polling = None

    def init_helpers(self):
        for i in range(self.workers):
            self.pool[i] = Thread(target=io_handler, \
                                  args=(self.req_queue, \
                                        self.resp_queue,\
                                        self.persistent, ))
                                  
    def run_helpers(self):    
        for thread in self.pool.values():
            thread.start()

    def run_server(self):
        self.polling = PollingSocket(self.host, self.port)
        self.init_helpers()
        self.run_helpers()
        while True:
            requests = self.polling.poll_connection()
            for request in requests:
                #request is a tuple of sock, request_data
                data = request[1]
                print("RECV ",data)
                #Process request here
                req = parse_req(data.decode('utf-8'))
                req.fd = request[0]

                if req.op == 'GET':
                    val = self.cache.get(req.key)
                    if val is None:
                        # Cache miss: non-blocking put to req_queue
                        # for helper_threads to consume 
                        self.req_queue.put(req, block=False)
                        print("REQ SUB")
                    else:
                        resp = val
                        add_response(self.polling.sock_data_map, request[0], resp)
                
                elif req.op == 'PUT':
                    retval = self.cache.put(req.key, req.value)    
                    if retval is None:
                        self.req_queue.put(req, block=False)
                        cache.insert(req.key, req.value)
                    else:
                        resp = "ACK"
                        add_response(self.polling.sock_data_map, request[0], resp)

                elif req.op == 'INSERT':
                    retkey, retval = self.cache.insert(req.key, req.value)
                    if retkey and retval:
                        self.req_queue.put(req, block=False)
                    resp = "ACK"
                    add_response(self.polling.sock_data_map, request[0], resp)
                
                elif req.op == 'DELETE':
                    self.cache.delete(req.key)
                    self.req_queue.put(req, block=False)
                    resp = "ACK"
                    add_response(self.polling.sock_data_map, request[0], resp)

                else:
                    resp = "WRONG OPERATION".encode('utf-8')
                    add_response(self.polling.sock_data_map, request[0], resp)

            # Consume from response queue (non-blocking)
            try:
                completion = self.resp_queue.get(block=False)
                print("Compl ", completion.value)
                #completion.value is actual value for GET
                #for PUT/INSERT/DEL, value is "ACK" message
                #value is "-1" for all errors
                resp = completion.value
                add_response(self.polling.sock_data_map, completion.fd, resp)
            except:
                pass


if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    cache_size = int(sys.argv[3])
    db_name = sys.argv[4]
    num_worker = int(sys.argv[5])
    server = PollingServer(host, port, cache_size, db_name, num_worker)
    server.run_server()
