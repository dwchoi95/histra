#!/usr/bin/env bash
cd /home/selab/cdw/histra
PY=env/bin/python
for m in loop beam beam_fb; do
  echo "### running $m" 
  $PY baselines/exp.py --method $m --problems p02694 p02659 -n 30 -k 4 --budget 80
done
echo "ALL DONE"
