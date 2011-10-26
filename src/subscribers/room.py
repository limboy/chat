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
        print item
        data = json.loads(item['data'])
        rc.set(config.ROOM_KEY.format(room=data['content']['room']), json.dumps(data))

if __name__ == '__main__':
    run()
