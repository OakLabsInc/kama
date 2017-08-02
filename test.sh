#!/bin/bash

wait_for_mysql() {
	echo -n "Waiting for mysql to start"
	while [ ! $(docker logs mysql 2>&1 | grep 'mysqld: ready for connections' | wc -l) -eq 2 ]; do
		echo -n "."
		sleep 1
	done
	echo "ok"
}

docker build -f Dockerfile.test -t kama-test .

docker create -P --env MYSQL_ROOT_PASSWORD=beer --name mysql mysql:5.7 --character-set-server=utf8mb4
docker start mysql
wait_for_mysql
docker run --rm --link mysql mysql:5.7 /bin/sh -c 'echo "CREATE DATABASE kama CHARACTER SET utf8mb4; GRANT ALL PRIVILEGES ON kama.* TO \"kama\"@\"%\" IDENTIFIED BY \"kama\"; FLUSH PRIVILEGES;" | mysql -u root --password=beer -h $MYSQL_PORT_3306_TCP_ADDR --port=$MYSQL_PORT_3306_TCP_PORT'

docker run --name kama-test --rm -t --link mysql --env MYSQL_SERVICE_PASSWORD=kama kama-test /bin/sh -c 'pip install nose && nosetests -x'

docker stop mysql
docker rm mysql
docker rmi kama-test
