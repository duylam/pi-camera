#!/bin/bash

docker-compose down &>/dev/null || true
docker-compose up -d

echo "Listening ports: "
echo "	- Web-viewer service on 8081"

