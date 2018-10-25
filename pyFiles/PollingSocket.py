#!/usr/bin/env python3

import socket, selectors, types

class PollingINETSocket:

  def __init__(self, host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen()
    sock.setblocking(False)
    self.sel = selectors.DefaultSelector()
    events = selectors.EVENT_READ 
    self.sel.register(sock, events, data=None)
    self.sock_data_map = {}

  def accept_connection(self, sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    #TODO:change data to mutable key value pair
    data = types.SimpleNamespace(addr=addr, req=b'', resp=b'')
    self.sock_data_map[conn] = data
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    self.sel.register(conn, events, data=data)

  def service_connection(self, info, mask):
    sock = info.fileobj
    data = self.sock_data_map[sock]
    new_request = None
    if mask & selectors.EVENT_READ:
      recv_data = sock.recv(4096)  # Should be ready to read
      if recv_data: #TODO: recvall??
        data.req += recv_data
        if '\n' in data.req.decode():					#"\n" indicated end of request
          print("Received a request from :", data.addr, data.req)
          new_request = (sock, data.req)
          data.req = b''
        self.sock_data_map[sock] = data

      else:																						#empty message is close request
        print('closing connection to', data.addr)
        self.sel.unregister(sock)
        sock.close()
        new_request = None
    else:	# Write event has occured
      if data.resp:
        sent = sock.send(data.resp)
        data.resp = data.resp[sent:]
        self.sock_data_map[sock] = data

    return new_request


  def poll_connection(self):
    request_list = []
    events = self.sel.select(timeout=0)
    for info, mask in events:
      if info.data is None:  #empty data object if connection is not established already
        self.accept_connection(info.fileobj)
      else:
        request = self.service_connection(info, mask)
        if request is not None:
          request_list.append(request)
    return request_list


#class PollingUNIXSocket:
#
#  def __init__(self, num_sockets):
#		sockfd = []
#		for i in range(num_sockets):
#      ssock, csock = socket.socketPair()
#      ssock.setblocking(False)
#      self.sel = selectors.DefaultSelector()
#      self.sel.register(ssock, selectors.EVENT_READ, data=None)
#			sockfd.append(ssock)
#		return sockfd
#
#  def service_connection(self, info, mask):
#    sock = info.fileobj
#		#TODO: fix it with mutable key value pair
#    data = info.data
#    if mask & selectors.EVENT_READ:
#      recv_data = sock.recv(1024)  # Should be ready to read
#      if recv_data:
#        data.req += recv_data
#        if(data.req.decode().endswith('\n')):					#"\n" indicated end of request
##          print("Received a request from :", data.addr, data.req)
#          new_request = (sock, data.req)
#      else:																						#empty message is close request
#        print('closing connection to', data.addr)
#        self.sel.unregister(sock)
#        sock.close()
#				new_request = None
#    return new_request
#
#  def poll_connection(self):
#		request_list = []
#    while True:
#      events = self.sel.select(timeout=0)
#      for info, mask in events:
#				request_list.append(service_connection(info, mask))
#		return request_list

