#coding=utf-8

DEBUG = True
PORT = 9527
SECRET_KEY = 'i have a dream'
SESSION_COOKIE_HTTPONLY = False

CHAT_NAME = u'谈天说地老天荒'

ONLINE_USER_CHANNEL = 'online_user_channel'
ROOM_ONLINE_USER_CHANNEL = 'room_online_user_channel_{room}'
ROOM_CHANNEL = 'room_channel_{room}'

ROOM_INCR_KEY = 'room_incr_key'
ROOM_CONTENT_INCR_KEY = 'room_content_incr_key'
ROOM_INFO_KEY = 'room_info_key_{room}'

ONLINE_USER_SIGNAL = ONLINE_USER_CHANNEL
ROOM_ONLINE_USER_SIGNAL = ROOM_ONLINE_USER_CHANNEL
ROOM_SIGNAL = ROOM_CHANNEL

CONN_CHANNEL_SET = 'conn_channel_set_{channel}'

COMET_TIMEOUT = 30
COMET_POLL_TIME = 2

CHANNEL_PLACEHOLDER = 'jwdlh'
