"""Re-score the committed results with trajectory-aware IP metrics and compare.

For every approach's results/<pid>/<approach>.csv, over its repaired (fixed==1)
users, compute four intent-preservation numbers using the FULL trajectory loaded
from data/: IP_last (current, last-WA only, read from the csv), IP_mean (1),
IP_recency (2), IP_stable (3). Reports RR + all four per approach.
"""
import os, sys, csv, argparse
from statistics import mean
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warnings; warnings.filterwarnings("ignore")
from src.utils import DataLoader
from baselines.traj_metrics import ip_mean, ip_recency, ip_stable

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPROACHES = ["partraj", "histra", "par", "refactory"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--problems", nargs="+", default=None)
    args = ap.parse_args()

    problems = DataLoader.run(os.path.join(ROOT, "data"))
    if args.problems:
        problems = [p for p in problems if p[0] in args.problems]

    acc = {a: {"pass": 0, "n": 0, "last": [], "mean": [], "rec": [], "stab": []}
           for a in APPROACHES}

    for pid, _, _, trajs, refs in problems:
        for a in APPROACHES:
            path = os.path.join(ROOT, "results", pid, f"{a}.csv")
            if not os.path.exists(path):
                continue
            for r in csv.DictReader(open(path, encoding="utf-8")):
                acc[a]["n"] += 1
                if str(r.get("fixed")) != "1":
                    continue
                acc[a]["pass"] += 1
                uid = r["user_id"]
                patch = r.get("patch") or ""
                oracle = r.get("oracle") or refs.get(uid) or ""
                traj = trajs.get(uid) or ([r.get("buggy")] if r.get("buggy") else [])
                if not patch or not traj:
                    continue
                try:
                    acc[a]["last"].append(float(r["ip"]))
                except Exception:
                    pass
                for key, fn in (("mean", ip_mean(traj, patch, oracle)),
                                ("rec", ip_recency(traj, patch, oracle)),
                                ("stab", ip_stable(traj, patch))):
                    if fn is not None:
                        acc[a][key].append(fn)
        print(f"  scored {pid}", flush=True)

    def m(xs):
        return f"{mean(xs):+.3f}" if xs else "  --  "
    print("\n=== Intent-Preservation metric comparison (micro-avg over repaired) ===")
    print(f"{'approach':10} | {'RR':>6} | {'IP_last(cur)':>12} | {'IP_mean(1)':>11} | "
          f"{'IP_recency(2)':>13} | {'IP_stable(3)':>12}")
    print("-" * 78)
    for a in APPROACHES:
        d = acc[a]
        rr = d["pass"] / d["n"] if d["n"] else 0
        print(f"{a:10} | {rr*100:5.0f}% | {m(d['last']):>12} | {m(d['mean']):>11} | "
              f"{m(d['rec']):>13} | {m(d['stab']):>12}")
    print("\nIP_last/mean/recency in [-1,1] (higher=closer to the student's code);")
    print("IP_stable in [0,1] = fraction of statements stable across ALL attempts kept.")


if __name__ == "__main__":
    main()
