from setuptools import setup, find_packages

setup(
    name = 'comet',
    version = '1.0',
    description = 'comet test',
    author = 'lzyy',
    author_email = 'healdream@gmail.com',
    url = 'http://blog.leezhong.com',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = [
        'flask',
        'redis',
        'gevent',
        'apscheduler',
    ],
)

