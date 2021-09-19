#!/bin/bash

set -e

bash scripts/build.sh

cd build
PI_MEETING_DOCKER_COMPOSE_UP_OPT="" bash start.sh

