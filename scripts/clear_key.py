#coding=utf-8
import redis

rc = redis.Redis()
for item in ['online_*', 'room_*']:
    for key in rc.keys(item):
        print 'deleting %s'%key
        rc.delete(key)
