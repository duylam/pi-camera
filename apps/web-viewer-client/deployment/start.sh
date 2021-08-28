#!/bin/bash

grpc_api_base_url=${VUE_APP_GRPC_API_BASE_URL-http://localhost:4001}
webrtc_ice_server_urls=${VUE_APP_WEBRTC_ICE_SERVER_URLS-stun:localhost:3478?transport=udp}

echo "Support below variables with their real data or default"
echo "	- VUE_APP_GRPC_API_BASE_URL=$grpc_api_base_url"
echo "	- VUE_APP_WEBRTC_ICE_SERVER_URLS=$webrtc_ice_server_urls"

docker run --rm \
  --entrypoint "/bin/sh" \
  --workdir "/host_dir" \
  -e "grpc_api_base_url=$grpc_api_base_url" \
  -e "webrtc_ice_server_urls=$webrtc_ice_server_urls" \
  -v "`pwd`:/host_dir/:rw" \
  python:3.9.6-alpine3.14 _apply_env.sh

docker-compose down &>/dev/null || true
docker-compose up -d

echo ""
echo "Listening ports: "
echo "	- Web-viewer service on 8081"

