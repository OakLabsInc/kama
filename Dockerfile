FROM alpine:3.6
RUN apk add --no-cache python python-dev openssl-dev py-pip py-mysqldb

WORKDIR /kama
COPY . .
RUN ./build.sh
