import time
import sys
import socket
import threading
from cache import Cache
from persistent import Persistent
from utils import parse_req, get, put, insert, delete

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

        self.max_throughput=0
        self.current_number_of_responses=0
    
        self.current_max_throughput=0
        self.get_times=['BREAK']
        self.put_times=['BREAK']
        self.current_elapsed_time=0
        self.total_number_of_responses_so_far=0


    def update_throughput_and_others(self,request_type,response_time):
        self.total_number_of_responses_so_far+=1
        flag=0
        if (self.current_number_of_responses <5):
            self.current_number_of_responses+=1
            if (request_type == "PUT"):
                self.put_times.append(response_time)
            elif (request_type == "GET"):
                self.get_times.append(response_time)
        elif (self.current_number_of_responses == 5):
            temp_throughput= (5/self.current_elapsed_time)
            if (self.current_max_throughput<temp_throughput):
                self.current_max_throughput = temp_throughput
                flag=1
            if (request_type == "PUT" and flag==0):
                self.put_times.append('BREAK')
                self.put_times.append(response_time)
            elif (request_type == "GET" and flag==0):
                self.get_times.append('BREAK')
                self.get_times.append(response_time)
            elif (request_type == "PUT" and flag==1):
                self.put_times.append('BREAK_MAX')
                self.put_times.append(response_time)
            elif (request_type == "GET" and flag==1):
                self.get_times.append('BREAK_MAX')
                self.get_times.append(response_time)
            self.current_number_of_responses=1
    
	   

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
            get_start_time=time.time()

            self.lock.acquire()
            value = get(req.key, self.cache, self.persistent)
            self.lock.release()
            get_response_time= time.time()-get_start_time
            self.current_elapsed_time+= get_response_time
            self.update_throughput_and_others("GET")
            if value is None:
                value = "NOT FOUND"
            #TODO send in batches.
            client_sock.send(value.encode('utf-8'))
        elif req.op == 'PUT':
            put_start_time=time.time()

            self.lock.acquire()
            put(req.key, req.value, self.cache, self.persistent)
            self.lock.release()
            put_response_time= time.time()-put_start_time
            self.current_elapsed_time+=put_response_time
            self.update_throughput_and_others("PUT",put_response_time)
            client_sock.send("ACK".encode('utf-8'))
        elif req.op == 'INSERT':
            insert_start_time=time.time()

            self.lock.acquire()
            insert(req.key, req.value, self.cache, self.persistent)
            self.lock.release()
            insert_response_time= time.time()-insert_start_time
            self.current_elapsed_time+=insert_response_time

            self.update_throughput_and_others('INSERT',insert_response_time)
            client_sock.send("ACK".encode('utf-8'))
        elif req.op == 'DELETE':
            delete_start_time=time.time()

            self.lock.acquire()
            delete(req.key, self.cache, self.persistent)
            self.lock.release()
            delete_response_time= time.time()-delete_start_time
            self.current_elapsed_time+=delete_response_time

            self.update_throughput_and_others('DELETE',delete_response_time)
            client_sock.send("ACK".encode('utf-8'))
        else:
            client_sock.send("WRONG OPERATION".encode('utf-8'))
        self.cache.show()
        print("Best throughput so far.....")
        print(self.current_max_throughput)

        client_sock.close()

if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    cache_size = int(sys.argv[3])
    db_name = sys.argv[4]
    # No sanity check for input
    server = MultiThreadedServer(host, port, cache_size, db_name)
    server.run_server()
