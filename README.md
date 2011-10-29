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
- make sure redis-server is started
- bin/supervisord
- [optional] bin/supervisorctl
- goto localhost:9527

Tips
====

- open multi browser to test live communication

Changes
=======

0.1
---

* login (custom nickname)
* adjust style
* create room
* coffee-script
