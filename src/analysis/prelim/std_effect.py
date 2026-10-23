"""Paper §4 RQ2: on how many trajectories does Standardize change the intent skeleton, and what is the skeleton
loss of HISTRA vs HISTRA-Std there?  Usage: [PER=0] [POOL=n] python std_effect.py results/eval"""
import json, os, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
from baselines import cases, POOL
from skel import holed_ids, units


def skel_sig(was, standardize):
    org, holed = holed_ids(was, standardize=standardize)
    return [i for i, n in enumerate(units(org)) if id(n) not in holed]


def one(c):
    try:
        return (c["pid"], c["user"]), skel_sig(c["was"], True) != skel_sig(c["was"], False)
    except Exception:
        return (c["pid"], c["user"]), None


if __name__ == "__main__":
    D = sys.argv[1]
    with Pool(POOL) as p:
        diff = dict(p.map(one, cases(), chunksize=4))
    changed = {k for k, v in diff.items() if v}
    print(f"skeleton changed by Standardize: {len(changed)}/{len(diff)} = {100*len(changed)/len(diff):.1f}%")
    for m in ("histra_min", "histra_nostd"):
        r = {(x["pid"], x["user"]): x for x in map(json.loads, open(f"{D}/{m}.ret.jsonl")) if x}
        xs = [r[k]["ret_patch"] for k in changed if k in r and r[k]["passed"] and r[k]["ret_patch"] is not None]
        print(f"{m} on those: passing {len(xs)} | loss {100*(1-sum(xs)/len(xs)):.1f}%")
