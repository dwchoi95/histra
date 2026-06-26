"""Final comparison: original HISTRA vs HISTRA+coherent (our method) vs PaR vs
Refactory, on the shared 50-buggy sample per problem. Reads each tool's per-user
results.csv and reports RR, mean TED, mean IP over repaired cases.
"""
import os, sys, csv
from statistics import mean
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import warnings; warnings.filterwarnings("ignore")
from src.utils import DataLoader

COH = os.path.join(HERE, "results_methods_full", "coherent")
PAR = os.path.join(HERE, "par", "results_par")
REF = os.path.join(HERE, "refactory", "results_refactory")
HIS_50 = os.path.join(HERE, "results_histra_50")
HIS_MAIN = os.path.join(ROOT, "results")


def rows(path):
    if not os.path.exists(path):
        return None
    return {r["user_id"]: r for r in csv.DictReader(open(path, encoding="utf-8"))}

def metrics(rm, uids):
    if rm is None:
        return None
    npass, teds, ips = 0, [], []
    for u in uids:
        r = rm.get(u)
        if r and str(r.get("pass")) == "1":
            npass += 1
            try: teds.append(float(r["ted"]))
            except: pass
            try: ips.append(float(r["ip"]))
            except: pass
    n = len(uids)
    return {"rr": npass / n if n else 0, "pass": npass, "n": n,
            "ted": mean(teds) if teds else None, "ip": mean(ips) if ips else None}

def his_rows(pid):
    p = os.path.join(HIS_50, pid, "results.csv")
    return rows(p) if os.path.exists(p) else rows(os.path.join(HIS_MAIN, pid, "results.csv"))

def cell(m):
    if m is None:
        return f"{'--':>5} {'--':>5} {'--':>5}"
    ted = f"{m['ted']:.0f}" if m['ted'] is not None else "--"
    ip = f"{m['ip']:+.2f}" if m['ip'] is not None else "--"
    return f"{m['rr']*100:4.0f}% {ted:>5} {ip:>5}"


def main():
    problems = DataLoader.run(os.path.join(ROOT, "data"))
    sample = {pid: sorted(trajs)[:50] for pid, _, _, trajs, _ in problems}
    hdr = f"{'problem':8} | {'HISTRA+ (ours)':^17} | {'HISTRA orig':^17} | {'PaR(7b)':^17} | {'Refactory':^17}"
    print(hdr); print("-" * len(hdr))
    agg = {k: [[], [], 0, 0] for k in ("coh", "his", "par", "ref")}
    for pid, _, _, trajs, _ in problems:
        uids = sample[pid]
        ms = {"coh": metrics(rows(os.path.join(COH, pid, "results.csv")), uids),
              "his": metrics(his_rows(pid), uids),
              "par": metrics(rows(os.path.join(PAR, pid, "results.csv")), uids),
              "ref": metrics(rows(os.path.join(REF, pid, "results.csv")), uids)}
        print(f"{pid:8} | {cell(ms['coh'])} | {cell(ms['his'])} | {cell(ms['par'])} | {cell(ms['ref'])}")
        for k, m in ms.items():
            if m:
                agg[k][2] += m["pass"]; agg[k][3] += m["n"]
                if m["ted"] is not None: agg[k][0].append(m["ted"])
                if m["ip"] is not None: agg[k][1].append(m["ip"])
    print("-" * len(hdr))
    cells = []
    for k in ("coh", "his", "par", "ref"):
        teds, ips, npass, n = agg[k]
        cells.append(cell({"rr": npass / n if n else 0, "pass": npass, "n": n,
                           "ted": mean(teds) if teds else None,
                           "ip": mean(ips) if ips else None}))
    print(f"{'OVERALL':8} | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]}")
    print("\nEach cell: RR  TED  IP   (TED/IP over repaired; OVERALL macro-avg).")


if __name__ == "__main__":
    main()
