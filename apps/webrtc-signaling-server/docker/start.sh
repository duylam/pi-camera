#!/bin/bash

docker-compose down &>/dev/null || true
docker-compose up -d

echo "Listening ports:"
echo "	- Signing service on 4000"

