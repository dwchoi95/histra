#!/bin/sh
# Paper §4: every repairer on the full benchmark (PER=0). Run from the repo root.
#   sh src/analysis/prelim/run_eval.sh cpu   # merge baseline, HISTRA, ablations   (~2-3 h on 14 workers)
#   sh src/analysis/prelim/run_eval.sh llm   # LLM baselines and LLM+HISTRA        (GPU-bound, many hours)
# Outputs and logs: results/eval/. Then: python src/analysis/prelim/measure.py results/eval/<name>.jsonl ...
set -x
export PER=0 POOL=14
PY=".venv/bin/python -W ignore"
D=src/analysis/prelim
O=results/eval
case "$1" in
cpu)
  $PY $D/baselines.py merge $O/merge.jsonl > $O/merge.log 2>&1
  for m in min plain nostd nohole nokept sizemin; do
    $PY $D/histra_eval.py $m $O/histra_$m.jsonl > $O/histra_$m.log 2>&1
  done ;;
llm)
  $PY $D/baselines.py llm $O/llm_gemma.jsonl gemma4:e4b > $O/llm_gemma.log 2>&1
  $PY $D/llm_histra.py full $O/llm_gemma.jsonl $O/llm_gemma_histra.jsonl gemma4:e4b > $O/llm_gemma_histra.log 2>&1
  $PY $D/llm_histra.py minonly $O/llm_gemma.jsonl $O/llm_gemma_min.jsonl gemma4:e4b > $O/llm_gemma_min.log 2>&1
  $PY $D/baselines.py llm $O/llm_gptoss.jsonl gpt-oss:20b > $O/llm_gptoss.log 2>&1 ;;
esac
# p02686 has the heaviest tests: 14 concurrent workers push correct candidates past its 2 s limit, so its
# trajectories are re-run with 4 workers (the LLM repairers' concurrency) and spliced into the outputs above:
#   sh src/analysis/prelim/run_eval.sh heavy
if [ "$1" = heavy ]; then
  export ONLY=p02686 POOL=4
  $PY $D/baselines.py merge $O/p02686/merge.jsonl > $O/p02686/merge.log 2>&1
  for m in min plain nostd nohole nokept sizemin; do
    $PY $D/histra_eval.py $m $O/p02686/histra_$m.jsonl > $O/p02686/histra_$m.log 2>&1
  done
fi
# Final-review re-runs (2026-10-15):
#   sh src/analysis/prelim/run_eval.sh llm-heavy   # LLM_G (+HISTRA, +Min) on p02686 alone, without concurrent CPU load
#   sh src/analysis/prelim/run_eval.sh fair        # fair history-free controls: Sarfgen-faithful merge, HISTRA with H = {}
if [ "$1" = llm-heavy ]; then
  export ONLY=p02686
  $PY $D/baselines.py llm $O/p02686/llm_gemma.jsonl gemma4:e4b > $O/p02686/llm_gemma.log 2>&1
  $PY $D/llm_histra.py full $O/p02686/llm_gemma.jsonl $O/p02686/llm_gemma_histra.jsonl gemma4:e4b > $O/p02686/llm_gemma_histra.log 2>&1
  $PY $D/llm_histra.py minonly $O/p02686/llm_gemma.jsonl $O/p02686/llm_gemma_min.jsonl gemma4:e4b > $O/p02686/llm_gemma_min.log 2>&1
  $PY $D/splice.py p02686 llm_gemma llm_gemma_histra llm_gemma_min
fi
if [ "$1" = fair ]; then
  $PY $D/baselines.py merge-min $O/merge_min.jsonl > $O/merge_min.log 2>&1
  $PY $D/histra_eval.py nohist $O/histra_nohist.jsonl > $O/histra_nohist.log 2>&1
  export ONLY=p02686 POOL=4
  $PY $D/baselines.py merge-min $O/p02686/merge_min.jsonl > $O/p02686/merge_min.log 2>&1
  $PY $D/histra_eval.py nohist $O/p02686/histra_nohist.jsonl > $O/p02686/histra_nohist.log 2>&1
  unset ONLY
  $PY $D/splice.py p02686 merge_min histra_nohist
fi
