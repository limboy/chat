#coding=utf-8

import gevent
import redis
import config
import time
import json

rc = redis.Redis()
ps = rc.pubsub()

ps.psubscribe(config.ROOM_SIGNAL.format(room='*'))

def run():
    for item in ps.listen():
        data = json.loads(item['data'])
        print data
        rc.set(config.ROOM_KEY.format(room=data['data']['room_id']), json.dumps(data))

if __name__ == '__main__':
    run()
