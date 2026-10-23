"""Run HISTRA (or one ablated variant) on the baselines.py sample and store its patches.
Usage: [PER=0] [POOL=n] python histra_eval.py MODE OUT.jsonl [LIMIT]      (PER=0: full benchmark)
  min      full HISTRA: Standardize -> Sketch -> Search -> Repair (hole-only first, Kept order, Minimize)
  plain    without Minimize            nostd    without Standardize (sketch on the raw ASTs)
  nohole   without the hole-only phase  nokept   without Kept ordering (Search rank order)
  sizemin  Minimize ordered by subtree size only (history-agnostic)
  nohist   HISTRA with H = {}: no hole-only phase, no Kept order, size-ordered Minimize (the fair history-free control)
  randhole holes matched to the history's in number, kind, and size, at random places (is it the history, or any holes?)
           HSEED=k selects the k-th random draw (default 0)
  randfrac history-free random holes: random subtrees covering the same fraction HFRAC (default 0.485, the benchmark's
           mean hole share) of every program, regardless of its history
  fltop    history-free holes from spectrum-based fault localization (Ochiai over the tests' line coverage of P_n): the
           statements tied at the top suspiciousness, as a fault localizer reports them (cf. Orvalho et al., AAAI'25)
  flhole   the same ranking, filled up to as many stmt/expr nodes as the history holes cover (is it the history, or any
           fault localization?); both FL modes cache P_n's per-test spectrum in FLCACHE (default results/eval/fl_cov)
Each row also records the phase of the returned patch and the stmt/expr nodes inside holes (cover) and frozen."""
import ast, os, json, random, sys, time
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
from baselines import cases, V, POOL, PY
from skel import naive_pair
from src.core.histra import HISTRA
from src.core.standardizer import Standardizer
from src.core.searcher import Searcher
from src.core.repair import Repair
from src.core.minimize import Minimizer

MODES = ("min", "plain", "nostd", "nohole", "nokept", "sizemin", "nohist", "randhole", "randfrac", "flhole", "fltop")
SHARED = (ast.expr_context, ast.boolop, ast.operator, ast.unaryop, ast.cmpop)   # tree-wide singletons, never holed


def random_holes(pristine, holed, seed):
    """Random holes matched to the history's (final review J7): one random root per history hole root, of the same
    kind (statement or expression) and the closest subtree size, pairwise disjoint; seeded per trajectory."""
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


# Runs P_n like V.verify (python -c), recording each executed line once (sys.monitoring, then DISABLE: near full speed);
# lines go to a file as they are hit, so a timed-out run keeps its coverage.
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
    """[(passed, executed lines)] of P_n per test, passed judged as V.verify does (same timeout); cached per trajectory."""
    import subprocess, tempfile
    path = os.path.join(os.environ.get("FLCACHE", "results/eval/fl_cov"), f"{c['pid']}_{c['user']}.json")
    if os.path.exists(path):
        return json.load(open(path))
    out = []
    for t in c["tests"]:
        with tempfile.NamedTemporaryFile("r", suffix=".cov") as cov:
            try:
                p = subprocess.run([PY, "-c", FL_TRACE, c["was"][-1], cov.name], input=t["input"], capture_output=True,
                                   text=True, timeout=c["timeout"])
                ok = p.returncode == 0 and " ".join(p.stdout.split()) == " ".join(t["output"].split())
            except subprocess.TimeoutExpired:
                ok = False
            out.append([ok, sorted({int(x) for x in open(cov.name).read().split()})])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(out, open(path, "w"))
    return out


def fl_holes(pristine, spec, budget=None):
    """History-free holes at the statements that Ochiai ranks most suspicious. A statement's hole is its subtree, or for a
    compound statement its header (test, target, iter, ...; the body stays outside). budget=None: the statements tied at
    the top score (> 0); budget=k: statements in rank order (ties by line) until they cover k stmt/expr nodes (the last
    one may overshoot, so the most suspicious statement is never skipped)."""
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
    if budget is None:
        top = score[id(ranked[0])] if ranked else 0.0
        return {id(x) for s in ranked if top > 0 and score[id(s)] == top for x in own(s)}
    out, left = set(), budget
    for s in ranked:
        if left <= 0:
            break
        new = [x for x in own(s) if id(x) not in out]
        out |= {id(x) for x in new}
        left -= sum(1 for x in new if unit(x))
    return out


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
        skt, _, (pristine, holed) = HISTRA._sketch(std)
        if mode == "randhole":
            holed = random_holes(pristine, holed, f"{c['user']}:{os.environ.get('HSEED', '0')}")
        elif mode == "randfrac":
            holed = fraction_holes(pristine, float(os.environ.get("HFRAC", "0.485")), f"{c['user']}:frac")
        elif mode in ("flhole", "fltop"):
            budget = sum(id(n) in holed for n in ast.walk(pristine) if isinstance(n, (ast.stmt, ast.expr)))
            holed = fl_holes(pristine, spectrum(c), budget if mode == "flhole" else None)
        rep = Repair(pristine, holed)
        if mode in ("sizemin", "nohist"):
            rep.minimizer = Minimizer(pristine, set())      # no holes -> every edit in one region, size order
        patch = None if skt is None else rep.run(
            traj[-1], Searcher(c["refs"]).run(traj[-1]), lambda s: V.verify(s, c["tests"], c["timeout"]).passed,
            holes_first=mode not in ("nohole", "nohist"), kept_order=mode not in ("nokept", "nohist"), minimize=mode != "plain")
        units = [n for n in ast.walk(pristine) if isinstance(n, (ast.stmt, ast.expr))]
        info = dict(phase=getattr(rep, "phase", None) if patch else None, cover=sum(id(n) in holed for n in units),
                    frozen=sum(id(n) in rep.skeleton for n in units), units=len(units))
    except Exception:
        patch, info = None, {}
    return patch, time.time() - t0, info


if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    assert mode in MODES, MODES
    cs = cases()[: int(sys.argv[3])] if len(sys.argv) > 3 else cases()
    with Pool(POOL) as p:
        res = p.map(run, [(c, mode) for c in cs], chunksize=1)
    with open(out, "w") as f:
        for c, (pt, sec, info) in zip(cs, res):
            f.write(json.dumps(dict(pid=c["pid"], user=c["user"], was=c["was"], oracle=c["oracle"], patch=pt, sec=sec, **info)) + "\n")
    secs = [s for _, s, _ in res]
    print(mode, f"passed {sum(p is not None for p, _, _ in res)}/{len(cs)} | hole-only {sum(i.get('phase') == 'hole' for *_, i in res)}"
          f" | mean {sum(secs)/len(secs):.1f}s median {sorted(secs)[len(secs)//2]:.1f}s max {max(secs):.1f}s")
