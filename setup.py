from setuptools import setup

setup(
        name='kama',
        version='1.0',
        packages=['kama'],
        install_requires=[
            'grpcio==1.4.0',
# We don't explicitly depend on MySQL-python because it's only required on the
# server and we don't want to introduce an unnecessary dependency for clients
# importing the library
#           'MySQL-python==1.2.5',
        ],
        entry_points={
            'console_scripts': [
                'kama=kama.server:main',
            ],
        }
)
