#!/bin/sh
# LSGen (Dai et al., AAAI'26) at the evaluated commit; run_lsgen.py drives its own code through lsgen_bridge.py.
# Needs git and uv; GPT-4o calls need OPENAI_API_KEY.
set -e
cd "$(dirname "$0")"
[ -d upstream ] || git clone -q https://github.com/PandaAB/LSGen upstream
git -C upstream checkout -q cb664a11a6b7a835da27e9af20fd2d39892415fc
uv venv -q -p 3.10 upstream/.venv
uv pip install -q -p upstream/.venv/bin/python torch==2.14.1 transformers==5.20.2 accelerate==1.15.0 datasets==5.1.0 \
  numpy==2.2.6 pandas==2.3.3 requests==2.34.2 tqdm
