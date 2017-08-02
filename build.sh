#!/bin/bash

if [ ! -e wheels ]; then
	docker build -f Dockerfile.build -t kama-build .
	CID=$(docker create kama-build)
	docker cp $CID:/kama/wheels wheels
	docker rm $CID
	docker rmi kama-build
else
	echo "wheels directory already exists, not rebuilding from source"
fi

docker build -f Dockerfile.install -t kama:v1 .
