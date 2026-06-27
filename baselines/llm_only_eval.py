"""Sampled eval of the all-to-LLM baseline (llm_only, gemma3n:e4b) against the
already-computed par/histra results on the SAME first-N users. Shows whether an
LLM, given everything (problem + full trajectory), can do the job alone.
"""
import os, sys, csv, argparse
from statistics import mean
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warnings; warnings.filterwarnings("ignore")
from src.utils import DataLoader
from src.utils import metrics as _metrics
import baselines.llm_only as L

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def baseline(pid, approach, n):
    path = os.path.join(ROOT, "results", pid, f"{approach}.csv")
    if not os.path.exists(path):
        return None
    rows = list(csv.DictReader(open(path, encoding="utf-8")))[:n]
    npass = sum(1 for r in rows if str(r.get("fixed")) == "1")
    ips = [float(r["ip"]) for r in rows if str(r.get("fixed")) == "1" and r.get("ip")]
    return {"rr": npass / len(rows) if rows else 0, "ip": mean(ips) if ips else None}


def run_llm_only(pid, n):
    _, timeout, tests, trajs, refs = DataLoader.run(os.path.join(ROOT, "data", pid))[0]
    sub = {u: trajs[u] for u in list(trajs)[:n]}
    out = L.solve(pid, timeout, tests, sub, refs)
    npass, ips, secs = 0, [], []
    for u, (patch, s) in out.items():
        secs.append(s)
        if patch:
            npass += 1
            ip = _metrics.intent_preservation(sub[u][-1], patch, refs.get(u))
            if ip is not None:
                ips.append(ip)
    return {"rr": npass / len(sub) if sub else 0, "ip": mean(ips) if ips else None,
            "att": mean(secs) if secs else 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--problems", nargs="+", required=True)
    ap.add_argument("-n", type=int, default=25)
    args = ap.parse_args()

    def f(m, key):
        if not m or m.get(key) is None:
            return "  -- "
        return f"{m[key]:+.2f}" if key == "ip" else f"{m[key]*100:3.0f}%"
    print(f"{'pid':8} | {'llm_only(gemma3n) RR  IP  ATT':>30} | {'par RR  IP':>12} | {'histra RR IP':>13}")
    print("-" * 76)
    for pid in args.problems:
        a = run_llm_only(pid, args.n)
        p = baseline(pid, "par", args.n)
        h = baseline(pid, "histra", args.n)
        print(f"{pid:8} | {f(a,'rr')} {f(a,'ip')} {a['att']:5.1f}s            "
              f"| {f(p,'rr')} {f(p,'ip')} | {f(h,'rr')} {f(h,'ip')}", flush=True)


if __name__ == "__main__":
    main()
