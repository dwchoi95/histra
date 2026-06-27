"""A/B test a HISTRA change against the committed results/<pid>/histra.csv baseline.

Baseline = the already-computed histra.csv (current code, first N users in run
order). After = re-run HISTRA._pipeline_run with whatever src/core/* is on disk
now, on the SAME first N users. Reports RR/IP/ATT per problem so we can gate:
targets up, regression holds, IP >= +0.30.

Usage: env/bin/python baselines/ab_test.py -p p02623 p03438 p02761 p02823 p02659 -n 30
"""
import os, sys, csv, time, argparse
from statistics import mean
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warnings; warnings.filterwarnings("ignore")
from src.utils import DataLoader
from src.core.histra import HISTRA
from src.utils import metrics as _metrics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def baseline(pid, n):
    path = os.path.join(ROOT, "results", pid, "histra.csv")
    if not os.path.exists(path):
        return None
    rows = list(csv.DictReader(open(path, encoding="utf-8")))[:n]
    npass = sum(1 for r in rows if str(r.get("fixed")) == "1")
    ips = [float(r["ip"]) for r in rows if str(r.get("fixed")) == "1" and r.get("ip")]
    return {"rr": npass / len(rows) if rows else 0, "pass": npass, "n": len(rows),
            "ip": mean(ips) if ips else None}


def after(pid, n):
    _, timeout, tests, trajs, refs = DataLoader.run(os.path.join(ROOT, "data", pid))[0]
    h = HISTRA(timeout, tests, refs)
    uids = list(trajs)[:n]
    npass, ips, secs = 0, [], []
    for u in uids:
        t0 = time.time()
        try:
            patch = h._pipeline_run(trajs[u], h._get_ac_pool(u))
        except Exception:
            patch = None
        secs.append(time.time() - t0)
        if patch:
            npass += 1
            ip = _metrics.intent_preservation(trajs[u][-1], patch, refs.get(u))
            if ip is not None:
                ips.append(ip)
    return {"rr": npass / len(uids) if uids else 0, "pass": npass, "n": len(uids),
            "ip": mean(ips) if ips else None, "att": mean(secs) if secs else 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--problems", nargs="+", required=True)
    ap.add_argument("-n", type=int, default=30)
    args = ap.parse_args()
    print(f"{'pid':8} | {'baseline RR  IP':>16} | {'after RR   IP   ATT':>22} | delta")
    print("-" * 70)
    def ipf(x):
        return f"{x:+.2f}" if x is not None else "  -- "
    for pid in args.problems:
        b = baseline(pid, args.n)
        a = after(pid, args.n)
        bs = f"{b['rr']*100:4.0f}% {ipf(b['ip'])}" if b else "  n/a"
        as_ = f"{a['rr']*100:4.0f}% {ipf(a['ip'])} {a['att']:5.1f}s"
        dl = f"{(a['rr']-b['rr'])*100:+.0f}pp" if b else ""
        print(f"{pid:8} | {bs:>16} | {as_:>22} | {dl}", flush=True)


if __name__ == "__main__":
    main()
