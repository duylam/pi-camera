#!/bin/bash

activate_venv() {
  mkdir .penv &>/dev/null || true
  if [ -z "`ls .penv`" ]; then
    # Use https://docs.python.org/3/library/venv.html to create virtual environment
    $python_cmd -m venv --clear ./.penv
  fi
  source .penv/bin/activate
}

python_cmd="python3"

if ! command -v $python_cmd &>/dev/null; then
  python_cmd="python"
fi

activate_venv

# Install deps
pip3 install -r requirements.txt
poetry install || true # not sure why poetry keeps upgrading lib which causes error

bash scripts/compile_proto.sh

echo 'Shell entered virtual environment. To exit, type "deactivate"'
echo ""

