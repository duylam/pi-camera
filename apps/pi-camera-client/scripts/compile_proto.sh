#!/bin/bash

python_cmd=./.penv/bin/python
if [ ! -f "$python_cmd" ] ; then
  python_cmd=python3

  if ! command -v $python_cmd &> /dev/null; then
    python_cmd=python
  fi
fi

bash ../../schema/scripts/compile_python.sh "`which $python_cmd`" ./src/schema_python

