#!/bin/bash

npm i
NODE_ENV=production \
  VUE_APP_GRPC_API_BASE_URL="{{ grpc_api_base_url }}" \
  VUE_APP_WEBRTC_ICE_SERVER_URLS="{{ webrtc_ice_server_urls }}" \
  vue-cli-service build
rm -rf ./www || true
mkdir ./www
mv dist/* ./www/
mv ./www dist/
cp -r deployment/ dist/

# Keep app.js file as template for overriding with runtime
# env on launching
cd dist/www/js
for filename in $(ls app.*.js)
do
  cp $filename $filename.tpl
done

echo "Done, check ./dist folder"

