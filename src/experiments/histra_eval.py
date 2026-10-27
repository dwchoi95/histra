"""Run HISTRA, a variant without one design choice, or a control with other holes on the benchmark (RQ1, RQ3).
Usage: python run.py [PROBLEM ...] -m MODE   -> output/approaches/histra.jsonl (min) or output/ablation/<MODE>.jsonl
  min       HISTRA
  nostd     without normalization (HISTRA-Norm)      nohole   without the hole-only phase (HISTRA-Hole)
  nokept    without the Kept order (HISTRA-Kept)     plain    without minimization (HISTRA-Min)
  sizemin   minimization ordered by subtree size only (HISTRA_size)
  nohist    H = {}: no hole-only phase, no Kept order, size-ordered minimization (HISTRA_empty)
  randhole  random holes matched to the history's in number, kind, and size (HISTRA_rand); HSEED=0,1,2
  randfrac  random holes covering HFRAC (0.485) of the stmt/expr nodes (HISTRA_frac)
  fl        holes at the top Ochiai statements of b (HISTRA_FL); coverage is cached in FLCACHE"""
import ast
import json
import os
import random
import subprocess
import sys
import tempfile
import time
from multiprocessing import Pool

from common import APPROACHES, ONLY, POOL, cases, passes, path
from measure import metrics
from skel import naive_pair
from src.core.histra import HISTRA
from src.core.minimize import Minimizer
from src.core.repair import SHARED, Repair
from src.core.searcher import Searcher
from src.core.standardizer import Standardizer

MODES = ("min", "nostd", "nohole", "nokept", "plain", "sizemin", "nohist", "randhole", "randfrac", "fl")


def random_holes(pristine, holed, seed):
    """Per history hole root, a disjoint random subtree of the same kind (stmt/expr) and the closest size."""
    unit = lambda n: isinstance(n, (ast.stmt, ast.expr))
    us = [n for n in ast.walk(pristine) if unit(n)]
    parent = {id(ch): p for p in ast.walk(pristine) for ch in ast.iter_child_nodes(p)}
    size = {id(n): sum(1 for x in ast.walk(n) if unit(x)) for n in us}
    roots = sorted((n for n in us if id(n) in holed and id(parent.get(id(n))) not in holed), key=lambda n: -size[id(n)])
    rnd, out = random.Random(seed), set()
    for h in roots:
        kind = ast.stmt if isinstance(h, ast.stmt) else ast.expr
        free = [n for n in us if isinstance(n, kind) and not any(id(x) in out for x in ast.walk(n))
                and not any(id(a) in out for a in _ancestors(n, parent))]
        if not free:
            continue
        best = min(abs(size[id(n)] - size[id(h)]) for n in free)
        pick = rnd.choice([n for n in free if abs(size[id(n)] - size[id(h)]) == best])
        out |= {id(x) for x in ast.walk(pick) if not isinstance(x, SHARED)}
    return out


def fraction_holes(pristine, frac, seed):
    """History-free random holes: random disjoint subtrees covering at most `frac` of the stmt/expr nodes."""
    unit = lambda n: isinstance(n, (ast.stmt, ast.expr))
    us = [n for n in ast.walk(pristine) if unit(n)]
    left, out, rnd = round(frac * len(us)), set(), random.Random(seed)
    for n in rnd.sample(us, len(us)):
        sub = [x for x in ast.walk(n) if unit(x)]
        if id(n) in out or len(sub) > left:
            continue
        out |= {id(x) for x in ast.walk(n) if not isinstance(x, SHARED)}
        left -= len(sub)
    return out


# Line coverage of b, run like the validator; lines are written as they are hit, so a timed-out run keeps its coverage.
FL_TRACE = r"""import sys
src, cov = sys.argv[1], open(sys.argv[2], "a")
mon = sys.monitoring
def line(code, n):
    if code.co_filename == "<student>":
        cov.write(f"{n}\n"); cov.flush()
    return mon.DISABLE
mon.use_tool_id(mon.COVERAGE_ID, "histra-fl")
mon.register_callback(mon.COVERAGE_ID, mon.events.LINE, line)
mon.set_events(mon.COVERAGE_ID, mon.events.LINE)
del sys.argv[1:]
exec(compile(src, "<student>", "exec"), {"__name__": "__main__", "__builtins__": __builtins__})
"""


