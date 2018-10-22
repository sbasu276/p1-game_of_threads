#!/usr/bin/env python3

import socket, selectors, types

class PollingSocket:

  def __init__(self, host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen()
    sock.setblocking(False)
    self.sel = selectors.DefaultSelector()
    self.sel.register(sock, selectors.EVENT_READ, data=None)

  def accept_connection(self, sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, req=b'', resp=b'')
    events = selectors.EVENT_READ
    self.sel.register(conn, events, data=data)

  def service_connection(self, key, mask):
    sock = key.fileobj
    data = key.data
    new_request_list = []
    if mask & selectors.EVENT_READ:
      recv_data = sock.recv(1024)  # Should be ready to read
      if recv_data:
        data.req += recv_data
        if(data.req.decode().endswith('\n')):					#"\n" indicated end of request
#          print("Received a request from :", data.addr, data.req)
          new_request_list.append((sock, data.req))
      else:																						#empty message is close request
        print('closing connection to', data.addr)
        self.sel.unregister(sock)
        sock.close()
    return new_request_list


  def poll_connection(self):
    while True:
      events = self.sel.select(timeout=0)
      for key, mask in events:
        if key.data is None:  #empty data object if connection is not established already
          self.accept_connection(key.fileobj)
        else:
          return self.service_connection(key, mask)
