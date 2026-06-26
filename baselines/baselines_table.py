"""Per-problem RR / TED / IP / ATT for the two baselines (Refactory, PaR) on the
shared 50-buggy sample, plus an OVERALL row. Refactory ATT = mean 'Total Time'
per repaired wrong (from refactory_online.csv); PaR ATT = mean att_seconds
(wall-clock per buggy). p03240 timed out for Refactory (shown as --).
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
REF_RAW = os.path.join(HERE, "refactory", "data_histra")


def read(path):
    if not os.path.exists(path):
        return None
    return {r["user_id"]: r for r in csv.DictReader(open(path, encoding="utf-8"))}

def stats(rm, uids):
    if rm is None:
        return None
    npass, teds, ips, atts = 0, [], [], []
    for u in uids:
        r = rm.get(u)
        if not r:
            continue
        if str(r.get("pass")) == "1":
            npass += 1
            for col, acc in (("ted", teds), ("ip", ips)):
                try: acc.append(float(r[col]))
                except: pass
        try: atts.append(float(r.get("att_seconds") or ""))
        except: pass
    n = len(uids)
    return {"rr": npass / n if n else 0, "pass": npass, "n": n,
            "ted": mean(teds) if teds else None,
            "ip": mean(ips) if ips else None,
            "att": mean(atts) if atts else None}

def refactory_att(pid):
    """Mean Refactory 'Total Time' per repaired wrong (seconds)."""
    p = os.path.join(REF_RAW, pid, "refactory_online.csv")
    if not os.path.exists(p):
        return None
    vals = []
    with open(p, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            try:
                vals.append(float(r.get("Total Time", "")))
            except: pass
    return mean(vals) if vals else None

def cell(m, att_override=None):
    if m is None:
        return f"{'--':>5} {'--':>6} {'--':>6} {'--':>7}"
    ted = f"{m['ted']:.1f}" if m['ted'] is not None else "--"
    ip = f"{m['ip']:+.2f}" if m['ip'] is not None else "--"
    att = att_override if att_override is not None else m['att']
    atts = f"{att:.2f}" if att is not None else "--"
    return f"{m['rr']*100:4.0f}% {ted:>6} {ip:>6} {atts:>7}"


def main():
    problems = DataLoader.run(os.path.join(ROOT, "data"))
    sample = {pid: sorted(trajs)[:50] for pid, _, _, trajs, _ in problems}
    sub = "  RR    TED     IP     ATT"
    hdr = f"{'problem':8} |{'Refactory':^28}|{'PaR (7b)':^28}"
    print(hdr)
    print(f"{'':8} |{sub:^28}|{sub:^28}")
    print("-" * len(hdr))
    agg = {"ref": [0, 0, [], [], []], "par": [0, 0, [], [], []]}
    for pid, _, _, trajs, _ in problems:
        uids = sample[pid]
        rm_ref = stats(read(os.path.join(REF, pid, "results.csv")), uids)
        rm_par = stats(read(os.path.join(PAR, pid, "results.csv")), uids)
        ratt = refactory_att(pid)
        print(f"{pid:8} | {cell(rm_ref, ratt)} | {cell(rm_par)}")
        for key, m, att in (("ref", rm_ref, ratt), ("par", rm_par, None)):
            if m:
                agg[key][0] += m["pass"]; agg[key][1] += m["n"]
                if m["ted"] is not None: agg[key][2].append(m["ted"])
                if m["ip"] is not None: agg[key][3].append(m["ip"])
                a = att if att is not None else m["att"]
                if a is not None: agg[key][4].append(a)
    print("-" * len(hdr))
    cells = []
    for key in ("ref", "par"):
        npass, n, teds, ips, atts = agg[key]
        cells.append(cell({"rr": npass / n if n else 0, "pass": npass, "n": n,
                           "ted": mean(teds) if teds else None,
                           "ip": mean(ips) if ips else None,
                           "att": mean(atts) if atts else None}))
    print(f"{'OVERALL':8} | {cells[0]} | {cells[1]}")
    print("\nRR=repaired/50, TED=mean tree-edit buggy->patch, IP=mean intent-pres.,")
    print("ATT=mean seconds/buggy (Refactory CPU 'Total Time'; PaR wall-clock, LLM on GPU).")
    print("OVERALL: RR pooled; TED/IP/ATT macro-averaged over problems with data.")
    print("p03240: Refactory timed out (>2h, combinatorial) -> no result.")


if __name__ == "__main__":
    main()
