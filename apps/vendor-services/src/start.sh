#!/bin/bash

echo -e

echo "Build variables (with default value)"
echo "  - PI_MEETING_DOWNSTREAM_HOSTNAME_AND_PORT=localhost:4001"
echo "  - PI_MEETING_UPSTREAM_PORT=4000"

downstream_hostname_port=${PI_MEETING_DOWNSTREAM_HOSTNAME_AND_PORT-localhost:4001}
upstream_port=${PI_MEETING_UPSTREAM_PORT-4000}

docker build --tag jinja:latest -f jinja.Dockerfile .
docker run --rm \
  -v `pwd`/envoy.yaml.j2:/envoy.yaml.j2 \
  -v `pwd`:/output/ \
  jinja:latest jinja \
    --define downstream_hostname_port $downstream_hostname_port \
    --define upstream_port $upstream_port \
    --output /output/envoy.yaml \
    /envoy.yaml.j2
  
if [ -z "`docker network ls | grep pi-network`" ]; then
  docker network create --subnet 172.10.0.0/16 --gateway 172.10.0.1 pi-network
fi

docker-compose up

