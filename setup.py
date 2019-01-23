
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def run_tests(self):
        import sys
        import shlex
        import pytest
        errno = pytest.main(['--doctest-modules'])
        if errno != 0:
            raise Exception('An error occured during installution.')
        install.run(self)


setup(
    packages=setuptools.find_packages('.'),
    version='0.1',
    url='https://github.com/junmakii/umuus-aioredis-pubsub',
    author='Jun Makii',
    author_email='junmakii@gmail.com',
    keywords=[],
    license='GPLv3',
    scripts=[],
    install_requires=['attrs==18.2.0',
 'addict==2.2.0',
 'fire==0.1.3',
 'aioredis==1.2.0',
 'toolz==0.9.0'],
    dependency_links=[],
    classifiers=[],
    entry_points={'console_scripts': ['umuus_aioredis_pubsub = umuus_aioredis_pubsub:main'],
 'gui_scripts': []},
    project_urls={},
    setup_requires=[],
    test_suite='',
    tests_require=[],
    extras_require={},
    package_data={},
    python_requires='',
    include_package_data=True,
    zip_safe=True,
    name='umuus-aioredis-pubsub',
    description='A utility that easy-to-use for Pub/Sub with aoredis of Python.',
    long_description=('A utility that easy-to-use for Pub/Sub with aoredis of Python.\n'
 '\n'
 'umuus-aioredis-pubsub\n'
 '=====================\n'
 '\n'
 'Installation\n'
 '------------\n'
 '\n'
 '    $ pip install git+https://github.com/junmakii/umuus-aioredis-pubsub.git\n'
 '\n'
 'Example\n'
 '-------\n'
 '\n'
 '$ export UMUUS_AIOREDIS_PUBSUB_CONFIG_FILE=/foo/bar/FILE.json\n'
 '\n'
 '$ cat umuus_aioredis_pubsub.json\n'
 '\n'
 '{\n'
 '    "redis": {\n'
 '        "address": "redis://redis:6379",\n'
 '        "password": "XXXXXXXXXXXX",\n'
 '        "db": 0\n'
 '    }\n'
 '}\n'
 '\n'
 '----\n'
 '\n'
 '``example.py``::\n'
 '\n'
 '    import umuus_aioredis_pubsub\n'
 '\n'
 '    @umuus_aioredis_pubsub.instance.subscribe()\n'
 '    def my_task(name):\n'
 "        message = 'Hello, %s.' % name\n"
 "        print('======')\n"
 '        print(message)\n'
 "        print('======')\n"
 '        return dict(message=message)\n'
 '\n'
 '    umuus_aioredis_pubsub.instance.run()\n'
 '\n'
 '----\n'
 '\n'
 '    $ python -m umuus_aioredis_pubsub run --module example\n'
 '\n'
 '----\n'
 '\n'
 '    $ redis-cli -u "redis://root:XXXX@redis:6379/0" PUBLISH example:my_task '
 '\'{"name": "James"}\'\n'
 '    (integer) 2\n'
 '\n'
 '    ======\n'
 '    Hello, James.\n'
 '    ======\n'
 "    DEBUG example:my_task:on_completed {'message': 'Hello, James.'}\n"
 '    DEBUG:x, y: None None\n'
 '\n'
 '----\n'
 '\n'
 'Dispatching\n'
 '-----------\n'
 '\n'
 "    await my_task(name='James')  # Return a normal asyncio coroutine.\n"
 '\n'
 "    await my_task.dispatch(name='James')  # Push a message into Redis store "
 'and wait until return a response.\n'
 '\n'
 "    await my_task.dispatch(message='James', wait=False)  # Return None, and "
 "don't wait a response.\n"
 '\n'
 "    await my_task.dispatch(message='James', wait=False)\n"
 '\n'
 "    await umuus_aioredis_pubsub.instance.dispatch('example:my_task', "
 "name='James')  # Send a messagee into Redis store by a string.\n"
 '\n'
 '\n'
 '----\n'
 '\n'
 'With Custom Pattern\n'
 '-------------------\n'
 '\n'
 '    import umuus_aioredis_pubsub\n'
 '\n'
 "    @umuus_aioredis_pubsub.instance.subscribe(pattern='MY_TASK')\n"
 '    def my_task(name):\n'
 '        ...\n'
 '\n'
 '----\n'
 '\n'
 '    $ redis-cli -u "redis://root:XXXX@redis:6379/0" PUBLISH MY_TASK '
 '\'{"name": "James"}\'\n'
 '\n'
 '----\n'
 '\n'
 'Authors\n'
 '-------\n'
 '\n'
 '- Jun Makii <junmakii@gmail.com>\n'
 '\n'
 'License\n'
 '-------\n'
 '\n'
 'GPLv3 <https://www.gnu.org/licenses/>'),
    cmdclass={"pytest": PyTest},
)
