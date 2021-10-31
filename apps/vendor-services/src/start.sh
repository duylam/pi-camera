#!/bin/bash

echo -e # stop on command error

downstream_hostname_port=${PI_CAMERA_DOWNSTREAM_HOSTNAME_AND_PORT-localhost:4001}
upstream_port=${PI_CAMERA_UPSTREAM_PORT-4000}
upstream_hostname=${PI_CAMERA_UPSTREAM_HOSTNAME-host.docker.internal}
advertised_ip=$PI_CAMERA_ADVERTISED_IP
docker_compose_up_opt="${PI_CAMERA_DOCKER_COMPOSE_UP_OPT--d}"

echo "Support variables (with default value)"
echo "  - PI_CAMERA_DOWNSTREAM_HOSTNAME_AND_PORT=$downstream_hostname_port"
echo "  - PI_CAMERA_UPSTREAM_PORT=$upstream_port"
echo "  - PI_CAMERA_UPSTREAM_HOSTNAME=$upstream_hostname"
echo "  - PI_CAMERA_ADVERTISED_IP=$advertised_ip (use built-in script 'detect-external-ip' if empty)"

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

if [ -z "$advertised_ip" ]; then
  advertised_ip='$(detect-external-ip)'
fi

PI_CAMERA_ADVERTISED_IP=$advertised_ip docker-compose up $docker_compose_up_opt

echo "Listening ports: "
echo "  - STUN service on 3478 (UDP)"
echo "  - GRPC-proxy service on 4001"

