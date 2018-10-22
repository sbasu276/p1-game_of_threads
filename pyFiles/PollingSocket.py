#!/usr/bin/env python3

import socket, selectors,types

class PollingSocket:

  def __init__(self, host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen()
    sock.setblocking(False)
    self.sel = selectors.DefaultSelector()
    self.sel.register(sock, selectors.EVENT_READ, data=None)

  def accept_wrapper(self, sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    self.sel.register(conn, events, data=data)

  def service_connection(self, key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
      recv_data = sock.recv(1024)  # Should be ready to read
      if recv_data:
        data.outb += recv_data
      else:
        print('closing connection to', data.addr)
        self.sel.unregister(sock)
        sock.close()
    if mask & selectors.EVENT_WRITE:
      if data.outb:
        print('echoing', repr(data.outb), 'to', data.addr)
        sent = sock.send(data.outb)  # Should be ready to write
        data.outb = data.outb[sent:]

  def test(self):
    while True:
      events = self.sel.select(timeout=None)
      for key, mask in events:
        if key.data is None:
          self.accept_wrapper(key.fileobj)
        else:
          self.service_connection(key, mask)
