from setuptools import setup

setup(
        name='kama',
        version='1.0',
        packages=['kama'],
        install_requires=[
            'grpcio==1.4.0',
#           'MySQL-python==1.2.5',
        ],
        entry_points={
            'console_scripts': [
                'kama=kama.server:main',
            ],
        }
)
