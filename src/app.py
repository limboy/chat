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

def is_admin():
    if session.get('admin'):
        return True
    return False

def is_duplicate_name():
    user_name = session.get('user', '')
    for online_user in rc.zrange(config.ONLINE_USER_CHANNEL, 0, -1):
        if online_user == user_name.encode('utf-8'):
            flash(u'该名(%s)已被抢占，换一个吧'%user_name, 'error')
            session.pop('user', None)
            return True
    return False

@app.route('/adm1n')
def admin():
    session['admin'] = 1
    return redirect('/chat')

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
    session['user'] = user_name
    if is_duplicate_name():
        return redirect('/')
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
        users = rc.zrevrange(config.ROOM_ONLINE_USER_CHANNEL.format(room=room_info['room_id']), 0, -1)
        rm_channel_placeholder(users)
        rooms.append({
            'id': room_info['room_id'],
            'creator': room_info['user'],
            'content': map(json.loads, reversed(rc.zrevrange(config.ROOM_CHANNEL.format(room=room_info['room_id']), 0, 4))),
            'title': room_info['title'],
            'users': users,
            })

    return render_template('chat.html',
            rooms = rooms,
            uri = request.path,
            is_admin = is_admin(),
            )

@app.route('/rm_room', methods=['POST'])
def rm_room():
    if not session.get('user'):
        return redirect('/')

    room_id = request.form.get('room_id')
    room_key = config.ROOM_INFO_KEY.format(room=room_id)
    room_channel = config.ROOM_CHANNEL.format(room=room_id)
    room = json.loads(rc.get(room_key))
    if not is_admin():
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
        if user == config.CHANNEL_PLACEHOLDER:
            continue
        room_online_users.append(user.decode('utf-8'))

    return render_template('room.html',
            room_content = room_content_list,
            uri = request.path,
            room_name = room['title'],
            room_id = room_id,
            room_online_users = room_online_users)

@app.route('/post_content', methods=['POST'])
def post_content():
    if not session.get('user'):
        return redirect('/')

    room_id = request.form.get('room_id')
    data = {'user': session.get('user'),
            'content': linkify(escape_text(request.form.get('content', ''))),
            'created': time.strftime('%m-%d %H:%M:%S'),
            'room_id': room_id,
            'id': rc.incr(config.ROOM_CONTENT_INCR_KEY),
            }
    rc.zadd(config.ROOM_CHANNEL.format(room=room_id), json.dumps(data), time.time())
    return jsonify(**data)

@app.route('/comet')
def comet():
    uri = request.args.get('uri', '')
    room_id = request.args.get('room_id', '')
    comet = request.args.get('comet', '').split(',')
    ts = request.args.get('ts', time.time())
    channel = config.CONN_CHANNEL_SET.format(channel=request.args.get('channel'))

    cmt = Comet()

    result = cmt.check(channel, comet, ts, room_id)
    if result:
        return jsonify(**result)

    passed_time = 0
    while passed_time < config.COMET_TIMEOUT:
        comet = rc.smembers(config.CONN_CHANNEL_SET.format(channel=channel))
        result = cmt.check(channel, comet, ts, room_id)
        if result:
            return jsonify(**result)
        passed_time += config.COMET_POLL_TIME
        gevent.sleep(config.COMET_POLL_TIME)

    if room_id:
        room_online_user_channel = config.ROOM_ONLINE_USER_CHANNEL.format(room=room_id)
        rc.zadd(room_online_user_channel, session['user'], time.time())
    rc.zadd(config.ONLINE_USER_CHANNEL, session['user'], time.time())

    return jsonify(ts=time.time())

def rm_channel_placeholder(data):
    for index, item in enumerate(data):
        if item == config.CHANNEL_PLACEHOLDER:
            data.pop(index)

class Comet(object):
    def check(self, channel, comet, ts, room_id = 0):
        conn_channel_set = config.CONN_CHANNEL_SET.format(channel=channel)
        if 'online_users' in comet:
            rc.sadd(conn_channel_set, 'online_users')
            new_data = rc.zrangebyscore(config.ONLINE_USER_CHANNEL, ts, '+inf')
            if new_data:
                data=rc.zrevrange(config.ONLINE_USER_CHANNEL, 0, -1)
                data.pop(0) if data[0] == config.CHANNEL_PLACEHOLDER else True
                return dict(data=data,
                        ts=time.time(), type='online_users')

        if 'room_online_users' in comet:
            rc.sadd(conn_channel_set, 'room_online_users')
            room_online_user_channel = config.ROOM_ONLINE_USER_CHANNEL.format(room=room_id)
            new_data = rc.zrangebyscore(room_online_user_channel, ts, '+inf')
            if new_data:
                users=rc.zrevrange(room_online_user_channel, 0, -1)
                rm_channel_placeholder(users)
                data = {'room_id': room_id, 'users': users}
                return dict(data=data,
                    ts=time.time(), type='room_online_users')

        if 'room_content' in comet:
            rc.sadd(conn_channel_set, 'room_content')
            room_channel = config.ROOM_CHANNEL.format(room=room_id)
            new_data = rc.zrangebyscore(room_channel, ts, '+inf')
            if new_data:
                data = {'room_id': room_id, 'content':[]}
                for item in new_data:
                    data['content'].append(json.loads(item))
                return dict(data=data, ts=time.time(), type='add_content')

        if 'room_online_users_count_all' in comet:
            rc.sadd(conn_channel_set, 'room_online_users_count_all')
            room_online_user_channels = config.ROOM_ONLINE_USER_CHANNEL.format(room='*')
            for room_online_user_channel in rc.keys(room_online_user_channels):
                new_data = rc.zrangebyscore(room_online_user_channel, ts, '+inf')
                if new_data:
                    users=rc.zrevrange(room_online_user_channel, 0, -1)
                    rm_channel_placeholder(users)
                    room_id = room_online_user_channel.split('_')[-1]
                    data = {'room_id': room_id, 'users': users}
                    return dict(data=data, ts=time.time(), type='room_online_users')

        if 'room_content_all' in comet:
            rc.sadd(conn_channel_set, 'room_content_all')
            room_channels = config.ROOM_CHANNEL.format(room='*')
            for room_channel in rc.keys(room_channels):
                new_data = rc.zrangebyscore(room_channel, ts, '+inf')
                if new_data:
                    room_id = room_channel.split('_')[-1]
                    data = {'room_id': room_id, 'content':[]}
                    for item in new_data:
                        data['content'].append(json.loads(item))
                    return dict(data=data, ts=time.time(), type='add_content')

def run():
    http_server = WSGIServer(('', config.PORT), app)
    http_server.serve_forever()
    #app.run(port=config.PORT)

if __name__ == '__main__':
    run()
