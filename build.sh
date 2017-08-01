#!/bin/bash

if [ ! -e env ]; then
	virtualenv env
fi
env/bin/pip install pip --upgrade
env/bin/pip install grpcio
env/bin/pip install grpcio-tools
env/bin/python -m grpc_tools.protoc -Iprotos --python_out=kama --grpc_python_out=kama protos/kama.proto
env/bin/python setup.py install
