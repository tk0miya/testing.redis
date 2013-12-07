``testing.redis`` automatically setups a redis instance in a temporary directory, and destroys it after testing

Install
=======
Use easy_install (or pip)::

   $ easy_install testing.redis

And ``testing.redis`` requires Redis server.


Usage
=====
Create Redis instance using ``testing.redis.Redis``::

  import pycassa
  import testing.redis

  # Launch new Redis server
  with testing.redis.Redis as redis:
      conn = pycassa.pool.ConnectionPool('test', redis.server_list())
      #
      # do any tests using Redis...
      #

  # Redis server is terminated here


``testing.redis`` automatically searchs for redis files in ``/usr/local/``.
If you install redis to other directory, set ``redis_home`` keyword::

  # uses a copy of specified data directory of Redis.
  redis = testing.redis.Redis(copy_data_from='/path/to/your/database')


``testing.redis.Redis`` executes ``redis`` on instantiation.
On deleting Redis object, it terminates Redis instance and removes temporary directory.

If you want a database including column families and any fixtures for your apps,
use ``copy_data_from`` keyword::

  # uses a copy of specified data directory of Redis.
  redis = testing.redis.Redis(copy_data_from='/path/to/your/database')


You can specify parameters for Redis with ``redis_yaml`` keyword::

  # boot Redis server listens on 12345 port
  redis = testing.redis.Redis(redis_yaml={'rpc_port': 12345})


For example, you can setup new Redis server for each testcases on setUp() method::

  import unittest
  import testing.redis

  class MyTestCase(unittest.TestCase):
      def setUp(self):
          self.redis = testing.redis.Redis()

      def tearDown(self):
          self.redis.stop()


Requirements
============
* Python 2.6, 2.7
* pycassa
* PyYAML


License
=======
Apache License 2.0


History
=======

1.0.0 (2013-10-17)
-------------------
* First release
