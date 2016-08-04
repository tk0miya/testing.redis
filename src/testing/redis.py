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
from redis import Redis

from testing.common.database import (
    Database, DatabaseFactory, SkipIfNotInstalledDecorator, get_path_of
)

__all__ = ['Redis', 'skipIfNotInstalled', 'skipIfNotFound']


class RedisServer(Database):
    DEFAULT_SETTINGS = dict(auto_start=2,
                            base_dir=None,
                            redis_server=None,
                            pid=None,
                            port=None,
                            copy_data_from=None)
    subdirectories = ['data', 'tmp']

    def initialize(self):
        self.redis_server = self.settings.get('redis_server')
        if self.redis_server is None:
            self.redis_server = get_path_of('redis-server')

            if self.redis_server is None:
                raise RuntimeError("command not found: redis-server")

        self.redis_conf = self.settings.get('redis_conf', {})
        self.redis_conf['bind'] = '127.0.0.1'
        self.redis_conf['dir'] = os.path.join(self.base_dir, 'data')
        self.redis_conf['dbfilename'] = 'dump.rdb'

    def dsn(self, **kwargs):
        params = dict(kwargs)
        params.setdefault('host', self.redis_conf['bind'])
        params.setdefault('port', self.redis_conf['port'])
        params.setdefault('db', 0)

        return params

    def get_data_directory(self):
        return os.path.join(self.base_dir, 'data')

    def prestart(self):
        super(RedisServer, self).prestart()
        if 'port' not in self.redis_conf:
            self.redis_conf['port'] = self.settings['port']

        # write redis.conf
        with open(os.path.join(self.base_dir, 'redis.conf'), 'w') as conf:
            for key, value in self.redis_conf.items():
                conf.write("%s\t%s\n" % (key, value))

    def get_server_commandline(self):
        return [self.redis_server,
                os.path.join(self.base_dir, 'redis.conf')]

    def is_server_available(self):
        try:
            r = Redis(**self.dsn())
            r.execute_command('QUIT')
            return True
        except:
            return False


class RedisServerFactory(DatabaseFactory):
    target_class = RedisServer


class RedisServerSkipIfNotInstalledDecorator(SkipIfNotInstalledDecorator):
    name = 'redis-server'

    def search_server(self):
        if not get_path_of('redis-server'):
            raise RuntimeError()


skipIfNotFound = skipIfNotInstalled = RedisServerSkipIfNotInstalledDecorator()
