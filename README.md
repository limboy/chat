a live chat room built with python(flask / gevent / apscheduler) + redis

Basic Architecture
==================

![architecture](http://blog.leezhong.com/image/comet_arch.png)

Screenshot
==========

![chat](http://blog.leezhong.com/image/comet_chat.png)

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
- execute `bin/python scripts/clear_key.py` to clear all data

Changes
=======

0.2
---

* adjust comet strategy
* add admin role
* fix duplicate name

0.1.1
-----

* adjust create room UI / UE
* add rm room func
* improve add chat message's response speed
* bugfixes

0.1
---

* add home page (all rooms in one page, and live content)
* custom nickname
* create room
* coffee-script
* bugfixes

![home](http://blog.leezhong.com/image/comet_home_0.1.png)
![room](http://blog.leezhong.com/image/comet_room_0.1.gif)
