#!/bin/bash

docker_image_name=${PI_MEETING_DOCKER_IMAGE_NAME-webrtc-signaling} 
docker_image_tag=${PI_MEETING_DOCKER_IMAGE_TAG-latest}

npm run build

cd docker
rm -rf app || true
mkdir app
cp -r ../build/ ./app/
docker build --label "commit.id=`git rev-parse --short HEAD`" --label "created.time=`date -u '+%Y-%m-%dT%H:%M:%S'`" --tag $docker_image_name:$docker_image_tag .

cd ..
rm -rf dist || true
mkdir dist
cd dist
cp ../docker/start.sh ../docker/docker-compose.yml .

echo "Done, check ./dist folder"

