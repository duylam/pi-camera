#!/bin/bash

rm -rf build || true; mkdir build; mkdir build/log/
cp -r src/ build/

echo "Done, check ./build folder"

