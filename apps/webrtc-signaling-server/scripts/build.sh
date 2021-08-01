#!/bin/bash

npm run compile-proto
rm -rf build || true
mkdir build
cp -r package.json package-lock.json src/ build/

echo "See build/ folder"

