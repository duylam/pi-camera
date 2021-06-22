#!/bin/bash

set -e # stop on error

python3_cmd=python3
schema_root_dir="`dirname $(dirname $0)`"
out_dir="$1"

validate()
{
  if ! command -v $python3_cmd &> /dev/null; then
    python3_cmd=python  
  
    if ! command -v $python3_cmd &> /dev/null; then
      echo "Missing python"
      exit -1
    fi
  fi
  
  local python_version="`$python3_cmd --version`"
  if [[ ! "$python_version" == *"Python 3."* ]]; then
    echo "Python 3.5+ required. Found: $python_version"
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

# Create virtual environment if unavailable
# See https://docs.python.org/3/library/venv.html
env_dir="$schema_root_dir/.penv" # this folder is in .gitignore

if [ ! -d "$env_dir" ]; then
  echo "Creating virtual environment dir at $env_dir"
  $python3_cmd -m venv --clear $env_dir
fi

$env_dir/bin/pip show grpcio-tools &>/dev/null || $env_dir/bin/pip install -r $schema_root_dir/requirements.txt
 
$env_dir/bin/python -m grpc_tools.protoc -I $schema_root_dir/src/ --python_out=$out_dir --grpc_python_out=$out_dir $schema_root_dir/src/rtc_signaling_service.proto

echo "Finished!"

