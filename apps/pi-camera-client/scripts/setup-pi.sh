#!/bin/bash

sudo apt-get update

# Python3 required
if ! command -v python3 &> /dev/null; then
  echo "* Installing python3"
  sudo apt-get install -y python3
fi

# Required while installing python libs
sudo apt-get install -y libffi-dev

