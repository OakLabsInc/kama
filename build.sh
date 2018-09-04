#!/bin/bash

if [ ! -e dist ]; then
	docker build -f Dockerfile.build -t kama-build .
	CID=$(docker create kama-build)
	docker cp $CID:/kama/dist dist
	docker rm $CID
	docker rmi kama-build
else
	echo "dist directory already exists, not rebuilding from source"
fi

docker build -f Dockerfile.install -t kama:v1 .
