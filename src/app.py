#coding=utf-8

from flask import Flask, request, session, render_template, Response, jsonify, redirect
from gevent.wsgi import WSGIServer
import gevent
import redis
import time
import config
import json

app = Flask(__name__)
app.config.from_object(config)
app.debug = True

rc = redis.Redis()
user_index = 1

channels = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat/<room>')
def chat_room(room):

    if not session.get('user'):
        global user_index
        user_name = session['user'] = 'user_%s'%user_index
        user_index += 1
    else:
        user_name = session['user']

    room_channel = config.ROOM_ONLINE_USER_CHANNEL.format(room=room)
    room_signal = config.ROOM_ONLINE_USER_SIGNAL.format(room=room)

    rc.zadd(config.ONLINE_USER_CHANNEL, user_name, time.time())
    rc.zadd(room_channel, user_name, time.time())
    rc.publish(config.ONLINE_USER_SIGNAL, '')
    rc.publish(room_signal, json.dumps({'room':room}))

    room_content = rc.zrange(config.ROOM_CHANNEL.format(room=room), 0, -1, withscores=True)
    room_content_list = []
    for item in room_content:
        room_content_list.append(json.loads(item[0]))

    online_users = rc.zrange(config.ONLINE_USER_CHANNEL, 0, -1)
    room_online_users = rc.zrange(room_channel, 0, -1)

    return render_template('room.html',
            room_content = room_content_list,
            online_users = online_users,
            uri = request.path,
            room_name = room,
            user_name = user_name,
            room_online_users = room_online_users)

@app.route('/post_content', methods=['POST'])
def post_content():
    room_name = request.form.get('room_name')
    data = {'user': session.get('user'),
            'content': request.form.get('content', ''),
            'created': time.strftime('%H:%M:%S'),
            'room': room_name,
            }
    rc.zadd(config.ROOM_CHANNEL.format(room=room_name), json.dumps(data), time.time())
    rc.publish(config.ROOM_SIGNAL.format(room=room_name), json.dumps({
        'type': 'add_content',
        'content': data,
        }))

    return jsonify(**data)

@app.route('/comet')
def comet():
    global channels
    uri = request.args.get('uri', '')
    room = request.args.get('room', '')
    comet = request.args.get('comet', '').split(',')
    channel = 'channel:%s'%request.args.get('channel')
    channels.setdefault(channel, {})

    # update user stats
    room_channel = config.ROOM_ONLINE_USER_CHANNEL.format(room=room)
    rc.zadd(config.ONLINE_USER_CHANNEL, session['user'], time.time())
    rc.zadd(room_channel, session['user'], time.time())

    comets = []
    if 'online_users' in comet:
        comets.append(config.ONLINE_USER_KEY)
        if config.ONLINE_USER_KEY not in channels[channel]:
            channels[channel][config.ONLINE_USER_KEY] = rc.get(config.ONLINE_USER_KEY)
        channel_val = channels[channel][config.ONLINE_USER_KEY]
        key_val = rc.get(config.ONLINE_USER_KEY)

        if channel_val != key_val:
            channels[channel][config.ONLINE_USER_KEY] = key_val
            return jsonify(json.loads(key_val))

    if 'room_online_users' in comet:
        room_online_user_key = config.ROOM_ONLINE_USER_KEY.format(room=room)
        comets.append(room_online_user_key)
        if room_online_user_key not in channels[channel]:
            channels[channel][room_online_user_key] = rc.get(room_online_user_key)

        channel_val = channels[channel][room_online_user_key]
        key_val = rc.get(room_online_user_key)

        if channel_val != key_val:
            channels[channel][room_online_user_key] = key_val
            return jsonify(json.loads(key_val))

    if 'room_content' in comet:
        room_key = config.ROOM_KEY.format(room=room)
        comets.append(room_key)
        if room_key not in channels[channel]:
            channels[channel][room_key] = rc.get(room_key)

        channel_val = channels[channel][room_key]
        key_val = rc.get(room_key)

        if channel_val != key_val:
            channels[channel][room_key] = key_val
            return jsonify(json.loads(key_val))

        passed_time = 0
        while passed_time < config.COMET_TIMEOUT:
            for key in comets:
                data_str = rc.get(key)
                if data_str:
                    data = json.loads(data_str)
                    if channels[channel][key] != data_str:
                        channels[channel][key] = data_str
                        return jsonify(**data)
            passed_time += config.COMET_POLL_TIME
            gevent.sleep(config.COMET_POLL_TIME)

        return jsonify([])

def run():
    http_server = WSGIServer(('', config.PORT), app)
    http_server.serve_forever()
    #app.run(port=config.PORT)

if __name__ == '__main__':
    run()
