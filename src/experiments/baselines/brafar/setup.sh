#!/bin/sh
# Brafar (Xie et al., ISSTA'24) at the evaluated commit, with our stdin/stdout adaptation and crash fixes
# (histra.patch). Needs git and uv.
set -e
cd "$(dirname "$0")"
[ -d upstream ] || git clone -q https://github.com/LinnaX7/brafar-python upstream
git -C upstream checkout -q d764a069483d90e03f322220e58fdbf7b9694880
[ -f upstream/basic_framework/stdin_io.py ] || git -C upstream apply ../histra.patch
uv venv -q -p 3.11 upstream/.venv
uv pip install -q -p upstream/.venv/bin/python -r upstream/requirements.txt
