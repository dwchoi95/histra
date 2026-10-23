"""Skeleton retention of passing patches (and of the student's own accepted fix) per repairer.
Usage: python measure.py merge.jsonl llm.jsonl ...   -> per-file + per-problem summary, writes *.ret.jsonl"""
import json, sys, os
from collections import defaultdict
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
from skel import holed_ids, retention, units


def one(row):
    try:
        org, holed = holed_ids(row["was"], standardize=True)
    except Exception:
        return None
    nunits = len(units(org))
    skel = nunits - sum(1 for n in units(org) if id(n) in holed)
    rp = retention(org, holed, row["patch"])[0] if row["patch"] else None
    ro = retention(org, holed, row["oracle"])[0]
    return dict(pid=row["pid"], user=row["user"], passed=row["patch"] is not None,
                skel_share=skel / nunits if nunits else None, ret_patch=rp, ret_oracle=ro)


def summarize(name, rs):
    rs = [r for r in rs if r]
    passed = [r for r in rs if r["passed"] and r["ret_patch"] is not None]
    mod = [r for r in passed if r["ret_patch"] < 1.0]
    orc = [r for r in rs if r["ret_oracle"] is not None]
    print(f"[{name}] n={len(rs)} RR={sum(r['passed'] for r in rs)/len(rs):.1%} | "
          f"passing patches modifying skeleton {len(mod)}/{len(passed)}={len(mod)/max(len(passed),1):.1%} "
          f"| mean skeleton retention {sum(r['ret_patch'] for r in passed)/max(len(passed),1):.1%}")
    om = [r for r in orc if r["ret_oracle"] < 1.0]
    print(f"   student's own AC modifies skeleton {len(om)}/{len(orc)}={len(om)/max(len(orc),1):.1%} "
          f"| mean retention {sum(r['ret_oracle'] for r in orc)/max(len(orc),1):.1%} "
          f"| skeleton share of WA_n {sum(r['skel_share'] for r in rs if r['skel_share'] is not None)/len(rs):.1%}")
    per = defaultdict(list)
    for r in rs: per[r["pid"]].append(r)
    for pid, xs in sorted(per.items()):
        pp = [r for r in xs if r["passed"] and r["ret_patch"] is not None]
        m = sum(r["ret_patch"] < 1.0 for r in pp)
        o = sum(r["ret_oracle"] is not None and r["ret_oracle"] < 1.0 for r in xs)
        print(f"   {pid} RR {sum(r['passed'] for r in xs)}/{len(xs)}  modify {m}/{len(pp)}  own-AC modify {o}/{len(xs)}")


if __name__ == "__main__":
    for f in sys.argv[1:]:
        rows = [json.loads(l) for l in open(f)]
        with Pool(int(os.environ.get("POOL", 18))) as p:
            rs = p.map(one, rows, chunksize=2)
        with open(f.replace(".jsonl", ".ret.jsonl"), "w") as g:
            for r in rs: g.write(json.dumps(r) + "\n")
        summarize(os.path.basename(f), rs)
