#!/bin/bash

set -e # stop on error

#
# Install grpc-web
#

# Update this var for upgrading protoc-gen-grpc-web version
# Ref: https://github.com/grpc/grpc-web/releases
VERSION=1.2.1

osName=`node -e "console.log(require('os').type())"`
filename="protoc-gen-grpc-web-$VERSION-linux-x86_64"
if [ "$osName" = "Darwin" ]; then
  filename="protoc-gen-grpc-web-$VERSION-darwin-x86_64"
fi

grpc_tools_bin_path=./node_modules/grpc-tools/bin/
if [ ! -f "$grpc_tools_bin_path/protoc-gen-grpc-web" ]; then
  # Download links: https://github.com/grpc/grpc-web/releases
  cd "$grpc_tools_bin_path"
  curl -OL "https://github.com/grpc/grpc-web/releases/download/$VERSION/$filename"

  # Create soft-link to use one path for both OS and Linux env
  rm protoc-gen-grpc-web &> /dev/null || true
  ln -s `pwd`/$filename protoc-gen-grpc-web
  chmod +x protoc-gen-grpc-web
  echo "Installed grpc-web"
fi

