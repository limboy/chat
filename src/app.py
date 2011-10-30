#coding=utf-8

from flask import Flask, request, session, render_template, Response, jsonify, redirect, flash
from gevent.wsgi import WSGIServer
from utils.text import linkify, escape_text
import gevent
import redis
import time
import config
import json

app = Flask(__name__)
app.config.from_object(config)
app.debug = True

rc = redis.Redis()

def is_duplicate_name():
    user_name = session.get('user', '')
    for online_user in rc.zrange(config.ONLINE_USER_CHANNEL, 0, -1):
        if online_user == user_name:
            flash(u'该名(%s)已被抢占，换一个吧'%user_name, 'error')
            return True
    return False

@app.route('/')
def index():
    if session.get('user'):
        return redirect('/chat')
    return render_template('index.html')

@app.route('/change_name')
def change_name():
    session.pop('user', None)
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    user_name = request.form.get('user_name', '')
    if is_duplicate_name():
        return redirect('/')
    session['user'] = escape_text(user_name)
    return redirect('/chat')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if not session.get('user'):
        return redirect('/')

    if request.method == 'POST':
        title = request.form.get('title', '')
        if not title:
            return jsonify(status='error', message={'title': 'empty title'})

        room_id = rc.incr(config.ROOM_INCR_KEY)
        rc.set(config.ROOM_INFO_KEY.format(room=room_id),
                json.dumps({'title': title,
                    'room_id': room_id,
                    'user': session['user'],
                    'created': time.time()
                    }))
        return redirect('/chat')

    rooms = []
    room_info_keys = config.ROOM_INFO_KEY.format(room='*')
    for room_info_key in rc.keys(room_info_keys):
        room_info = json.loads(rc.get(room_info_key))
        rooms.append({
            'id': room_info['room_id'],
            'creator': room_info['user'],
            'content': map(json.loads, reversed(rc.zrevrange(config.ROOM_CHANNEL.format(room=room_info['room_id']), 0, 4))),
            'title': room_info['title'],
            'users': rc.zrange(config.ROOM_ONLINE_USER_CHANNEL.format(room=room_info['room_id']), 0, -1),
            })

    return render_template('chat.html',
            rooms = rooms,
            uri = request.path,
            )

@app.route('/rm_room', methods=['POST'])
def rm_room():
    if not session.get('user'):
        return redirect('/')

    room_id = request.form.get('room_id')
    room_key = config.ROOM_INFO_KEY.format(room=room_id)
    room_channel = config.ROOM_CHANNEL.format(room=room_id)
    room = json.loads(rc.get(room_key))
    if room['user'] != session.get('user'):
        return jsonify(status='error', content={'message': 'permission denied'})

    rc.delete(room_key)
    rc.delete(room_channel)
    return jsonify(status='ok', content={'url': '/chat'})

@app.route('/chat/<int:room_id>')
def chat_room(room_id):
    if not session.get('user'):
        return redirect('/')

    user_name = session['user']
    room = json.loads(rc.get(config.ROOM_INFO_KEY.format(room=room_id)))
    room_online_user_channel = config.ROOM_ONLINE_USER_CHANNEL.format(room=room_id)
    room_online_user_signal = config.ROOM_ONLINE_USER_SIGNAL.format(room=room_id)

    rc.zadd(config.ONLINE_USER_CHANNEL, user_name, time.time())
    rc.zadd(room_online_user_channel, user_name, time.time())
    rc.publish(config.ONLINE_USER_SIGNAL, '')
    rc.publish(room_online_user_signal, json.dumps({'room_id':room_id}))

    room_content = reversed(rc.zrevrange(config.ROOM_CHANNEL.format(room=room_id), 0, 200, withscores=True))
    room_content_list = []
    for item in room_content:
        room_content_list.append(json.loads(item[0]))

    room_online_users =[]
    for user in rc.zrange(room_online_user_channel, 0, -1):
        room_online_users.append(user.decode('utf-8'))

    return render_template('room.html',
            room_content = room_content_list,
            uri = request.path,
            room_name = room['title'],
            room_id = room_id,
            room_online_users = room_online_users)

