a live chat room built with python(flask / gevent / apscheduler) + redis

Basic Architecture
==================

![architecture](http://blog.leezhong.com/image/comet_arch.png)

Screenshot
==========

![architecture](http://blog.leezhong.com/image/comet_chat.png)

Install
=======

- cd /path/to/source
- python bootstrap.py
- bin/buildout
- bin/supervisord
- [optional] bin/supervisorctl
- goto localhost:9527

Tips
====

- users are created automaticly after entering room (user\_1 / user\_2 ...)
- open multi browser to test live communication
