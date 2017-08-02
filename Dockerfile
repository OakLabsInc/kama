FROM alpine:3.6
RUN apk add --no-cache bash python python-dev openssl-dev py-pip py-mysqldb alpine-sdk
RUN pip install pip --upgrade
RUN pip install grpcio==1.4.0
RUN pip install grpcio-tools==1.4.0

WORKDIR /kama
COPY . .
RUN python -m grpc_tools.protoc -Iprotos --python_out=kama --grpc_python_out=kama protos/kama.proto
RUN python setup.py install
