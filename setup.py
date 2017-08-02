'''
Kama
Copyright 2017 Oak Labs, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from setuptools import setup

setup(
        name='kama',
        version='1.0.2',
        description='A truth database',
        url='https://kama.sh/',
        author='Jeremy Grosser',
        author_email='jeremy@oaklabs.is',
        license='Apache-2.0',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'License :: OSI Approved :: Apache Software License',
        ],
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
                'kama-server=kama.server:main',
                'kama=kama.client:main',
            ],
        }
)
