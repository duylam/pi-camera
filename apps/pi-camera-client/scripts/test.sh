#!/bin/bash

python_cmd=./.penv/bin/python
if [ ! -f "$python_cmd" ] ; then
  python_cmd=python3

  if ! command -v $python_cmd &> /dev/null; then
    python_cmd=python
  fi
fi

# See https://docs.python.org/3/library/unittest.html?highlight=test#test-discovery
$python_cmd -m unittest discover -t . -s test/

