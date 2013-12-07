# -*- coding: utf-8 -*-
#  Copyright 2013 Takeshi KOMIYA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import absolute_import

import os
import sys
import signal
import socket
import tempfile
import subprocess
from time import sleep
from shutil import copytree
from redis import StrictRedis

__all__ = ['Redis', 'skipIfNotInstalled', 'skipIfNotFound']

DEFAULT_SETTINGS = dict(auto_start=2,
                        base_dir=None,
                        redis_server=None,
                        pid=None,
                        copy_data_from=None)


class Redis(object):
    def __init__(self, **kwargs):
        self.settings = dict(DEFAULT_SETTINGS)
        self.settings.update(kwargs)
        self.pid = None
        self.port = None
        self._owner_pid = os.getpid()
        self._use_tmpdir = False

        if self.base_dir:
            if self.base_dir[0] != '/':
                self.settings['base_dir'] = os.path.join(os.getcwd(), self.base_dir)
        else:
            self.settings['base_dir'] = tempfile.mkdtemp()
            self._use_tmpdir = True

        if self.redis_server is None:
            self.settings['redis_server'] = get_path_of('redis-server')

            if self.redis_server is None:
                raise RuntimeError("command not found: redis-server")

        redis_conf = self.settings.setdefault('redis_conf', {})
        redis_conf['bind'] = '127.0.0.1'
        redis_conf['dir'] = os.path.join(self.base_dir, 'data')
        redis_conf['dbfilename'] = 'dump.rdb'

        if 'port' in redis_conf:
            self.port = redis_conf['port']

        if self.auto_start:
            if os.path.exists(self.pid_file):
                raise RuntimeError('redis is already running (%s)' % self.pid_file)

            if self.auto_start >= 2:
                self.setup()

            self.start()

    def __del__(self):
        self.stop()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stop()

    def __getattr__(self, name):
        if name in self.settings:
            return self.settings[name]
        else:
            raise AttributeError("'Redis' object has no attribute '%s'" % name)

    @property
    def pid_file(self):
        return os.path.join(self.base_dir, 'tmp', 'redis.pid')

    def dsn(self, **kwargs):
        params = dict(kwargs)
        params.setdefault('host', self.redis_conf['bind'])
        params.setdefault('port', self.port)
        params.setdefault('db', 0)

        return params

    def setup(self):
        # copy data files
        if self.copy_data_from:
            try:
                datadir = os.path.join(self.base_dir, 'data')
                copytree(self.copy_data_from, datadir)
            except Exception as exc:
                raise RuntimeError("could not copytree %s to %s: %r" %
                                   (self.copy_data_from, datadir, exc))

        # (re)create directory structure
        for subdir in ['data', 'tmp']:
            try:
                path = os.path.join(self.base_dir, subdir)
                os.makedirs(path)
            except:
                pass

        # write redis.conf
        with open(os.path.join(self.base_dir, 'redis.conf'), 'w') as conf:
            for key, value in self.redis_conf.items():
                conf.write("%s\t%s\n" % (key, value))

    def start(self):
        if self.pid:
            return  # already started

        if 'port' in self.redis_conf:
            self.port = None
        else:
            self.port = get_unused_port()

        logger = open(os.path.join(self.base_dir, 'tmp', 'redis.log'), 'wt')
        pid = os.fork()
        if pid == 0:
            os.dup2(logger.fileno(), sys.__stdout__.fileno())
            os.dup2(logger.fileno(), sys.__stderr__.fileno())

            try:
                with open(self.pid_file, 'wt') as fd:
                    fd.write(str(pid))

                args = [os.path.join(self.base_dir, 'redis.conf')]
                if self.port:
                    args += ['--port', str(self.port)]

                os.execl(self.redis_server, self.redis_server, *args)
            except Exception as exc:
                raise RuntimeError('failed to launch redis: %r' % exc)
        else:
            logger.close()

            while True:
                try:
                    r = StrictRedis(**self.dsn())
                    r.execute_command('QUIT')
                    break
                except:
                    pass

                if os.waitpid(pid, os.WNOHANG) != (0, 0):
                    raise RuntimeError("*** failed to launch redis ***\n" + self.read_log())

                sleep(1)

            self.pid = pid

    def stop(self, _signal=signal.SIGTERM):
        if self._owner_pid == os.getpid():
            self.terminate(_signal)
            self.cleanup()

    def terminate(self, _signal=signal.SIGTERM):
        import os
        if self.pid is None:
            return  # not started

        if self._owner_pid != os.getpid():
            return  # could not stop in child process

        try:
            os.kill(self.pid, _signal)
            while (os.waitpid(self.pid, 0)):
                pass
        except:
            pass

        self.pid = None

        try:
            os.unlink(self.pid_file)
        except:
            pass

    def cleanup(self):
        if self.pid is not None:
            return

        from shutil import rmtree
        if self._use_tmpdir and os.path.exists(self.base_dir):
            rmtree(self.base_dir)

    def read_log(self):
        try:
            with open(os.path.join(self.base_dir, 'tmp', 'redis.log')) as log:
                return log.read()
        except Exception as exc:
            raise RuntimeError("failed to open file:tmp/redis.log: %r" % exc)


def skipIfNotInstalled(arg=None):
    if sys.version_info < (2, 7):
        from unittest2 import skipIf
    else:
        from unittest import skipIf

    def decorator(fn, path=arg):
        if path:
            cond = not os.path.exists(path)
        else:
            if get_path_of('redis-server'):  # found
                cond = False
            else:
                cond = True

        return skipIf(cond, "Redis does not found")(fn)

    if callable(arg):  # execute as simple decorator
        return decorator(arg, None)
    else:  # execute with path argument
        return decorator


skipIfNotFound = skipIfNotInstalled


def get_path_of(name):
    path = subprocess.Popen(['which', name], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
    if path:
        return path.rstrip().decode('utf-8')
    else:
        return None


def get_unused_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    _, port = sock.getsockname()
    sock.close()

    return port
