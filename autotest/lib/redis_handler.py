# -*- coding:utf-8 -*-
import redis


class RedisHandler:
    def __init__(self, ip, password, port=6379, db=0):
        try:
            self.r = redis.Redis(host=ip, password=password, port=port, db=db)
        except Exception as e:
            print('redis连接失败，错误信息:%s' % e)

    def str_get(self, k):
        return self.r.get(k)

    def str_set(self, k, v, time=None):
        self.r.set(k, v, time)

    def delete(self, k):
        tag = self.r.exists(k)
        if tag:
            self.r.delete(k)
        else:
            print('这个key不存在')

    def hash_get(self, name, k):
        res = self.r.hget(name, k)
        if res:
            return res.decode()

    def hash_set(self, name, k, v):
        self.r.hset(name, k, v)

    def hash_getall(self, name):
        res = self.r.hgetall(name)
        data = {}
        if res:
            for k, v in res.items():
                k = k.decode()
                v = v.decode()
                data[k] = v
        return data

    def hash_del(self, name, k):
        res = self.r.hdel(name, k)
        if res:
            return 1
        else:
            return 0

    @property
    def clean_redis(self):
        self.r.flushdb()
        return 0


if __name__ == '__main__':
    handler = RedisHandler("10.13.4.34", "")
    ret = handler.str_get()
