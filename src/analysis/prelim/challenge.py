"""Y/Z: share of the last WA's stmt/expr nodes marked changed without standardization, and the
share of those that standardization turns back into skeleton (surface-only differences)."""
import json, glob, os, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
from skel import holed_ids, units


def one(was):
    try:
        org_n, hn = holed_ids(was, standardize=False)
        org_s, hs = holed_ids(was, standardize=True)
    except Exception as e:
        return None
    un, us = units(org_n), units(org_s)
    # align the two parses of the same anchor by walk order (identical source -> identical order)
    cn = {i for i, n in enumerate(un) if id(n) in hn}
    cs = {i for i, n in enumerate(us) if id(n) in hs}
    return len(un), len(cn), len(cn - cs), len(cs)


if __name__ == "__main__":
    jobs = []
    for f in sorted(glob.glob(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")) + "/p*/trajectories.jsonl")):
        for ln in open(f, encoding="utf-8"):
            t = json.loads(ln)
            jobs.append([s["code"] for s in t["submissions"] if s["verdict"] != "Accepted"])
    with Pool(18) as p:
        res = p.map(one, jobs, chunksize=8)
    ok = [r for r in res if r]
    N = sum(r[0] for r in ok); CN = sum(r[1] for r in ok); SURF = sum(r[2] for r in ok); CS = sum(r[3] for r in ok)
    per_y = [r[1] / r[0] for r in ok if r[0]]
    per_z = [r[2] / r[1] for r in ok if r[1]]
    print(f"trajectories {len(ok)}/{len(jobs)} | nodes {N}")
    print(f"naive changed (pooled) {CN/N:.1%} | mean per-traj {sum(per_y)/len(per_y):.1%}")
    print(f"surface-only among naive-changed (pooled) {SURF/CN:.1%} | mean per-traj {sum(per_z)/len(per_z):.1%}")
    print(f"standardized changed (pooled) {CS/N:.1%}")
    print(f"skeleton share after standardization (pooled) {1-CS/N:.1%}")
