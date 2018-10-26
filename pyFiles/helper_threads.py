from queue import Queue
from threading import Thread, Lock

class OperationError(Exception):
    def __init__(self, op):
        self.op = op
    def __str__(self):
        return repr(self.op)

def io_handler(req_queue, resp_queue, persistent):
    while True:
        try:
            event = req_queue.get()
            if event.op == 'GET':
                value = persistent.get(event.key)
                event.value = value if value else "-1"
            elif event.op in ['PUT', 'INSERT']:
                try:
                    persistent.put(event.key, event.value)
                    event.value = "ACK"
                except:
                    event.value = "-1"
            elif event.op == 'DELETE':
                try:
                    persistent.delete(event.key)
                    event.value = "ACK"
                except:
                    event.value = "-1"
            else:
                pass
            resp_queue.put(event)
        except:
            pass
            
