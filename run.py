import os
import argparse
import time
import csv
from statistics import mean
from tqdm import tqdm
from prettytable import PrettyTable
from multiprocessing import Process, Lock
import warnings
warnings.filterwarnings('ignore')

from src.utils import DataLoader
from src.core.histra import HISTRA
from src.utils import metrics as _metrics


def core(pid, timeout, tests, trajs, refs, 
         reset, out_root, lock):
    out_dir = os.path.join(out_root, pid)
    os.makedirs(out_dir, exist_ok=True)
    per_csv_path = os.path.join(out_dir, "results.csv")
    overall_path = os.path.join(out_root, "overall.csv")

    # Run HISTRA (multiprocessing under the hood)
    start = time.process_time()
    histra = HISTRA(timeout, tests, refs)
    results = histra.run(trajs)  # {user_id: patch|None}
    total_sec = time.process_time() - start

    # Build per-user metrics (no per-user table printing)
    pass_cnt = 0
    ted_vals, ip_vals = [], []
    csv_rows = [("user_id", "pass", "ted", "ip", "att_seconds", "buggy", "fixed", "oracle")]

    for user_id, patch in tqdm(results.items(), total=len(results), desc="Eval", leave=False):
        wan = trajs.get(user_id, [None])[-1] if user_id in trajs and trajs[user_id] else None
        oracle = refs.get(user_id)
        passed = patch is not None
        ted = _metrics.ted(wan, patch) if passed and wan else None
        ip = _metrics.intent_preservation(wan, patch, oracle) if passed and wan and oracle else None

        # Collect metrics
        if passed:
            pass_cnt += 1
            if ted is not None:
                ted_vals.append(ted)
            if ip is not None:
                ip_vals.append(ip)
        # ATT per user will be computed from total CPU time later

        # Append row with codes instead of saving individual .py files
        csv_rows.append((
            user_id,
            int(passed),
            ted if ted is not None else "",
            ip if ip is not None else "",
            "",  # placeholder; replaced after ATT per user is known
            wan or "",
            patch or "",
            oracle or "",
        ))

    # Aggregate metrics
    total_users = max(len(trajs), 1)
    rr = pass_cnt / total_users
    ted_mean = mean(ted_vals) if ted_vals else 0.0
    ip_mean = mean(ip_vals) if ip_vals else 0.0
    # ATT: use total CPU time divided by number of users in this problem
    n_users = max(len(trajs), 1)
    att_per_user = (total_sec / n_users) if n_users else 0.0
    att_mean = att_per_user

    # Print summary-only table
    summary_table = PrettyTable()
    summary_table.field_names = ["PID", "Users", "Pass", "RR", "TED(mean)", "IP(mean)", "ATT(mean)s", "Total(s)"]
    summary_table.add_row([
        pid,
        len(trajs),
        pass_cnt,
        f"{rr:.0%}",
        f"{ted_mean:.2f}",
        f"{ip_mean:+.2f}",
        f"{att_mean:.2f}",
        f"{total_sec:.2f}",
    ])

    # Update ATT column in csv_rows (skip header index 0)
    csv_rows = [csv_rows[0]] + [
        (uid, pas, tedc, ipc, f"{att_per_user:.6f}", buggy, fixed, oracle)
        for (uid, pas, tedc, ipc, _old_att, buggy, fixed, oracle) in csv_rows[1:]
    ]

    # Save per-problem CSV (overwrite or create)
    with open(per_csv_path, "w", newline="", encoding="utf-8") as cf:
        writer = csv.writer(cf)
        writer.writerows(csv_rows)

    with lock:
        print(summary_table, flush=True)

        # Update overall.csv (append or replace pid row)
        overall_rows = []
        if os.path.exists(overall_path) and os.path.getsize(overall_path) > 0:
            with open(overall_path, "r", newline="", encoding="utf-8") as of:
                reader = csv.reader(of)
                for row in reader:
                    overall_rows.append(row)
        header = ["pid", "rr", "pass", "n_users", "ted_mean", "ip_mean", "att_mean", "total_seconds"]
        if not overall_rows:
            overall_rows.append(header)
        # remove existing row for pid if present (refresh)
        overall_rows = [r for r in overall_rows if not (r and r[0] == pid) or r == header]
        overall_rows.append([
            pid,
            f"{rr:.6f}",
            str(pass_cnt),
            str(n_users),
            f"{ted_mean:.6f}",
            f"{ip_mean:.6f}",
            f"{att_mean:.6f}",
            f"{total_sec:.6f}",
        ])
        with open(overall_path, "w", newline="", encoding="utf-8") as of:
            writer = csv.writer(of)
            writer.writerows(overall_rows)

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', type=str, required=True,
                        help="Path to dataset directory or JSON file")
    parser.add_argument('-ab', '--ablation', type=str, default=None,
                        choices=["full", "no-reformat", 
                                 "no-standardize", 
                                 "ref-random", "ref-oracle", 
                                 "wan-ac", "was-only", "plain"],
                        help="Ablate a single MooRepair component; 'random' "
                             "replaces ALL selection steps with random choices "
                             "(only valid with -a MooRepair)")
    parser.add_argument('-s', '--sampling', action='store_true', default=False,
                        help="Use 10%% sampling of buggy programs")
    parser.add_argument('-r', '--reset', action='store_true', default=False,
                        help="Reset overall.csv before running experiments")
    args = parser.parse_args()

    assert os.path.exists(args.dataset), f"Dataset path does not exist: {args.dataset}"
    assert args.ablation in [None, "full", "no-reformat", "no-standardize",
                             "ref-random", "ref-oracle", "wan-ac", "was-only", "plain"], \
        f"Invalid ablation choice: {args.ablation}"
    assert isinstance(args.sampling, bool), "Sampling must be a boolean flag"
    assert isinstance(args.reset, bool), "Reset must be a boolean flag"

    problems = DataLoader.run(args.dataset)

    out_root = 'results'
    os.makedirs(out_root, exist_ok=True)

    procs = []
    lock = Lock()
    for data in problems:
        pid, timeout, tests, trajs, refs = data
        # Prepare output directory and skipping/refresh logic
        out_dir = os.path.join(out_root, pid)
        os.makedirs(out_dir, exist_ok=True)
        per_csv_path = os.path.join(out_dir, "results.csv")

        # Skip if results already exist and not resetting
        if (not args.reset) and os.path.exists(per_csv_path):
            continue

        proc = Process(target=core, args=(pid, timeout, tests, trajs, refs, 
                                          args.reset, out_root, lock))
        proc.start()
        procs.append(proc)
    
    for proc in procs:
        proc.join()
        if proc.exitcode != 0:
            raise RuntimeError(f"Problem process failed with exit code {proc.exitcode}")
    

