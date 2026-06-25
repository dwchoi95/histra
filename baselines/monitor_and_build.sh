#!/usr/bin/env bash
# Wait for PaR, Refactory, and HISTRA(missing) runs to finish, then collect
# Refactory patches and build the 3-way comparison table.
set -u
ROOT=/home/selab/cdw/histra
PY=$ROOT/env/bin/python
LOG=$ROOT/baselines/monitor.log
echo "monitor started $(date)" > "$LOG"

alive() {
  local n_par n_ref n_his
  n_par=$(pgrep -f "python baselines/par/run_par.py" | wc -l)
  n_ref=$(pgrep -f "run.py -d ./data_histra" | wc -l)
  n_his=$(pgrep -f "histra_sample.py" | wc -l)
  echo "$n_par $n_ref $n_his"
}

for i in $(seq 1 360); do      # up to 6 hours (60s * 360)
  read p r h <<< "$(alive)"
  echo "$(date +%H:%M:%S) iter=$i par=$p refactory=$r histra=$h" >> "$LOG"
  if [ "$p" -eq 0 ] && [ "$r" -eq 0 ] && [ "$h" -eq 0 ]; then
    echo "all runs finished at $(date)" >> "$LOG"
    break
  fi
  sleep 60
done

echo "=== collecting Refactory patches ===" >> "$LOG"
cd "$ROOT"
$PY baselines/refactory/collect_refactory.py >> "$LOG" 2>&1

echo "=== building comparison table ===" >> "$LOG"
$PY baselines/build_comparison.py > baselines/comparison.txt 2>> "$LOG"
echo "DONE $(date)" >> "$LOG"
cat baselines/comparison.txt >> "$LOG"
