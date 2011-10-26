a live chat room built with python(flask / gevent / apscheduler) + redis

Basic Architecture
==================

![architecture](http://blog.leezhong.com/image/comet_arch.png)

Screenshot
==========

![architecture](http://blog.leezhong.com/image/comet_chat.png)

Install
=======

0) cd /path/to/source
1) python bootstrap.py
2) bin/buildout
3) bin/supervisord
4) [optional] bin/supervisorctl
5) goto localhost:9527

Tips
====

1) users are created automaticly after entering room (user\_1 / user\_2 ...)
2) open multi browser to test live communication
