#!/bin/bash

echo -e # stop on command error

downstream_hostname_port=${PI_MEETING_DOWNSTREAM_HOSTNAME_AND_PORT-localhost:4001}
upstream_port=${PI_MEETING_UPSTREAM_PORT-4000}
upstream_hostname=${PI_MEETING_UPSTREAM_HOSTNAME-host.docker.internal}
advertised_ip=${PI_MEETING_ADVERTISED_IP-127.0.0.1}

echo "Support variables (with default value)"
echo "  - PI_MEETING_DOWNSTREAM_HOSTNAME_AND_PORT=$downstream_hostname_port"
echo "  - PI_MEETING_UPSTREAM_PORT=$upstream_port"
echo "  - PI_MEETING_UPSTREAM_HOSTNAME=$upstream_hostname"
echo "  - PI_MEETING_ADVERTISED_IP=$advertised_ip (transfer to --primaryadvertised of stun server)"

docker build --tag jinja:latest -f jinja.Dockerfile .
docker run --rm \
  -v `pwd`/envoy.yaml.j2:/envoy.yaml.j2 \
  -v `pwd`:/output/ \
  jinja:latest jinja \
    --define downstream_hostname_port $downstream_hostname_port \
    --define upstream_port $upstream_port \
    --define upstream_hostname $upstream_hostname \
    --output /output/envoy.yaml \
    /envoy.yaml.j2
  
if [ -z "`docker network ls | grep pi-network`" ]; then
  docker network create --subnet 172.10.0.0/16 pi-network
fi

docker-compose down &>/dev/null || true
PI_MEETING_ADVERTISED_IP=$advertised_ip docker-compose up -d

echo "Listening ports: "
echo "  - STUN service on 3478 (UDP)"
echo "  - GRPC-proxy service on 4001"

