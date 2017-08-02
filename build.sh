#!/bin/bash

pip install pip --upgrade
pip install grpcio==1.4.0
pip install grpcio-tools==1.4.0
python -m grpc_tools.protoc -Iprotos --python_out=kama --grpc_python_out=kama protos/kama.proto
python setup.py install
