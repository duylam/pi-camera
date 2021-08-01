#!/bin/bash

python_cmd=python3
if ! command -v $python_cmd &> /dev/null; then
  python_cmd=python
fi

# See https://docs.python.org/3/library/unittest.html?highlight=test#test-discovery
$python_cmd -m unittest discover -t . -s test/

