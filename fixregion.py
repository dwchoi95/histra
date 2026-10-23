"""How coarsely the history marks where to repair (Section II-B). Over every trajectory, N = stmt/expr nodes of b,
H = nodes inside holes, F = nodes that the student's own accepted fix does not keep (value-aware APTED mapping).
Usage: [POOL=16] python paper/fixregion.py"""
import ast
import glob
import json
import os
import sys
from multiprocessing import Pool

from apted import APTED

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "experiments"))   # this folder is histra/paper/
from common import DATA, POOL  # noqa: E402
from skel import _Cfg, _tree, holed_ids, units  # noqa: E402


def one(t):
    was = [s["code"] for s in t["submissions"] if s["verdict"] != "Accepted"]
    try:
        org, holed = holed_ids(was)
        mp = APTED(_tree(org), _tree(ast.parse(t["submissions"][-1]["code"])), _Cfg()).compute_edit_mapping()
    except Exception:
        return None
    kept = {id(a.node) for a, b in mp if a is not None and b is not None and a.name == b.name}
    us = units(org)
    H = {id(n) for n in us if id(n) in holed}
    F = {id(n) for n in us if id(n) not in kept}
    return len(us), len(H), len(F), len(H & F)


if __name__ == "__main__":
    ts = [json.loads(l) for f in sorted(glob.glob(os.path.join(DATA, "p*", "trajectories.jsonl"))) for l in open(f)]
    with Pool(POOL) as p:
        rs = [r for r in p.map(one, ts, chunksize=8) if r]
    N, H, F, HF = (sum(r[i] for r in rs) for i in range(4))
    print(f"trajectories {len(rs)}/{len(ts)}")
    print(f"code outside the skeleton (holes) |H|/|N| {100 * H / N:.1f}%")
    print(f"the student's fix changes {100 * HF / H:.1f}% of the code outside the skeleton and "
          f"{100 * (F - HF) / (N - H):.1f}% of the skeleton")
    print(f"share of the nodes that the fix changes that lie outside the skeleton |F&H|/|F| {100 * HF / F:.1f}%")
