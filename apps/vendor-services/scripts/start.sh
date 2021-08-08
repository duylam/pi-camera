#!/bin/bash

set -e

bash scripts/build.sh

cd build

docker-compose up

