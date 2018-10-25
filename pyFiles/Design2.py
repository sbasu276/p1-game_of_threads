from PollingSocket import PollingSocket 

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

#Starting with no-write allocate and write-through caches

if __name__ == "__main__" :
	server = PollingSocket(HOST, PORT)
	requests_list = server.poll_connection()

	for item in request_list:
		op = item[1].strip('\n').split(' ')[0]
		key = item[1].strip('\n').split(' ')[1]
		value = item[1].strip('\n').split(' ')[-1]

		if(op == 'GET'): #GET operation
			if(value = check_in_cache(key)):  #available in cache
				continue
			else:
				value = file_read(key)
			respond_client(value)

		else(op == 'PUT'):
			# Update the cache if the entry exist
			if(value = check_in_cache(key)):
				update_cache(key, value)

			#Assign the update task to one of the threads in thread pool
			file_write(key, value)
			
			respond_client('DONE')
