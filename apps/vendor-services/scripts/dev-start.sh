#!/bin/bash

set -e

bash scripts/build.sh

cd build
bash start.sh

