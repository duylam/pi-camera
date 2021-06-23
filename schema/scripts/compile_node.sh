#!/bin/bash

set -e # stop on error

schema_root_dir="`dirname $(dirname $0)`"
out_dir="$1"

validate()
{
  if ! command -v node &> /dev/null; then
    echo "Missing node"
    exit -1
  fi
  
  if [ -z "$out_dir" ]; then
    echo "Usage: $0 /path/to/out/dir/"
    exit -1
  fi
}

validate

rm -rf $out_dir || true
mkdir $out_dir

npm i

grpc_tools_node_protoc -I $schema_root_dir/src/ --js_out=import_style=commonjs,binary:$out_dir --grpc_out=grpc_js:$out_dir $schema_root_dir/src/rtc_signaling_service.proto

echo "Finished!"

