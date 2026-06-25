"""Run HISTRA on the SAME deterministic 50-buggy sample (sorted uids) used by the
Refactory and PaR baselines, so all three tools are scored on identical sets.
Output schema matches the main runner (results.csv + overall.csv).
"""
import os, sys, csv, time, argparse
from statistics import mean
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import warnings; warnings.filterwarnings("ignore")
from src.utils import DataLoader
from src.core.histra import HISTRA
from src.utils import metrics as _metrics


def run_problem(pid, timeout, tests, trajs, refs, sample, out_root):
    uids = sorted(trajs)[:sample]
    trajs = {u: trajs[u] for u in uids}
    t0 = time.time()
    histra = HISTRA(timeout, tests, refs)
    results = histra.run(trajs)
    total = time.time() - t0

    rows = [("user_id", "pass", "ted", "ip", "att_seconds", "buggy", "fixed", "oracle")]
    pass_cnt, ted_vals, ip_vals = 0, [], []
    for uid in uids:
        patch = results.get(uid)
        buggy = trajs[uid][-1] if trajs.get(uid) else None
        oracle = refs.get(uid)
        passed = patch is not None
        ted = _metrics.ted(buggy, patch) if passed and buggy else None
        ip = (_metrics.intent_preservation(buggy, patch, oracle)
              if passed and buggy and oracle else None)
        if passed:
            pass_cnt += 1
            if ted is not None: ted_vals.append(ted)
            if ip is not None: ip_vals.append(ip)
        rows.append((uid, int(passed), ted if ted is not None else "",
                     ip if ip is not None else "", "", buggy or "",
                     patch or "", oracle or ""))
    n = max(len(uids), 1)
    att = total / n
    rows = [rows[0]] + [(u, p, t, i, f"{att:.6f}", b, f, o)
                        for (u, p, t, i, _a, b, f, o) in rows[1:]]
    od = os.path.join(out_root, pid); os.makedirs(od, exist_ok=True)
    with open(os.path.join(od, "results.csv"), "w", newline="", encoding="utf-8") as fp:
        csv.writer(fp).writerows(rows)
    print(f"[{pid}] RR={pass_cnt/n:.3f} pass={pass_cnt}/{n} "
          f"ted={mean(ted_vals) if ted_vals else 0:.2f} "
          f"ip={mean(ip_vals) if ip_vals else 0:+.2f} t={total:.1f}s", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--dataset", default=os.path.join(ROOT, "data"))
    ap.add_argument("-p", "--problems", nargs="+", default=None)
    ap.add_argument("-n", "--sample", type=int, default=50)
    ap.add_argument("-o", "--out", default=os.path.join(HERE, "results_histra_50"))
    args = ap.parse_args()
    problems = DataLoader.run(args.dataset)
    if args.problems:
        problems = [p for p in problems if p[0] in args.problems]
    os.makedirs(args.out, exist_ok=True)
    for pid, timeout, tests, trajs, refs in problems:
        run_problem(pid, timeout, tests, trajs, refs, args.sample, args.out)


if __name__ == "__main__":
    main()
