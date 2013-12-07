# -*- coding: utf-8 -*-

import os
import sys
import signal
import testing.redis
from redis import Redis
from time import sleep

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest


class TestRedisServer(unittest.TestCase):
    def test_basic(self):
        # start redis server
        redis = testing.redis.RedisServer()
        self.assertIsNotNone(redis)
        self.assertEqual(redis.dsn(),
                         dict(host='127.0.0.1', port=redis.port, db=0))

        # connect to redis
        r = Redis(**redis.dsn())
        self.assertIsNotNone(r)

        # shutting down
        pid = redis.pid
        self.assertTrue(pid)
        os.kill(pid, 0)  # process is alive

        redis.stop()
        sleep(1)

        self.assertIsNone(redis.pid)
        with self.assertRaises(OSError):
            os.kill(pid, 0)  # process is down

    def test_stop(self):
        # start redis server
        redis = testing.redis.RedisServer()
        self.assertIsNotNone(redis.pid)
        self.assertTrue(os.path.exists(redis.base_dir))
        pid = redis.pid
        os.kill(pid, 0)  # process is alive

        # call stop()
        redis.stop()
        self.assertIsNone(redis.pid)
        self.assertFalse(os.path.exists(redis.base_dir))
        with self.assertRaises(OSError):
            os.kill(pid, 0)  # process is down

        # call stop() again
        redis.stop()
        self.assertIsNone(redis.pid)
        self.assertFalse(os.path.exists(redis.base_dir))
        with self.assertRaises(OSError):
            os.kill(pid, 0)  # process is down

        # delete redis object after stop()
        del redis

    def test_with_redis(self):
        with testing.redis.RedisServer() as redis:
            self.assertIsNotNone(redis)

            # connect to redis
            r = Redis(**redis.dsn())
            self.assertIsNotNone(r)

            pid = redis.pid
            os.kill(pid, 0)  # process is alive

        self.assertIsNone(redis.pid)
        with self.assertRaises(OSError):
            os.kill(pid, 0)  # process is down

    def test_multiple_redis(self):
        redis1 = testing.redis.RedisServer()
        redis2 = testing.redis.RedisServer()
        self.assertNotEqual(redis1.pid, redis2.pid)

        os.kill(redis1.pid, 0)  # process is alive
        os.kill(redis2.pid, 0)  # process is alive

    def test_redis_is_not_found(self):
        try:
            path = os.environ['PATH']
            os.environ['PATH'] = '/usr/bin'

            with self.assertRaises(RuntimeError):
                testing.redis.RedisServer()
        finally:
            os.environ['PATH'] = path

    def test_fork(self):
        redis = testing.redis.RedisServer()
        if os.fork() == 0:
            del redis
            redis = None
            os.kill(os.getpid(), signal.SIGTERM)  # exit tests FORCELY
        else:
            os.wait()
            sleep(1)
            self.assertTrue(redis.pid)
            os.kill(redis.pid, 0)  # process is alive (delete mysqld obj in child does not effect)

    def test_stop_on_child_process(self):
        redis = testing.redis.RedisServer()
        if os.fork() == 0:
            redis.stop()
            self.assertTrue(redis.pid)
            os.kill(redis.pid, 0)  # process is alive (calling stop() is ignored)
            os.kill(os.getpid(), signal.SIGTERM)  # exit tests FORCELY
        else:
            os.wait()
            sleep(1)
            self.assertTrue(redis.pid)
            os.kill(redis.pid, 0)  # process is alive (calling stop() in child is ignored)

    def test_copy_data_from(self):
        data_dir = os.path.join(os.path.dirname(__file__), 'copy-data-from')
        redis = testing.redis.RedisServer(copy_data_from=data_dir)

        # connect to mysql
        r = Redis(**redis.dsn())

        self.assertEqual('1', r.get('scott'))
        self.assertEqual('2', r.get('tiger'))

    def test_skipIfNotInstalled_found(self):
        @testing.redis.skipIfNotInstalled
        def testcase():
            pass

        self.assertEqual(False, hasattr(testcase, '__unittest_skip__'))
        self.assertEqual(False, hasattr(testcase, '__unittest_skip_why__'))

    def test_skipIfNotInstalled_notfound(self):
        try:
            path = os.environ['PATH']
            os.environ['PATH'] = '/usr/bin'

            @testing.redis.skipIfNotInstalled
            def testcase():
                pass

            self.assertEqual(True, hasattr(testcase, '__unittest_skip__'))
            self.assertEqual(True, hasattr(testcase, '__unittest_skip_why__'))
            self.assertEqual(True, testcase.__unittest_skip__)
            self.assertEqual("redis-server does not found", testcase.__unittest_skip_why__)
        finally:
            os.environ['PATH'] = path

    def test_skipIfNotInstalled_with_args_found(self):
        redis_server = testing.redis.get_path_of('redis-server')

        @testing.redis.skipIfNotInstalled(redis_server)
        def testcase():
            pass

        self.assertEqual(False, hasattr(testcase, '__unittest_skip__'))
        self.assertEqual(False, hasattr(testcase, '__unittest_skip_why__'))

    def test_skipIfNotInstalled_with_args_notfound(self):
        @testing.redis.skipIfNotInstalled("/path/to/anywhere")
        def testcase():
            pass

        self.assertEqual(True, hasattr(testcase, '__unittest_skip__'))
        self.assertEqual(True, hasattr(testcase, '__unittest_skip_why__'))
        self.assertEqual(True, testcase.__unittest_skip__)
        self.assertEqual("redis-server does not found", testcase.__unittest_skip_why__)

    def test_skipIfNotFound_found(self):
        @testing.redis.skipIfNotFound
        def testcase():
            pass

        self.assertEqual(False, hasattr(testcase, '__unittest_skip__'))
        self.assertEqual(False, hasattr(testcase, '__unittest_skip_why__'))

    def test_skipIfNotFound_notfound(self):
        try:
            path = os.environ['PATH']
            os.environ['PATH'] = '/usr/bin'

            @testing.redis.skipIfNotFound
            def testcase():
                pass

            self.assertEqual(True, hasattr(testcase, '__unittest_skip__'))
            self.assertEqual(True, hasattr(testcase, '__unittest_skip_why__'))
            self.assertEqual(True, testcase.__unittest_skip__)
            self.assertEqual("redis-server does not found", testcase.__unittest_skip_why__)
        finally:
            os.environ['PATH'] = path
