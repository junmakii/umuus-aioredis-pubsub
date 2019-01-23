#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Jun Makii <junmakii@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""A utility that easy-to-use for Pub/Sub with aoredis of Python.

umuus-aioredis-pubsub
=====================

Installation
------------

    $ pip install git+https://github.com/junmakii/umuus-aioredis-pubsub.git

Example
-------

$ export UMUUS_AIOREDIS_PUBSUB_CONFIG_FILE=/foo/bar/FILE.json

$ cat umuus_aioredis_pubsub.json

{
    "redis": {
	"address": "redis://redis:6379",
	"password": "XXXXXXXXXXXX",
	"db": 0
    }
}

----

``example.py``::

    import umuus_aioredis_pubsub

    @umuus_aioredis_pubsub.instance.subscribe()
    def my_task(name):
        message = 'Hello, %s.' % name
        print('======')
        print(message)
        print('======')
        return dict(message=message)

    umuus_aioredis_pubsub.instance.run()

----

    $ python -m umuus_aioredis_pubsub run --module example

----

    $ redis-cli -u "redis://root:XXXX@redis:6379/0" PUBLISH example:my_task '{"name": "James"}'
    (integer) 2

    ======
    Hello, James.
    ======
    DEBUG example:my_task:on_completed {'message': 'Hello, James.'}
    DEBUG:x, y: None None

----

Dispatching
-----------

    await my_task(name='James')  # Return a normal asyncio coroutine.

    await my_task.dispatch(name='James')  # Push a message into Redis store and wait until return a response.

    await my_task.dispatch(message='James', wait=False)  # Return None, and don't wait a response.

    await my_task.dispatch(message='James', wait=False)

    await umuus_aioredis_pubsub.instance.dispatch('example:my_task', name='James')  # Send a messagee into Redis store by a string.


----

With Custom Pattern
-------------------

    import umuus_aioredis_pubsub

    @umuus_aioredis_pubsub.instance.subscribe(pattern='MY_TASK')
    def my_task(name):
        ...

----

    $ redis-cli -u "redis://root:XXXX@redis:6379/0" PUBLISH MY_TASK '{"name": "James"}'

----

Authors
-------

- Jun Makii <junmakii@gmail.com>

License
-------

GPLv3 <https://www.gnu.org/licenses/>

