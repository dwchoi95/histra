"""Rebuild results/overall.csv authoritatively from the per-problem
results/<pid>/<approach>.csv files (race-free; the per-problem CSVs are the
source of truth). Each overall row is:
  pid, approach, corrects, buggys, fixed, rr, ted, ip, att
where corrects == buggys == number of buggy users (every student has one AC, so
the AC-pool size equals the buggy count), ted/ip are means over fixed cases, and
att is the mean per-buggy time.
"""
import os, csv, glob
from statistics import mean

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
HEADER = ["pid", "approach", "corrects", "buggys", "fixed",
          "rr", "ted", "ip", "att"]
APPROACHES = ("histra", "histra_llm", "partraj", "refactory", "par")


def summarize(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    buggys = len(rows)
    fixed = sum(1 for r in rows if str(r.get("fixed")) == "1")
    teds, ips, atts = [], [], []
    for r in rows:
        try: atts.append(float(r.get("att") or ""))
        except: pass
        if str(r.get("fixed")) == "1":
            try: teds.append(float(r["ted"]))
            except: pass
            try: ips.append(float(r["ip"]))
            except: pass
    return {"corrects": buggys, "buggys": buggys, "fixed": fixed,
            "rr": fixed / buggys if buggys else 0.0,
            "ted": mean(teds) if teds else 0.0,
            "ip": mean(ips) if ips else 0.0,
            "att": mean(atts) if atts else 0.0}


def main():
    out = []
    for path in sorted(glob.glob(os.path.join(RESULTS, "*", "*.csv"))):
        approach = os.path.splitext(os.path.basename(path))[0]
        if approach not in APPROACHES:
            continue
        pid = os.path.basename(os.path.dirname(path))
        s = summarize(path)
        out.append([pid, approach, s["corrects"], s["buggys"], s["fixed"],
                    f"{s['rr']:.6f}", f"{s['ted']:.6f}", f"{s['ip']:.6f}",
                    f"{s['att']:.6f}"])
    out.sort(key=lambda r: (r[1], r[0]))
    with open(os.path.join(RESULTS, "overall.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        w.writerows(out)
    print(f"rebuilt overall.csv: {len(out)} rows from per-problem CSVs")


if __name__ == "__main__":
    main()
