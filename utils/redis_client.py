import redis
from django.conf import settings


class RedisClient:
    conn = None

    @classmethod
    def get_connection(cls):
        # use the singleton mode, create the connection globally
        if cls.conn:
            return cls.conn
        cls.conn = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
        )
        return cls.conn

    @classmethod
    def clear(cls):
        # clear all keys in redis, for testing purpose
        if not settings.TESTING_MODE:
            raise Exception("You can NOT flush redis in Prod environment...")
        conn = cls.get_connection()
        conn.flushdb()
