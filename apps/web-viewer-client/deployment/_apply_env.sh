#!/bin/sh

pip3 install jinja2-cli

cd www/js/

stdout="`ls app.*.js`"
app_js_filename="`basename $stdout`"
jinja2 -D "grpc_api_base_url=$grpc_api_base_url" \
  -D "webrtc_ice_server_urls=$webrtc_ice_server_urls" \
  $app_js_filename.tpl -o $app_js_filename

