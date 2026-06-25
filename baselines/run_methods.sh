#!/usr/bin/env bash
cd /home/selab/cdw/histra
PY=env/bin/python
PROBS="p02694 p02659 p03324 p02823"
for m in beam coherent cascade; do
  echo "### running $m"
  $PY baselines/exp.py --method $m --problems $PROBS -n 30 -k 4 --budget 80
done
echo "ALL DONE"
