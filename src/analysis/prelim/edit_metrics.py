"""Paper §4 (final review, C3): metrics that do not depend on HISTRA's own skeleton.
For each repairer's passing patches:
  ted     value-aware tree edit distance between P_n and the patch (how much the patch changes)
  growth  number of AST nodes the patch adds to P_n
  own     of the statement/expression nodes of P_n that the student's own accepted submission P_ac keeps
          (identical under the minimum-cost mapping), the fraction that the patch also keeps
  to_ac   value-aware tree edit distance between the patch and P_ac (how far the patch is from the student's own fix;
          independent of HISTRA's skeleton), and exact = the patch equals P_ac up to formatting
Usage: [POOL=n] python edit_metrics.py results/eval NAME ...   (writes results/eval/edit_metrics.json)"""
import ast, json, os, sys, statistics as st
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
from apted import APTED
from skel import _tree, _Cfg, units

D, NAMES = sys.argv[1], sys.argv[2:]


def kept_ids(anchor, src):
    """ids of anchor stmt/expr nodes mapped to an identical node of src, and the edit distance."""
    t = APTED(_tree(anchor), _tree(ast.parse(src)), _Cfg())
    keep = {id(a.node) for a, b in t.compute_edit_mapping() if a is not None and b is not None and a.name == b.name}
    return keep, t.compute_edit_distance()


def one(args):
    key, was, oracle, patches = args
    try:
        pn = ast.parse(was)
        us = {id(n) for n in units(pn)}
        own, _ = kept_ids(pn, oracle)
        own &= us
    except Exception:
        return key, {}
    out = {}
    for name, src in patches.items():
        try:
            keep, ted = kept_ids(pn, src)
            to_ac = APTED(_tree(ast.parse(src)), _tree(ast.parse(oracle)), _Cfg()).compute_edit_distance()
            out[name] = dict(ted=ted, growth=sum(1 for _ in ast.walk(ast.parse(src))) - sum(1 for _ in ast.walk(pn)),
                             own=len(keep & own) / len(own) if own else None, to_ac=to_ac,
                             exact=ast.dump(ast.parse(src)) == ast.dump(ast.parse(oracle)))
        except Exception:
            pass
    return key, out


if __name__ == "__main__":
    rows = {n: {(r["pid"], r["user"]): r for r in map(json.loads, open(f"{D}/{n}.jsonl"))} for n in NAMES}
    base = rows[NAMES[0]]
    jobs = [(k, base[k]["was"][-1], base[k]["oracle"], {n: rows[n][k]["patch"] for n in NAMES if rows[n][k]["patch"]})
            for k in base]
    jobs = jobs[:int(os.environ.get("LIMIT", len(jobs)))]
    with Pool(int(os.environ.get("POOL", 16))) as p:
        res = dict(p.map(one, jobs, chunksize=4))
    json.dump({f"{k[0]}/{k[1]}": v for k, v in res.items()}, open(f"{D}/{os.environ.get('OUTNAME', 'edit_metrics')}.json", "w"))
    for n in NAMES:
        vs = [v[n] for v in res.values() if n in v]
        own = [x["own"] for x in vs if x["own"] is not None]
        print(f"{n:18s} n={len(vs):5d} | TED mean {st.mean(x['ted'] for x in vs):6.1f} median {st.median(x['ted'] for x in vs):5.1f}"
              f" | growth {st.mean(x['growth'] for x in vs):+5.1f} | own-fix-kept {100*st.mean(own):5.1f}%"
              f" | TED to P_ac mean {st.mean(x['to_ac'] for x in vs):6.1f} median {st.median(x['to_ac'] for x in vs):5.1f}"
              f" | equal to P_ac {100*st.mean(x['exact'] for x in vs):4.1f}%")
    h = NAMES[NAMES.index("histra_min")] if "histra_min" in NAMES else None
    if h:
        for n in NAMES:
            if n == h: continue
            both = [v for v in res.values() if h in v and n in v]
            if not both: continue
            own = [(v[h]["own"], v[n]["own"]) for v in both if v[h]["own"] is not None and v[n]["own"] is not None]
            print(f"  paired vs {n:16s} n={len(both):5d} | TED {st.mean(v[h]['ted'] for v in both):6.1f} vs {st.mean(v[n]['ted'] for v in both):6.1f}"
                  f" | own-fix-kept {100*st.mean(a for a, _ in own):5.1f}% vs {100*st.mean(b for _, b in own):5.1f}%"
                  f" | TED to P_ac {st.mean(v[h]['to_ac'] for v in both):6.1f} vs {st.mean(v[n]['to_ac'] for v in both):6.1f}")
