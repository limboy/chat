#coding=utf-8

import gevent
import redis
import config
import time
import json

rc = redis.Redis()
ps = rc.pubsub()

ps.psubscribe(config.ROOM_ONLINE_USER_SIGNAL.format(room='*'))

def run():
    for item in ps.listen():
        print item
        data = json.loads(item['data'])
        room_id = data['room_id']
        online_users = rc.zrange(config.ROOM_ONLINE_USER_CHANNEL.format(room=room_id), 0, -1)
        rc.set(config.ROOM_ONLINE_USER_KEY.format(room=room_id), json.dumps({
            'data': {room_id: online_users},
            'type': 'room_online_users',
            }))

if __name__ == '__main__':
    run()
