from apscheduler.scheduler import Scheduler
import signal
import redis
import config
import time
import json

rc = redis.Redis()

sched = Scheduler()
sched.start()

def clear():
    print 'clearing'
    current_time = time.time()
    affcted_num = rc.zremrangebyscore(config.ONLINE_USER_CHANNEL, '-inf', current_time - 60)
    print 'affcted_num:%s'%affcted_num
    if affcted_num:
        rc.publish(config.ONLINE_USER_SIGNAL, '')

    # cause channel == signal, so publish channel is ok
    for key in rc.keys(config.ROOM_ONLINE_USER_CHANNEL.format(room='*')):
        affcted_num = rc.zremrangebyscore(key, '-inf', current_time - 60)
        room = key.split('_')[-1]
        if affcted_num:
            rc.publish(key, json.dumps({'room': room}))

sched.add_cron_job(clear,  minute='*')

signal.pause()
