"""Share of HISTRA's passing patches that came from the hole-only phase (paper §3, Repair).
Usage: [PER=0] python phase_share.py HISTRA_PLAIN.jsonl [OUT.jsonl]   (OUT: per-case phase, read by summarize.py)"""
import os, sys, json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))); sys.path.insert(0, os.path.dirname(__file__))
from multiprocessing import Pool
from baselines import cases, POOL
from src.core.histra import HISTRA
from src.core.standardizer import Standardizer
from src.core.searcher import Searcher
from src.core.merge import MergeRepair
from src.core.repair import Repair

patch = {(r["pid"], r["user"]): r["patch"] for r in map(json.loads, open(sys.argv[1]))}

def one(c):
    p = patch[(c["pid"], c["user"])]
    if p is None: return None
    _, _, (pristine, holed) = HISTRA._sketch(Standardizer.run(c["was"]))
    rep, m = Repair(pristine, holed), MergeRepair()
    hole = {m._merge_patch(pristine, r, o, rep.skeleton) for o in (False, True) for r in Searcher(c["refs"]).run(c["was"][-1])}
    return (c["pid"], c["user"], p in hole)

if __name__ == "__main__":
    with Pool(POOL) as pool: res = [r for r in pool.map(one, cases(), chunksize=2) if r is not None]
    n = sum(h for _, _, h in res)
    print(f"hole-only phase: {n}/{len(res)} = {100*n/len(res):.1f}% of passing patches")
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w") as f:
            for pid, user, h in res:
                f.write(json.dumps(dict(pid=pid, user=user, phase="hole" if h else "free")) + "\n")
