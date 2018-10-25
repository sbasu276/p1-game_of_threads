from PollingSocket import *
from cache import Cache
import sys

HOST = '127.0.0.1'		# Standard loopback interface address (localhost)
PORT = int(sys.argv[1])					# Port to listen on (non-privileged ports are > 1023)
NUMTHREADS = 10						# Number of threads in thread pool

#Starting with no-write allocate and write-through caches

if __name__ == "__main__" :

	#Initialisation Phase
	server			= PollingINETSocket(HOST, PORT)
#	thread_pool	= ThreadPool(NUMTHREADS)
#	cache				=	Cache(10)

#	while True:
#
#		request_list = server.poll_connection()
#		server.sock_data_map
#	
#		for item in request_list:
#			fd		=	item[0]
#			op		= item[1].strip('\n').split(' ')[0]
#			key		= item[1].strip('\n').split(' ')[1]
#			value	= item[1].strip('\n').split(' ')[-1]
#
#			value = cache.get(key)
#
#			if(op == 'GET'): #GET operation
#				if(value):  #cache hit
#					sent_bytes	= fd.send(value)
#					value				=	value[sent_bytes:]
#				else: #cache miss
#					e_key, e_value  = cache.evict()
#					if(): # Writing back the evicted line
#						thread_pool.submit('PUT', e_key, e_value)
#					# Reading the missed entry
#					thread_pool.submit('GET', key, value)
#	
#			else(op == 'PUT'): #PUT operation
#				if(value): #cahce hit
#					cache.put(key, value)
#				else: #cache miss
#					e_key, e_value = cache.evict()
#					if(e_key): # Writing back the evicted line
#						thread_pool.submit('PUT', e_key, e_value)
#					# Writing the missed entry
#					thread_pool.submit('GET', key, value)
#					pending_writes.append(key, value)

	while True:
		requests = server.poll_connection()
		if len(requests):
			data = server.sock_data_map[requests[0][0]]
			data.resp = b'Received!\n'
			server.sock_data_map[requests[0][0]] = data
	#		print(requests)
