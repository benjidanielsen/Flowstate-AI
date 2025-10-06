import redis
import json

class RedisCache:
    def __init__(self, host='localhost', port=6379, db=0, default_expire=300):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.default_expire = default_expire

    def get(self, key):
        value = self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    def set(self, key, value, expire=None):
        if expire is None:
            expire = self.default_expire
        if not isinstance(value, str):
            value = json.dumps(value)
        self.client.set(name=key, value=value, ex=expire)

    def delete(self, key):
        self.client.delete(key)

    def clear(self):
        self.client.flushdb()
