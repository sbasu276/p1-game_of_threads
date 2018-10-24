import threading

class Cache:
    def __init__(self, size):
        """ Initialize the Cache
        """
        self.limit = size # Total size of cache
        self.cache = [] #list of (key, value) tuples
        self.size = 0 # Current size of cache
        self.locks = {} # Dict to store key -> lock 

    def get(self, key):
        """ Get a value from a cache
            key: argument to get
            Returns None if key,value is not in cache
        """
        val = self.__evict(key)
        self._insert(key, val)
        return val

    def put(self, key, value):
        """ Put a value to the cache
            key, value: arguments to put
            Returns True if key existed in cache
        """
        retflag = False
        position = self.__search(key)
        if position:
            k, v = self.cache.pop(position)
            retflag = True
        if self.size < self.limit:
            self.size += 1
        else:
            self.__evict()
        self._insert(key, value)
        return retflag

    def __evict(self, key=None):
        """ Private method to evict a key, value from cache
            Evicts the last element by default (LRU)
        """
        if key:
            val = None
            position = self.__search(key)
            if position:
                key, val = self.cache.pop(position)
        else:
            val = self.cache.pop()
        return val

    def _insert(self, key, value, position=0):
        """ Inserts a value in the given position
            By default inserts at the beginning (LRU)
        """
        self.cache.insert(position, (key, value))

    def __search(self, key):
        """ Search a key in cache
            Return position if found, None otherwise
        """
        if key is None:
            return None
        for i, item in enumerate(self.cache):
            if item[0] == key:
                return i
        return None

class ThreadSafeCache(Cache):
