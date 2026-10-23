"""Does the student's own history localize the bug?  For each trajectory (all of data/):
  N = stmt/expr nodes of WA_n, H = nodes inside holes (Sketch+Reformat), F = nodes the student's own
  accepted fix does not keep (value-aware APTED mapping WA_n -> AC).  Reports |H|/|N|, |F|/|N|,
  recall |F∩H|/|F| and precision |F∩H|/|H| (pooled and per-trajectory means)."""
import json, glob, os, sys, ast
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
from skel import holed_ids, units, _tree, _Cfg
from apted import APTED


def one(t):
    was = [s["code"] for s in t["submissions"] if s["verdict"] != "Accepted"]
    ac = t["submissions"][-1]["code"]
    try:
        org, holed = holed_ids(was, standardize=True)
        mp = APTED(_tree(org), _tree(ast.parse(ac)), _Cfg()).compute_edit_mapping()
    except Exception:
        return None
    kept = {id(a.node) for a, b in mp if a is not None and b is not None and a.name == b.name}
    U = units(org)
    H = {id(n) for n in U if id(n) in holed}
    F = {id(n) for n in U if id(n) not in kept}
    # kinds of the student's fix: the topmost changed stmt/expr nodes (no changed stmt/expr ancestor)
    uid = {id(n) for n in U}
    parent = {id(c): p for p in ast.walk(org) for c in ast.iter_child_nodes(p)}
    def unit_parent(n):
        p = parent.get(id(n))
        while p is not None and id(p) not in uid:
            p = parent.get(id(p))
        return p
    top = [n for n in U if id(n) in F and (unit_parent(n) is None or id(unit_parent(n)) not in F)]
    return len(U), len(H), len(F), len(H & F), [("stmt" if isinstance(n, ast.stmt) else "expr", type(n).__name__) for n in top]


if __name__ == "__main__":
    ts = [json.loads(l) for f in sorted(glob.glob(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")) + "/p*/trajectories.jsonl")) for l in open(f)]
    with Pool(18) as p:
        rs = [r for r in p.map(one, ts, chunksize=8) if r]
    N, H, F, HF = (sum(r[i] for r in rs) for i in range(4))
    rec = [r[3] / r[2] for r in rs if r[2]]; pre = [r[3] / r[1] for r in rs if r[1]]
    print(f"trajectories {len(rs)}/{len(ts)}")
    print(f"hole share |H|/|N| {H/N:.1%} | fix share |F|/|N| {F/N:.1%}")
    print(f"recall |F∩H|/|F| pooled {HF/F:.1%} mean {sum(rec)/len(rec):.1%} | precision |F∩H|/|H| pooled {HF/H:.1%} mean {sum(pre)/len(pre):.1%}")
    print(f"changed by the fix: skeleton nodes |F-H|/|N-H| {(F-HF)/(N-H):.1%} | other nodes |F∩H|/|H| {HF/H:.1%}")
    kinds = [r[4] for r in rs]
    only_expr = sum(bool(k) and all(c == "expr" for c, _ in k) for k in kinds)
    print(f"student fixes: changing only expressions inside kept statements {only_expr/len(rs):.1%} | changing statements "
          f"{sum(any(c == 'stmt' for c, _ in k) for k in kinds)/len(rs):.1%} | only inserting code {sum(not k for k in kinds)/len(rs):.1%}")
    group = {"Constant": "constant", "Compare": "condition", "BoolOp": "condition", "BinOp": "arithmetic",
             "UnaryOp": "arithmetic", "Call": "call", "Name": "variable", "Attribute": "variable", "Subscript": "variable"}
    from collections import Counter
    ex = Counter(group.get(t, "other expression") for k in kinds for c, t in k if c == "expr")
    st = Counter(t for k in kinds for c, t in k if c == "stmt")
    tot = sum(ex.values())
    print("topmost changed expressions: " + ", ".join(f"{g} {v/tot:.1%}" for g, v in ex.most_common()))
    print("topmost changed statements: " + ", ".join(f"{g} {v}" for g, v in st.most_common(8)))
    print(f"no-hole trajectories {sum(r[1]==0 for r in rs)} | fix entirely inside holes {sum(r[2] and r[3]==r[2] for r in rs)} | fix entirely outside holes {sum(r[2] and r[3]==0 for r in rs)}")
