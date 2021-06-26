#!/bin/bash

set -e # stop on error

schema_root_dir="`dirname $(dirname $0)`"
python3_cmd="$1"
out_dir="$2"

validate()
{
  usage_line="Usage: $0 /path/python /path/out/dir/"
  if [ -z "$python3_cmd" ]; then
    echo "Missing python path"
    echo $usage_line
    exit -1
  fi

  if [ -z "$out_dir" ]; then
    echo "Missing outdir path"
    echo $usage_line
    exit -1
  fi
}

validate

rm -rf $out_dir || true
mkdir $out_dir

pip_cmd="`dirname $python3_cmd`"/pip

$pip_cmd show grpcio-tools &>/dev/null || $pip_cmd install -r $schema_root_dir/requirements.txt
 
$python3_cmd -m grpc_tools.protoc -I $schema_root_dir/src/ --python_out=$out_dir --grpc_python_out=$out_dir $schema_root_dir/src/rtc_signaling_service.proto

echo "Finished!"

