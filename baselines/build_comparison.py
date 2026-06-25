"""Build the HISTRA vs PaR vs Refactory comparison table on the SHARED 50-buggy
sample (sorted uids) per problem. Reads each tool's per-user results.csv and
reports RR (pass/N), mean TED and mean IP over repaired cases.

HISTRA source per problem: results_histra_50/<pid> if present, else the main
results/<pid> subset to the 50 sampled uids.
PaR:       baselines/par/results_par/<pid>
Refactory: baselines/refactory/results_refactory/<pid>
"""
import os, sys, csv
from statistics import mean
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import warnings; warnings.filterwarnings("ignore")
from src.utils import DataLoader

PAR = os.path.join(HERE, "par", "results_par")
REF = os.path.join(HERE, "refactory", "results_refactory")
HIS_50 = os.path.join(HERE, "results_histra_50")
HIS_MAIN = os.path.join(ROOT, "results")


def read_rows(path):
    if not os.path.exists(path):
        return None
    out = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[r["user_id"]] = r
    return out


def metrics_for(rowmap, uids):
    """RR over |uids|, mean TED & IP over repaired (pass==1)."""
    if rowmap is None:
        return None
    npass = 0; teds = []; ips = []
    for u in uids:
        r = rowmap.get(u)
        if not r:
            continue
        if str(r.get("pass")) == "1":
            npass += 1
            try: teds.append(float(r["ted"]))
            except: pass
            try: ips.append(float(r["ip"]))
            except: pass
    n = len(uids)
    return {"rr": npass / n if n else 0.0, "pass": npass, "n": n,
            "ted": mean(teds) if teds else None,
            "ip": mean(ips) if ips else None}


def histra_rows(pid, uids):
    p = os.path.join(HIS_50, pid, "results.csv")
    if os.path.exists(p):
        return read_rows(p)
    return read_rows(os.path.join(HIS_MAIN, pid, "results.csv"))


def fmt(m):
    if m is None:
        return f"{'--':>6} {'--':>6} {'--':>6}"
    ted = f"{m['ted']:.1f}" if m['ted'] is not None else "--"
    ip = f"{m['ip']:+.2f}" if m['ip'] is not None else "--"
    return f"{m['rr']*100:5.1f}% {ted:>6} {ip:>6}"


def main():
    problems = DataLoader.run(os.path.join(ROOT, "data"))
    sample = {pid: sorted(trajs)[:50] for pid, _, _, trajs, _ in problems}

    print(f"{'problem':9} | {'HISTRA  RR   TED    IP':>22} | "
          f"{'PaR     RR   TED    IP':>22} | {'Refactory RR  TED   IP':>22}")
    print("-" * 86)
    agg = {"HISTRA": [[], [], 0, 0], "PaR": [[], [], 0, 0], "Refactory": [[], [], 0, 0]}
    for pid, _, _, trajs, _ in problems:
        uids = sample[pid]
        h = metrics_for(histra_rows(pid, uids), uids)
        p = metrics_for(read_rows(os.path.join(PAR, pid, "results.csv")), uids)
        r = metrics_for(read_rows(os.path.join(REF, pid, "results.csv")), uids)
        print(f"{pid:9} | {fmt(h)} | {fmt(p)} | {fmt(r)}")
        for name, m in (("HISTRA", h), ("PaR", p), ("Refactory", r)):
            if m:
                agg[name][2] += m["pass"]; agg[name][3] += m["n"]
                if m["ted"] is not None: agg[name][0].append(m["ted"])
                if m["ip"] is not None: agg[name][1].append(m["ip"])
    print("-" * 86)
    cells = []
    for name in ("HISTRA", "PaR", "Refactory"):
        teds, ips, npass, n = agg[name]
        rr = npass / n if n else 0.0
        m = {"rr": rr, "pass": npass, "n": n,
             "ted": mean(teds) if teds else None,
             "ip": mean(ips) if ips else None}
        cells.append(fmt(m))
    print(f"{'OVERALL':9} | {cells[0]} | {cells[1]} | {cells[2]}")
    print("\n(RR = repaired/sample; TED = mean tree-edit-distance buggy->patch; "
          "IP = mean intent-preservation, higher=closer to student. "
          "Per-problem mean TED/IP are macro-averaged for OVERALL.)")


if __name__ == "__main__":
    main()
