import pickledb

class Persistent:
    def __init__(self, name, db=None):
        self.name = name
        self.db = db if db else pickledb.load(name, False)

    def get(self, key):
        return self.db.get(key)

    def put(self, key, value):
        self.db.set(key, value)
        self.db.dump()

    def insert(self, key, value):
        self.put(key, value)

    def delete(self, key):
        self.db.rem(key)
        self.db.dump()
        
