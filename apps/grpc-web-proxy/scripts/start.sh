#!/bin/bash

set -e

bash scripts/build.sh

cd build

echo '===== GRPC Web will listen on 4001 and proxies to 4000'
sleep 2
docker-compose up

