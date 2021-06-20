#!/bin/bash

# See https://docs.python.org/3/library/unittest.html?highlight=test#test-discovery
python3 -m unittest discover -t . -s test/

