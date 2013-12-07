``testing.redis`` automatically setups a redis instance in a temporary directory, and destroys it after testing

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
  with testing.redis.RedisServer as redis_server:
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
* Python 2.6, 2.7, 3.2, 3.3
* redis


License
=======
Apache License 2.0


History
=======

1.0.0 (2013-12-07)
-------------------
* First release
