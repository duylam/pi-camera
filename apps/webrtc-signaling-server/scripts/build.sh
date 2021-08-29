#!/bin/bash

docker_image_name=${PI_MEETING_DOCKER_IMAGE_NAME-webrtc-signaling} 
docker_image_tag=${PI_MEETING_DOCKER_IMAGE_TAG-latest}

npm i
rm -rf build || true
mkdir build
mkdir build/app
cp -r package.json package-lock.json src/ build/app/
cp docker/* build/

echo "See build/ folder"

