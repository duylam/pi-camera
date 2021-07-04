#!/bin/bash

echo -e

echo "Build variables (with default value)"
echo "  - PI_MEETING_DOWNSTREAM_HOSTNAME_AND_PORT=localhost:4001"
echo "  - PI_MEETING_UPSTREAM_HOSTNAME=host.docker.internal"
echo "  - PI_MEETING_UPSTREAM_PORT=4000"

downstream_hostname_port=${PI_MEETING_DOWNSTREAM_HOSTNAME_AND_PORT-localhost:4001}
upstream_hostname=${PI_MEETING_UPSTREAM_HOSTNAME-host.docker.internal}
upstream_port=${PI_MEETING_UPSTREAM_PORT-4000}

bash scripts/_jinja.sh

rm -rf build || true; mkdir build; mkdir build/log/
cp docker-compose.yml build/

docker run --rm \
  -v `pwd`/src/envoy.yaml.j2:/envoy.yaml.j2 \
  -v `pwd`/build/:/output/ \
  jinja:latest jinja \
    --define downstream_hostname_port $downstream_hostname_port \
    --define upstream_hostname $upstream_hostname \
    --define upstream_port $upstream_port \
    --output /output/envoy.yaml \
    /envoy.yaml.j2

echo 'Done, ./build folder'

