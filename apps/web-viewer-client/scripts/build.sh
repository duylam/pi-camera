#!/bin/bash

NODE_ENV=production vue-cli-service build
rm -rf ./www || true
mkdir ./www
mv dist/* ./www/
mv ./www dist/
cp docker-compose.yml dist/

