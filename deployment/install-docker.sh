#!/bin/bash

set -e # stop execution on command error

if ! command -v docker &>/dev/null
then
  echo ">>> Install Docker Engine"
  curl https://get.docker.com/ | bash -e -s -
  echo ">>> Enable non-root user to run docker"
  sudo usermod -aG docker $USER
fi

if ! command -v docker-compose &>/dev/null
then
  echo ">>> Install Docker Compose"
  sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
fi

echo ""
echo ">>> Completed !."
echo ""

