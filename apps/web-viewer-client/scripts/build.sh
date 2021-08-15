#!/bin/bash

npm i
NODE_ENV=production vue-cli-service build
rm -rf ./www || true
mkdir ./www
mv dist/* ./www/
mv ./www dist/
cp -r deployment/ dist/

echo "Done, check ./dist folder"

