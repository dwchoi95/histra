#!/bin/sh
# Refactory (Hu et al., ASE'19) at the evaluated commit, with our stdin/stdout adaptation (histra.patch).
# Needs git and uv.
set -e
cd "$(dirname "$0")"
[ -d upstream ] || git clone -q https://github.com/githubhuyang/refactory upstream
git -C upstream checkout -q f05583a56c2e3c50aa8cc0327645283f27df3a68
[ -f upstream/basic_framework/stdin_io.py ] || git -C upstream apply ../histra.patch
uv venv -q -p 3.9 upstream/.venv
uv pip install -q -p upstream/.venv/bin/python -r upstream/requirements.txt
