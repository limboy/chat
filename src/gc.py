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
    current_time = time.time()
    affcted_num = rc.zremrangebyscore(config.ONLINE_USER_CHANNEL, '-inf', current_time - 60)
    if affcted_num:
        rc.zadd(config.ONLINE_USER_CHANNEL, config.CHANNEL_PLACEHOLDER, time.time())

    for key in rc.keys(config.ROOM_ONLINE_USER_CHANNEL.format(room='*')):
        affcted_num = rc.zremrangebyscore(key, '-inf', current_time - 60)
        if affcted_num:
            rc.zadd(key, config.CHANNEL_PLACEHOLDER, time.time())

sched.add_cron_job(clear,  minute='*')

signal.pause()
