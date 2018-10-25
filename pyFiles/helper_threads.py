from multiprocessing import Pool as ThreadPool
from queue import Queue

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
                event.value = persistent.get(event.key)
            elif event.op in ['PUT', 'INSERT']:
                persistent.put(event.key, event.value)
            elif event.op == 'DELETE':
                persistent.delete(event.key)
            else:
                pass
            resp_queue.put(event)
        except:
            pass
            
