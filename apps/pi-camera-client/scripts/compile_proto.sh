#!/bin/bash

set -e # stop on error

python_cmd=python3
if ! command -v $python_cmd &> /dev/null; then
  python_cmd=python
fi

bash ../../schema/scripts/compile_python.sh "`which $python_cmd`" "`pwd`/src/schema_python"

