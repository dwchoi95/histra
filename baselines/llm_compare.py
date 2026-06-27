"""Isolate the TRAJECTORY contribution: histra_llm (full trajectory + peer) vs the
already-computed PaR baseline (last submission + peer), SAME model, SAME peer PSM,
SAME first-N users. The only difference is that histra_llm feeds the LLM the whole
submission history. Reports RR/IP so the delta = the trajectory's effect.

Usage: env/bin/python baselines/llm_compare.py -p p02623 -n 25
"""
import os, sys, csv, time, argparse
from statistics import mean
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warnings; warnings.filterwarnings("ignore")
from src.utils import DataLoader
from src.utils import metrics as _metrics
import baselines.histra_llm as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def par_baseline(pid, n):
    path = os.path.join(ROOT, "results", pid, "par.csv")
    if not os.path.exists(path):
        return None
    # match histra_llm's user order (dict order); par.csv is in that same order
    rows = list(csv.DictReader(open(path, encoding="utf-8")))[:n]
    npass = sum(1 for r in rows if str(r.get("fixed")) == "1")
    ips = [float(r["ip"]) for r in rows if str(r.get("fixed")) == "1" and r.get("ip")]
    return {"rr": npass / len(rows) if rows else 0, "pass": npass, "n": len(rows),
            "ip": mean(ips) if ips else None}


def run_histra_llm(pid, n):
    _, timeout, tests, trajs, refs = DataLoader.run(os.path.join(ROOT, "data", pid))[0]
    sub = {u: trajs[u] for u in list(trajs)[:n]}
    t0 = time.time()
    out = H.solve(pid, timeout, tests, sub, refs)
    npass, ips, secs = 0, [], []
    for u, (patch, s) in out.items():
        secs.append(s)
        if patch:
            npass += 1
            ip = _metrics.intent_preservation(sub[u][-1], patch, refs.get(u))
            if ip is not None:
                ips.append(ip)
    return {"rr": npass / len(sub) if sub else 0, "pass": npass, "n": len(sub),
            "ip": mean(ips) if ips else None, "att": mean(secs) if secs else 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--problems", nargs="+", required=True)
    ap.add_argument("-n", type=int, default=25)
    args = ap.parse_args()

    def ipf(x):
        return f"{x:+.2f}" if x is not None else "  -- "
    print(f"{'pid':8} | {'PaR(last)  RR  IP':>18} | {'histra_llm(traj) RR  IP  ATT':>30} | dRR")
    print("-" * 78)
    for pid in args.problems:
        b = par_baseline(pid, args.n)
        a = run_histra_llm(pid, args.n)
        bs = f"{b['rr']*100:4.0f}% {ipf(b['ip'])}" if b else "  n/a"
        as_ = f"{a['rr']*100:4.0f}% {ipf(a['ip'])} {a['att']:5.1f}s"
        d = f"{(a['rr']-b['rr'])*100:+.0f}pp" if b else ""
        print(f"{pid:8} | {bs:>18} | {as_:>30} | {d}", flush=True)


if __name__ == "__main__":
    main()