def spectrum(c):
    """[(passed, executed lines)] of b per test, judged as the validator does; cached per trajectory."""
    cache = os.path.join(os.environ.get("FLCACHE", os.path.join(tempfile.gettempdir(), "histra_fl")), f"{c['pid']}_{c['user']}.json")
    if os.path.exists(cache):
        return json.load(open(cache))
    out = []
    for t in c["tests"]:
        with tempfile.NamedTemporaryFile("r", suffix=".cov") as cov:
            try:
                p = subprocess.run([sys.executable, "-c", FL_TRACE, c["was"][-1], cov.name], input=t["input"], capture_output=True,
                                   text=True, timeout=c["timeout"])
                ok = p.returncode == 0 and " ".join(p.stdout.split()) == " ".join(t["output"].split())
            except subprocess.TimeoutExpired:
                ok = False
            out.append([ok, sorted({int(x) for x in open(cov.name).read().split()})])
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    json.dump(out, open(cache, "w"))
    return out


def fl_holes(pristine, spec):
    """Holes at the statements tied at the top Ochiai score (> 0); a compound statement's hole is its header only."""
    fail = [set(ls) for ok, ls in spec if not ok]
    pas = [set(ls) for ok, ls in spec if ok]
    unit = lambda n: isinstance(n, (ast.stmt, ast.expr))
    header = lambda ch: not isinstance(ch, (ast.stmt, ast.excepthandler, ast.match_case))
    def own(s):
        roots = [ch for ch in ast.iter_child_nodes(s) if header(ch)] if any(
            isinstance(ch, ast.stmt) for ch in ast.iter_child_nodes(s)) else [s]
        return [x for r in roots for x in ast.walk(r) if not isinstance(x, SHARED)]
    def ochiai(s):
        ef, ep = sum(s.lineno in f for f in fail), sum(s.lineno in p for p in pas)
        return ef / ((len(fail) * (ef + ep)) ** 0.5) if ef else 0.0
    stmts = [s for s in ast.walk(pristine) if isinstance(s, ast.stmt)
             and not isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    score = {id(s): ochiai(s) for s in stmts}
    ranked = sorted(stmts, key=lambda s: (-score[id(s)], s.lineno, s.col_offset))
    top = score[id(ranked[0])] if ranked else 0.0
    return {id(x) for s in ranked if top > 0 and score[id(s)] == top for x in own(s)}


def _ancestors(n, parent):
    while id(n) in parent:
        n = parent[id(n)]
        yield n


def run(args):
    c, mode = args
    t0 = time.time()
    try:
        traj = c["was"]
        std = [naive_pair(x) for x in traj] if mode == "nostd" else Standardizer.run(traj)
        skt, _, (pristine, holed) = HISTRA.sketch(std)
        if mode == "randhole":
            holed = random_holes(pristine, holed, f"{c['user']}:{os.environ.get('HSEED', '0')}")
        elif mode == "randfrac":
            holed = fraction_holes(pristine, float(os.environ.get("HFRAC", "0.485")), f"{c['user']}:frac")
        elif mode == "fl":
            holed = fl_holes(pristine, spectrum(c))
        rep = Repair(pristine, holed)
        if mode in ("sizemin", "nohist"):
            rep.minimizer = Minimizer(pristine, set())      # no holes -> every edit in one region, size order
        patch = None if skt is None else rep.run(
            traj[-1], Searcher(c["refs"]).run(traj[-1]), lambda s: passes(s, c["tests"], c["timeout"]),
            holes_first=mode not in ("nohole", "nohist"), kept_order=mode not in ("nokept", "nohist"), minimize=mode != "plain")
        units = [n for n in ast.walk(pristine) if isinstance(n, (ast.stmt, ast.expr))]
        info = dict(phase=getattr(rep, "phase", None) if patch else None, cover=sum(id(n) in holed for n in units),
                    frozen=sum(id(n) in rep.skeleton for n in units), units=len(units))
    except Exception:
        patch, info = None, {}
    return patch, time.time() - t0, info


def main(mode):
    assert mode in MODES, MODES
    name = "histra" if mode == "min" else mode + (os.environ.get("HSEED", "0") if mode == "randhole" else "")
    out, cs = path(name), cases()
    with Pool(POOL) as p:
        res = p.map(run, [(c, mode) for c in cs], chunksize=1)
        rows = [dict(pid=c["pid"], user=c["user"], was=c["was"], oracle=c["oracle"], patch=pt, sec=sec, **info)
                for c, (pt, sec, info) in zip(cs, res)]
        ms = p.starmap(metrics, [(r, name in APPROACHES) for r in rows], chunksize=2)
    new = [json.dumps({**r, **m}) + "\n" for r, m in zip(rows, ms)]
    # with ONLY, replace only those problems' rows
    old = [l for l in open(out) if json.loads(l)["pid"] not in ONLY.split(",")] if ONLY and os.path.exists(out) else []
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.writelines(sorted(old + new, key=lambda l: json.loads(l)["pid"]))
    print(f"{mode}: fixed {sum(p is not None for p, _, _ in res)}/{len(cs)} -> {out}")