@app.route('/post_content', methods=['POST'])
def post_content():
    room_id = request.form.get('room_id')
    data = {'user': session.get('user'),
            'content': linkify(escape_text(request.form.get('content', ''))),
            'created': time.strftime('%m-%d %H:%M:%S'),
            'room_id': room_id,
            'id': rc.incr(config.ROOM_CONTENT_INCR_KEY),
            }
    rc.zadd(config.ROOM_CHANNEL.format(room=room_id), json.dumps(data), time.time())
    rc.publish(config.ROOM_SIGNAL.format(room=room_id), json.dumps({
        'type': 'add_content',
        'data': data,
        }))

    return jsonify(**data)

@app.route('/comet')
def comet():
    uri = request.args.get('uri', '')
    room_id = request.args.get('room_id', '')
    comet = request.args.get('comet', '').split(',')
    channel = config.CONN_CHANNEL_HASH.format(channel=request.args.get('channel'))

    if room_id:
        room_online_user_channel = config.ROOM_ONLINE_USER_CHANNEL.format(room=room_id)
        rc.zadd(room_online_user_channel, session['user'], time.time())
    rc.zadd(config.ONLINE_USER_CHANNEL, session['user'], time.time())

    if 'online_users' in comet:
        if config.ONLINE_USER_KEY not in rc.hgetall(channel):
            rc.hset(channel, config.ONLINE_USER_KEY, rc.get(config.ONLINE_USER_KEY))
        channel_val = rc.hget(channel, config.ONLINE_USER_KEY)
        key_val = rc.get(config.ONLINE_USER_KEY)

        if channel_val != key_val:
            rc.hset(channel, config.ONLINE_USER_KEY, key_val)
            if key_val:
                return jsonify(json.loads(key_val))

    if 'room_online_users' in comet:
        room_online_user_key = config.ROOM_ONLINE_USER_KEY.format(room=room_id)
        if room_online_user_key not in rc.hgetall(channel):
            rc.hset(channel, room_online_user_key, rc.get(room_online_user_key))

        channel_val = rc.hget(channel, room_online_user_key)
        key_val = rc.get(room_online_user_key)

        if channel_val != key_val:
            rc.hset(channel, room_online_user_key, key_val)
            if key_val:
                return jsonify(json.loads(key_val))

    if 'room_content' in comet:
        room_key = config.ROOM_KEY.format(room=room_id)
        if room_key not in rc.hgetall(channel):
            rc.hset(channel, room_key, rc.get(room_key))

        channel_val = rc.hget(channel, room_key)
        key_val = rc.get(room_key)

        if channel_val != key_val:
            rc.hset(channel, room_key, key_val)
            if key_val:
                return jsonify(json.loads(key_val))

    if 'room_online_users_count_all' in comet:
        room_online_user_keys = config.ROOM_ONLINE_USER_KEY.format(room='*')
        for user_key in rc.keys(room_online_user_keys):
            if user_key not in rc.hgetall(channel):
                rc.hset(channel, user_key, rc.get(user_key))

            channel_val = rc.hget(channel, user_key)
            key_val = rc.get(user_key)

            if channel_val != key_val:
                rc.hset(channel, user_key, key_val)
                if key_val:
                    return jsonify(json.loads(key_val))

    if 'room_content_all' in comet:
        max_room_id = rc.get(config.ROOM_INCR_KEY)
        if max_room_id:
            room_keys = [config.ROOM_KEY.format(room=tmp_room_id) for tmp_room_id in range(1, int(max_room_id)+1)]
            for room_key in room_keys:
                if room_key not in rc.hgetall(channel):
                    rc.hset(channel, room_key, rc.get(room_key))

                channel_val = rc.hget(channel, room_key)
                key_val = rc.get(room_key)

                if channel_val != key_val:
                    rc.hset(channel, room_key, key_val)
                    if key_val:
                        return jsonify(json.loads(key_val))

    passed_time = 0
    while passed_time < config.COMET_TIMEOUT:
        for key, val in rc.hgetall(channel).items():
            current_val = rc.get(key)
            if current_val and val != current_val:
                data = json.loads(current_val)
                rc.hset(channel, key, current_val)
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
