from redis import Redis


class CustomRedis:
    database: Redis
    
    def __init__(self, database: Redis):
        self.database = database

    def get(self, key):
        return self.database.get(key)
    
    def set(self, key, value):
        return self.database.set(key, value)

    def list_get(self, list_name):
        length = self.database.llen(list_name)
        return self.database.lrange(list_name, 0, length)
    
    def list_rem(self, list_name, value):
        self.database.lrem(list_name, 0, value)
    
    def list_push(self, list_name, value):
        self.database.lpush(list_name, value)
        
    def list_pop(self, list_name):
        self.database.lpop(list_name, 1)

    def delete(self, key):
        return self.database.delete(key)
    
    def dropDatabase(self):
        self.database.flushall()
        
    def allKeys(self):
        return self.database.keys('*')