"""
import os
import sys
import aioredis
# from aioredis.pubsub import Receiver
import asyncio
import fire
import attr
import functools
import types
import toolz
import json
import inspect
import addict
import logging
logger = logging.getLogger(__name__)
(__name__ == '__main__' and logging.basicConfig(
    level=os.environ.get(__name__.upper().replace('.', '__') + '_LOG_LEVEL',
                         'WARNING'),
    stream=sys.stdout))
(__name__ == '__main__' and logger.setLevel(
    os.environ.get(__name__.upper().replace('.', '__') + '_LOGLEVEL',
                   'DEBUG')))
logging.basicConfig(level='DEBUG')
__version__ = '0.1'
__url__ = 'https://github.com/junmakii/umuus-aioredis-pubsub'
__author__ = 'Jun Makii'
__author_email__ = 'junmakii@gmail.com'
__author_username__ = 'junmakii'
__keywords__ = []
__license__ = 'GPLv3'
__scripts__ = []
__install_requires__ = [
    'attrs==18.2.0',
    'addict==2.2.0',
    'fire==0.1.3',
    'aioredis==1.2.0',
    'toolz==0.9.0',
]
__dependency_links__ = []
__classifiers__ = []
__entry_points__ = {
    'console_scripts': ['umuus_aioredis_pubsub = umuus_aioredis_pubsub:main'],
    'gui_scripts': [],
}
__project_urls__ = {}
__setup_requires__ = []
__test_suite__ = ''
__tests_require__ = []
__extras_require__ = {}
__package_data__ = {}
__python_requires__ = ''
__include_package_data__ = True
__zip_safe__ = True
__static_files__ = {}
__extra_options__ = {}
__download_url__ = ''
__all__ = []


@attr.s()
class AsyncCorotine(object):
    fn = attr.ib(None, converter=lambda _: error_handler_decorator(_))
    pattern = attr.ib(None)
    ignore_result = attr.ib(False)
    result_event_name = attr.ib(None)
    redis = attr.ib(None)

    def __attrs_post_init__(self):
        self.pattern = self.pattern or self.fn.__module__ + ':' + self.fn.__name__
        self.result_event_name = self.pattern + ':on_completed'
        self.error_event_name = self.pattern + ':on_error'
        self.spec = inspect.getfullargspec(self.fn)
        logging.info(dict(pattern=self.pattern))

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)

    async def dispatch(self, **kwargs):
        return await self.redis.dispatch(self.pattern, **kwargs)

    async def get_coroutine(self):
        while not self.redis.is_connected:
            await asyncio.sleep(0.1)

        while True:
            for channel in await self.redis.redis.psubscribe(
                    self.pattern):  # type: aioredis.pubsub.Channel
                while await channel.wait_message():  # type: bool
                    channel_name, receive_data = await channel.get_json(
                        encoding=self.redis.encoding
                    )  # (b'my_channel', b'my_data') <class 'tuple'>
                    channel_name = channel_name.decode(self.redis.encoding)
                    data = (isinstance(receive_data, dict) and
                            (dict(dict(type='', payload={}), **receive_data))
                            or dict(type='', payload=receive_data))
                    payload = data.get('payload')
                    receive_data.get('type', '')
                    if channel_name != self.result_event_name:
                        kw = ({
                            key: value
                            for key, value in (
                                    []
                                    + (
                                        isinstance(payload, dict)
                                        and list(payload.items())
                                        or []
                                    )
                                    + list(receive_data.items())
                                    + list(data.items())
                                    + list(dict(
                                        dispatch=lambda name, **kwargs: self.redis.subscribe.publish_json(name, dict(type=name, payload=kwargs)),
                                    ).items())
                            )
                        })
                        result = self.fn(**kw)
                        if isinstance(result, types.CoroutineType):
                            result = await result
                        if isinstance(result, Exception):
                            response = dict(
                                type=self.error_event_name,
                                error=str(result),
                            )
                        else:
                            response = dict(
                                type=self.result_event_name, payload=result)
                        if self.pattern != '*' or not self.ignore_result:
                            await self.redis.subscribe.publish_json(
                                self.result_event_name, response)
            await asyncio.sleep(1)


@attr.s()
class AsyncRedisPubSub(object):
    name = attr.ib(__name__)
    options = attr.ib({}, converter=lambda _: addict.Dict(
        _,
        dict(redis=dict(
            address='',
            password='',
            db=0,
        )),
    ))
    encoding = attr.ib(sys.getdefaultencoding())
    is_connected = attr.ib(False)
    coroutines = []

    def __attrs_post_init__(self):
        logger.info(__name__.replace('.', '__').upper() + '_CONFIG_FILE')
        logger.info(self.name.replace('.', '__').upper() + '_CONFIG_FILE')
        logger.info(self.name.replace('.', '__') + '.json')
        logger.info(__name__.replace('.', '__') + '.json')
        self.options.update(
            functools.reduce(
                lambda acc, _: (acc.update(json.load(open(_))), acc)[-1],
                filter(lambda _: _ and os.path.exists(_), [
                    os.environ.get(
                        __name__.replace('.', '__').upper() + '_CONFIG_FILE'),
                    os.environ.get(
                        self.name.replace('.', '__').upper() + '_CONFIG_FILE'),
                    self.name.replace('.', '__') + '.json',
                    __name__.replace('.', '__') + '.json',
                ]), addict.Dict()))

    async def connect(self):
        self.redis = await aioredis.create_redis(
            self.options.redis.address,
            db=self.options.redis.db,
            password=self.options.redis.password,
        )
        self.subscribe = await aioredis.create_redis(
            self.options.redis.address,
            password=self.options.redis.password,
        )
        self.is_connected = True

    async def on_error(self, err):
        raise err

    async def dispatch(self, pattern, wait=True, **kwargs):
        await self.subscribe.publish_json(pattern,
                                          dict(type=pattern, payload=kwargs))
        if wait:
            for channel in await self.redis.psubscribe(pattern +
                                                       ':on_completed'):
                channel_name, receive_data = await channel.get_json(
                    encoding=self.encoding
                )  # (b'my_channel', b'my_data') <class 'tuple'>
                channel_name = channel_name.decode(self.encoding)
                return receive_data.get('payload')

    @toolz.curry
    def add_callback(self, fn, callback, **kwargs):
        return self.subscribe(
            fn=callback, pattern=fn.result_event_name, **kwargs)

    @toolz.curry
    def subscribe(self, fn, **kwargs):
        coroutine = AsyncCorotine(
            redis=self, fn=fn, **{k: v
                                  for k, v in kwargs.items()})
        self.coroutines.append(coroutine)
        return coroutine

    def unsubscribe(self, coroutine):
        self.coroutines.remove(coroutine)
        return self

    def run(self):
        self.loop = asyncio.get_event_loop()
        try:
            self.loop.run_until_complete(
                asyncio.gather(*(
                    [self.connect()] + [_ for _ in self.get_coroutines()])))
        except KeyboardInterrupt:
            pass
        finally:
            self.loop.close()

    def get_coroutines(self):
        return [_.get_coroutine() for _ in self.coroutines]


instance = AsyncRedisPubSub(
    name=os.path.splitext(os.path.basename(__file__))[0])


@toolz.curry
def error_handler_decorator(fn, exc=Exception):
    spec = inspect.getfullargspec(fn)

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(
                *args, **{
                    key: value
                    for key, value in kwargs.items()
                    if key in spec.args or spec.varkw
                })
        except exc as err:
            return err

    return wrapper


def run(module=''):
    module = __import__(module)
    module.umuus_aioredis_pubsub.instance.run()


def main(argv=[]):
    fire.Fire()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
