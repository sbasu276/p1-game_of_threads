class Request:
    def __init__(self, op=None, key=None, value=None, fd=None):
        self.op = op
        self.key = key
        self.value = value
        self.fd = fd

def parse_req(request):
    print("UTIL ", request)
    req = request.strip('\n').split()
    print(req)
    request = None
    if len(req)>2:
        request = Request(req[0], req[1], req[2])
    else:
        request = Request(req[0], req[1])
    return request

def add_response(mapper, sock, response):
    data = mapper[sock]
    data.resp = response
    mapper[sock] = data

def get(key, cache, persistent):
    val = cache.get(key)
    if val is None:
        val = persistent.get(key)
        if val:
            retkey, retval = cache.insert(key, val, dirty=False)
            if retkey and retval:
                persistent.put(retkey, retval)
    if val:
        return val
    else:
        return "-1"

def put(key, value, cache, persistent):
    retval = cache.put(key, value)
    if retval is None:
        persistent.put(key, value)
        retkey, retval = cache.insert(key, value, dirty=False)
        if retkey and retval:
            persistent.put(retkey, retval)

def insert(key, value, cache, persistent):
    retkey, retval = cache.insert(key, value)
    if retkey and retval:
        persistent.put(retkey, retval)

def delete(key, cache, persistent):
    elem = cache.delete(key)
    persistent.delete(key)
