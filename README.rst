``testing.redis`` automatically setups a redis instance in a temporary directory, and destroys it after testing

.. image:: https://travis-ci.org/tk0miya/testing.redis.svg?branch=master
   :target: https://travis-ci.org/tk0miya/testing.redis

.. image:: https://coveralls.io/repos/tk0miya/testing.redis/badge.png?branch=master
   :target: https://coveralls.io/r/tk0miya/testing.redis?branch=master

.. image:: https://codeclimate.com/github/tk0miya/testing.redis/badges/gpa.svg
   :target: https://codeclimate.com/github/tk0miya/testing.redis

Install
=======
Use easy_install (or pip)::

   $ easy_install testing.redis

And ``testing.redis`` requires Redis server.


Usage
=====
Create Redis instance using ``testing.redis.RedisServer``::

  import redis
  import testing.redis

  # Launch new Redis server
  with testing.redis.RedisServer() as redis_server:
      r = redis.Redis(**redis_server.dsn())
      #
      # do any tests using Redis...
      #

  # Redis server is terminated here


``testing.redis`` automatically searchs for redis-server from ``$PATH``.
If you install redis to other directory, set ``redis_server`` keyword::

  redis = testing.redis.RedisServer(redis_server='/path/to/your/redis-server')


``testing.redis.RedisServer`` executes ``redis-server`` on instantiation.
On deleting RedisServer object, it terminates Redis instance and removes temporary directory.

If you want a database including any fixtures for your apps,
use ``copy_data_from`` keyword::

  # uses a copy of specified data directory of Redis.
  redis = testing.redis.RedisServer(copy_data_from='/path/to/your/database')


You can specify parameters for Redis with ``redis_conf`` keyword::

  # Enable appendonly mode
  redis = testing.redis.RedisServer(redis_conf={'appendonly': 'yes'})


For example, you can setup new Redis server for each testcases on setUp() method::

  import unittest
  import testing.redis

  class MyTestCase(unittest.TestCase):
      def setUp(self):
          self.redis = testing.redis.RedisServer()

      def tearDown(self):
          self.redis.stop()


Requirements
============
* Python 2.6, 2.7, 3.2, 3.3, 3.4, 3.5
* redis


License
=======
Apache License 2.0


History
=======

1.1.1 (2016-08-20)
-------------------
* Fix a bug

  - #1 Fix parameter handling

1.1.0 (2016-02-03)
-------------------
* Add timeout to server invoker
* Add testing.redis.RedisServerFactory
* Depend on ``testing.common.database`` package

1.0.3 (2015-04-06)
-------------------
* Fix bugs:

  - Do not call os.getpid() on destructor (if not needed)
  - Use absolute path for which command

1.0.2 (2014-06-19)
-------------------
* Add timeout on terminating redis-server
* Fix bugs

1.0.1 (2014-06-11)
-------------------
* Fix ImportError if caught SIGINT on py3

1.0.0 (2013-12-07)
-------------------
* First release
