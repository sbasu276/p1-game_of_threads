from PollingSocket import PollingSocket 

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

if __name__ == "__main__" :
	server = PollingSocket(HOST, PORT)
	requests_list = server.test()

#	for request in request_list:
		

	
