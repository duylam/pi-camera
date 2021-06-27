#!/bin/bash

set -e # stop on error

python_cmd=./.penv/bin/python
if [ ! -f "$python_cmd" ] ; then
  python_cmd=python3

  if ! command -v $python_cmd &> /dev/null; then
    python_cmd=python
  fi
fi

out_dir="./src/schema_python"
bash ../../schema/scripts/compile_python.sh "`realpath $(which $python_cmd)`" "`realpath $out_dir`"

