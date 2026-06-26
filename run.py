import os
import argparse
import csv
from statistics import mean
from tqdm import tqdm
from prettytable import PrettyTable
from multiprocessing import Process, Lock
import warnings
warnings.filterwarnings('ignore')

from src.utils import DataLoader
from src.utils import metrics as _metrics
from baselines.approaches import solve as approach_solve, APPROACHES

PER_HEADER = ["user_id", "buggy", "patch", "oracle", "fixed", "ted", "ip", "att"]
OVERALL_HEADER = ["pid", "approach", "corrects", "buggys", "fixed",
                  "rr", "ted", "ip", "att"]


def core(pid, timeout, tests, trajs, refs, approach, reset, out_root, lock):
    out_dir = os.path.join(out_root, pid)
    os.makedirs(out_dir, exist_ok=True)
    per_csv_path = os.path.join(out_dir, f"{approach}.csv")
    overall_path = os.path.join(out_root, "overall.csv")

    if (not reset) and os.path.exists(per_csv_path):
        return

    # Run the chosen approach -> {user_id: (patch_or_None, seconds)}
    results = approach_solve(approach, pid, timeout, tests, trajs, refs)

    rows = [tuple(PER_HEADER)]
    fixed_cnt = 0
    ted_vals, ip_vals, att_vals = [], [], []
    for uid, (patch, secs) in results.items():
        was = trajs.get(uid) or []
        buggy = was[-1] if was else ""
        oracle = refs.get(uid) or ""
        fixed = 1 if patch else 0
        ted = _metrics.ted(buggy, patch) if (fixed and buggy) else None
        ip = (_metrics.intent_preservation(buggy, patch, oracle)
              if (fixed and buggy and oracle) else None)
        if fixed:
            fixed_cnt += 1
            if ted is not None:
                ted_vals.append(ted)
            if ip is not None:
                ip_vals.append(ip)
        att_vals.append(secs)
        rows.append((uid, buggy, patch or "", oracle, fixed,
                     ted if ted is not None else "",
                     ip if ip is not None else "",
                     f"{secs:.6f}"))

    with open(per_csv_path, "w", newline="", encoding="utf-8") as cf:
        csv.writer(cf).writerows(rows)

    corrects = len(refs)
    buggys = max(len(results), 1)
    rr = fixed_cnt / buggys
    ted_mean = mean(ted_vals) if ted_vals else 0.0
    ip_mean = mean(ip_vals) if ip_vals else 0.0
    att_mean = mean(att_vals) if att_vals else 0.0

    summary = PrettyTable()
    summary.field_names = ["PID", "Approach", "Corrects", "Buggys", "Fixed",
                           "RR", "TED", "IP", "ATT(s)"]
    summary.add_row([pid, approach, corrects, len(results), fixed_cnt,
                     f"{rr:.0%}", f"{ted_mean:.2f}", f"{ip_mean:+.2f}",
                     f"{att_mean:.2f}"])
    print(summary)

    with lock:
        overall_rows = []
        if os.path.exists(overall_path) and os.path.getsize(overall_path) > 0:
            with open(overall_path, "r", newline="", encoding="utf-8") as of:
                overall_rows = [r for r in csv.reader(of)]
        if not overall_rows:
            overall_rows.append(OVERALL_HEADER)
        # drop any existing row for this (pid, approach)
        overall_rows = [r for r in overall_rows
                        if r == OVERALL_HEADER or not (len(r) >= 2 and r[0] == pid and r[1] == approach)]
        overall_rows.append([pid, approach, corrects, len(results), fixed_cnt,
                             f"{rr:.6f}", f"{ted_mean:.6f}", f"{ip_mean:.6f}",
                             f"{att_mean:.6f}"])
        with open(overall_path, "w", newline="", encoding="utf-8") as of:
            csv.writer(of).writerows(overall_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', type=str, required=True,
                        help="Path to dataset directory (data/<pid>/...)")
    parser.add_argument('-a', '--approach', type=str, default="histra",
                        choices=list(APPROACHES),
                        help="Repair approach to run: histra | refactory | par")
    parser.add_argument('-r', '--reset', action='store_true', default=False,
                        help="Recompute even if results/<pid>/<approach>.csv exists")
    args = parser.parse_args()

    assert os.path.exists(args.dataset), f"Dataset path does not exist: {args.dataset}"

    problems = DataLoader.run(args.dataset)
    out_root = 'results'
    os.makedirs(out_root, exist_ok=True)

    procs = []
    lock = Lock()
    for data in problems:
        pid, timeout, tests, trajs, refs = data
        out_dir = os.path.join(out_root, pid)
        os.makedirs(out_dir, exist_ok=True)
        per_csv_path = os.path.join(out_dir, f"{args.approach}.csv")
        if (not args.reset) and os.path.exists(per_csv_path):
            continue
        proc = Process(target=core, args=(pid, timeout, tests, trajs, refs,
                                          args.approach, args.reset, out_root, lock))
        proc.start()
        procs.append(proc)

    for proc in procs:
        proc.join()
        if proc.exitcode != 0:
            raise RuntimeError(f"Problem process failed with exit code {proc.exitcode}")
