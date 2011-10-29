#coding=utf-8

import gevent
import redis
import config
import time
import json

rc = redis.Redis()
ps = rc.pubsub()

ps.subscribe(config.ONLINE_USER_SIGNAL)

def run():
    for item in ps.listen():
        online_users = rc.zrange(config.ONLINE_USER_CHANNEL, 0, -1)
        rc.set(config.ONLINE_USER_KEY, json.dumps({
            "data": online_users,
            'type': 'online_users',
            }))

if __name__ == '__main__':
    run()
