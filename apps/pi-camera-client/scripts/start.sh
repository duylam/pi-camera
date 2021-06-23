#!/bin/bash

python_cmd=python3

if [ ! -z "$VIRTUAL_ENV" ]; then
  python_cmd=./.penv/bin/python
fi

bash scripts/compile_proto.sh
$python_cmd src/app.py

