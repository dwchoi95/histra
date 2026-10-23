"""Metrics of every row, added in place: skeleton share and loss (Section II-B, RQ1, RQ3); for HISTRA and the baselines
also Kept and Dist (RQ2). Usage: [POOL=16] python src/experiments/measure.py output/<group>/<name>.jsonl ..."""
import ast
import json
import os
import sys
from multiprocessing import Pool

from apted import APTED

from common import APPROACHES, POOL
from skel import _Cfg, _tree, holed_ids, retention, units


def kept_ids(anchor, src):
    """ids of the anchor's nodes mapped to an identical node of src."""
    t = APTED(_tree(anchor), _tree(ast.parse(src)), _Cfg())
    return {id(a.node) for a, b in t.compute_edit_mapping() if a is not None and b is not None and a.name == b.name}


def metrics(row, edit):
    """skel_share, ret_patch, ret_oracle (shares of b's stmt/expr nodes in the skeleton and of the skeleton kept), and
    with edit, kept (of the nodes of b that the student's fix keeps, the share the patch keeps) and dist (TED to it)."""
    m = dict(skel_share=None, ret_patch=None, ret_oracle=None)
    try:
        org, holed = holed_ids(row["was"])
    except Exception:
        org = None
    if org is not None:
        us = units(org)
        m.update(skel_share=sum(id(n) not in holed for n in us) / len(us) if us else None,
                 ret_patch=retention(org, holed, row["patch"])[0] if row["patch"] else None,
                 ret_oracle=retention(org, holed, row["oracle"])[0])
    if edit:
        m.update(kept=None, dist=None)
        try:
            if row["patch"]:
                b = ast.parse(row["was"][-1])
                own = kept_ids(b, row["oracle"]) & {id(n) for n in units(b)}
                m.update(kept=len(kept_ids(b, row["patch"]) & own) / len(own) if own else None,
                         dist=APTED(_tree(ast.parse(row["patch"])), _tree(ast.parse(row["oracle"])), _Cfg()).compute_edit_distance())
        except Exception:
            pass
    return m


def measure(f):
    rows = [json.loads(l) for l in open(f)]
    edit = os.path.basename(f).removesuffix(".jsonl") in APPROACHES
    with Pool(POOL) as p:
        ms = p.starmap(metrics, [(r, edit) for r in rows], chunksize=2)
    rows = [{**r, **m} for r, m in zip(rows, ms)]
    with open(f, "w") as g:
        g.writelines(json.dumps(r) + "\n" for r in rows)
    ok = [r for r in rows if r["patch"] and r["ret_patch"] is not None]
    print(f"{f}: fixed {sum(bool(r['patch']) for r in rows)}/{len(rows)} | "
          f"skeleton loss {100 * (1 - sum(r['ret_patch'] for r in ok) / max(len(ok), 1)):.1f}%")


if __name__ == "__main__":
    for f in sys.argv[1:]:
        measure(f)
