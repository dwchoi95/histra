"""Clean ablation of the TRAJECTORY itself: run histra_llm with the trajectory ON
vs OFF (last submission only) on the SAME users, model, peer, and prompt skeleton.
The only variable is whether the LLM sees the whole submission history. The delta
is the pure effect of the trajectory — the project's central claim.

Usage: env/bin/python baselines/traj_ablation.py -p p02659 p02694 p03438 -n 20
"""
import os, sys, time, argparse
from statistics import mean
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warnings; warnings.filterwarnings("ignore")
from src.utils import DataLoader
from src.utils import metrics as _metrics
import baselines.histra_llm as H

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(pid, n, traj_on):
    H.USE_TRAJ = traj_on
    _, timeout, tests, trajs, refs = DataLoader.run(os.path.join(ROOT, "data", pid))[0]
    sub = {u: trajs[u] for u in list(trajs)[:n]}
    out = H.solve(pid, timeout, tests, sub, refs)
    npass, ips, secs = 0, [], []
    for u, (patch, s) in out.items():
        secs.append(s)
        if patch:
            npass += 1
            ip = _metrics.intent_preservation(sub[u][-1], patch, refs.get(u))
            if ip is not None:
                ips.append(ip)
    return {"rr": npass / len(sub) if sub else 0, "n": len(sub),
            "ip": mean(ips) if ips else None, "att": mean(secs) if secs else 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--problems", nargs="+", required=True)
    ap.add_argument("-n", type=int, default=20)
    args = ap.parse_args()

    def ipf(x):
        return f"{x:+.2f}" if x is not None else "  -- "
    print(f"{'pid':8} | {'TRAJ OFF (last)  RR  IP':>24} | {'TRAJ ON (history)  RR  IP':>26} | dRR")
    print("-" * 80)
    for pid in args.problems:
        off = run(pid, args.n, False)
        on = run(pid, args.n, True)
        os_ = f"{off['rr']*100:4.0f}% {ipf(off['ip'])}"
        on_ = f"{on['rr']*100:4.0f}% {ipf(on['ip'])} {on['att']:4.1f}s"
        d = f"{(on['rr']-off['rr'])*100:+.0f}pp"
        print(f"{pid:8} | {os_:>24} | {on_:>26} | {d}", flush=True)


if __name__ == "__main__":
    main()
