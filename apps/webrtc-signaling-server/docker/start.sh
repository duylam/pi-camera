#!/bin/bash

echo "Supported environments:"
echo "	- PI_CAMERA_GRPC_PORT=$PI_CAMERA_GRPC_PORT"
echo "	- PI_CAMERA_HEARTBEAT_INTERVAL_MS=$PI_CAMERA_HEARTBEAT_INTERVAL_MS"
echo "	- PI_CAMERA_MAX_EVENT_LISTENER=$PI_CAMERA_MAX_EVENT_LISTENER"

docker-compose down &>/dev/null || true
docker-compose up --build -d

echo "Started. Ports:"
echo "	- Signing service on 4000"

