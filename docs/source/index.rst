
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

Browser
-------

    const websocket = new WebSocket('ws://0.0.0.0:8000');
    websocket.onmessage = (message) => console.log(message.data)


----

With Other Coroutines
---------------------

    asyncio.get_event_loop().run_until_complete(
        asyncio.gather(
            *([
                websockets.serve(self.server, '0.0.0.0', 8000)
            ] + umuus_aioredis_pubsub.instance.get_coroutines())
        ))
    asyncio.get_event_loop().run_forever()

----

With websockets
---------------

    import asyncio
    import websockets
    import attr
    import umuus_aioredis_pubsub


    @umuus_aioredis_pubsub.instance.subscribe()
    async def my_task(name):
        message = 'Hello, %s.' % name
        await WebSocket.queue.put(message)
        return dict(message=message)


    @attr.s()
    class WebSocket(object):
        queue = asyncio.Queue()
        connections = set()

        async def on_message(self):
            while True:
                if not self.queue.empty():
                    message = await self.queue.get()
                    for connection in self.connections:
                        res = await connection.send(message)
                await asyncio.sleep(0.1)

        async def server(self, websocket, path):
            self.connections.add(websocket)
            while True:
                await asyncio.sleep(0.1)

        def run(self):
            asyncio.get_event_loop().run_until_complete(
                asyncio.gather(
                    *([
                        websockets.serve(self.server, '0.0.0.0', 8012),
                        self.on_message(),
                    ] + umuus_aioredis_pubsub.instance.get_coroutines())
                ))
            asyncio.get_event_loop().run_forever()

    if __name__ == '__main__':
        WebSocket().run()

----

Authors
-------

- Jun Makii <junmakii@gmail.com>

License
-------

GPLv3 <https://www.gnu.org/licenses/>

Table of Contents
-----------------
.. toctree::
   :maxdepth: 2
   :glob:

   *

