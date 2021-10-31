#!/bin/bash

set -e

bash scripts/build.sh

cd build

# Run docker containers in foreground in dev mode
PI_CAMERA_DOCKER_COMPOSE_UP_OPT="" bash start.sh

