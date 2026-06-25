"""Experiment harness for HISTRA improvement methods.

All methods keep standardize/sketch/reformat + the trajectory concept unchanged;
they differ only in how search -> repair -> validate is performed. Each run
appends a row to baselines/METHODS.md so we can track which method is best.

Usage:
  python baselines/exp.py --method beam --problems p02694 p02659 -n 30 [-k 4]
"""
import os, sys, ast, copy, time, csv, json, argparse, itertools
from statistics import mean
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warnings; warnings.filterwarnings("ignore")

from src.utils import DataLoader
from src.core.standardizer import Standardizer
from src.core.sketch import Sketcher
from src.core.reformat import Reformatter
from src.core.searcher import Searcher, NConfig
from apted import APTED
from src.core.repair import Repair
from src.core.validator import Validator
from src.utils import metrics as _metrics
from baselines.histra_loop import (is_hole, n_holes, hole_nodes, parent_map,
                                    enclosing_stmt, replace_node, repair_loop)

HERE = os.path.dirname(os.path.abspath(__file__))


# ----------------------------------------------------------------- shared
def sketch_of(traj):
    std = Standardizer.run(traj)
    anchor = std[-1]
    skt = Sketcher.run(std)
    return Reformatter.run(anchor, skt), anchor

def maximal_hole_stmts(tree):
    pm = parent_map(tree)
    out = []
    for s in [n for n in ast.walk(tree) if isinstance(n, ast.stmt)]:
        if any(is_hole(x) for x in ast.walk(s)):
            p = enclosing_stmt(pm.get(id(s)), pm)
            if p is None or not any(is_hole(x) for x in ast.walk(p)):
                out.append(s)
    return out

def topk_same_type(node, sch, k):
    cands = [r for roots in sch.ref_roots_list for r in roots if type(r) is type(node)]
    scored = []
    for r in cands:
        try:
            scored.append((sch._apted_dist(node, r), r))
        except Exception:
            pass
    scored.sort(key=lambda x: x[0])
    seen, out = set(), []
    for _, r in scored:
        key = ast.dump(r)
        if key in seen:
            continue
        seen.add(key); out.append(r)
        if len(out) >= k:
            break
    return out

def topk_modules(cur, refs_src, sch, k):
    scored = []
    for code in refs_src:
        try:
            r = ast.parse(code)
            vm = sch._varmap_defuse(cur, r)
            r = sch._rename_vars(r, vm)
            scored.append((sch._apted_dist(cur, r), r))
        except Exception:
            pass
    scored.sort(key=lambda x: x[0])
    return [r for _, r in scored[:k]]


# ----------------------------------------------------------------- methods
def solve_loop(traj, refpool, **kw):
    return repair_loop(traj, refpool, restarts=kw.get("restarts", 1))


def _build_parent_slot(tree):
    ps = {}
    for p in ast.walk(tree):
        for field, val in ast.iter_fields(p):
            if isinstance(val, list):
                for i, it in enumerate(val):
                    if isinstance(it, ast.AST):
                        ps[id(it)] = (p, field, i)
            elif isinstance(val, ast.AST):
                ps[id(val)] = (p, field, None)
    return ps

def _set_node(ps, node, repl):
    p, field, i = ps[id(node)]
    if i is None:
        setattr(p, field, repl)
    else:
        getattr(p, field)[i] = repl


def _plan_units(skt_org, sch, refpool, k, allow_module):
    """Each maximal hole-statement -> (walk_index in skt_org, [donor candidates]).
    No same-type donor -> escalate to nearest ancestor stmt that has one; if none
    up to the module, optionally use nearest whole-program donors (walk_index 0)."""
    walk_idx = {id(n): i for i, n in enumerate(ast.walk(skt_org))}
    pm = parent_map(skt_org)
    plan = {}
    for u in maximal_hole_stmts(skt_org):
        node = u
        donors = topk_same_type(node, sch, k)
        while not donors:
            parent = enclosing_stmt(pm.get(id(node)), pm)
            if parent is None:
                if allow_module:
                    plan[0] = topk_modules(skt_org, refpool, sch, k)  # root
                node = None
                break
            node = parent
            donors = topk_same_type(node, sch, k)
        if node is not None and donors:
            plan[walk_idx[id(node)]] = donors
    return plan


def solve_beam(traj, refpool, k=4, budget=80, allow_module=False, **kw):
    skt_org, anchor = sketch_of(traj)
    if n_holes(skt_org) == 0:
        return None
    sch = Searcher(refpool, anchor)
    plan = _plan_units(skt_org, sch, refpool, k, allow_module)
    if not plan or any(len(v) == 0 for v in plan.values()):
        return None
    items = list(plan.items())                       # [(walk_idx, donors)]
    ranges = [range(len(donors)) for _, donors in items]
    # nearest-first: combinations ordered by total donor rank (-> minimal edit)
    combos = sorted(itertools.product(*ranges), key=lambda c: sum(c))
    best, best_ted = None, float("inf")
    for ci, combo in enumerate(combos):
        if ci >= budget:
            break
        cur = copy.deepcopy(skt_org)
        nodes = list(ast.walk(cur))
        ps = _build_parent_slot(cur)
        root_replaced = False
        for (widx, donors), idx in zip(items, combo):
            if widx == 0:                            # whole-program donor
                cur = copy.deepcopy(donors[idx]); root_replaced = True; break
            tgt = nodes[widx]
            if id(tgt) in ps:
                _set_node(ps, tgt, copy.deepcopy(donors[idx]))
        ast.fix_missing_locations(cur)
        if n_holes(cur) != 0:
            continue
        try:
            patch = ast.unparse(cur)
        except Exception:
            continue
        try:
            ok = Validator.run(patch).passed()
        except Exception:
            ok = False
        if ok:
            t = _metrics.ted(traj[-1], patch) or 0
            if t < best_ted:
                best_ted, best = t, patch
            break                                    # nearest-first => first pass is good
    return best


def solve_beam_fb(traj, refpool, k=4, budget=80, **kw):
    """beam, then if nothing passes fall back to nearest whole-program donor."""
    p = solve_beam(traj, refpool, k=k, budget=budget, allow_module=True)
    if p is not None:
        return p
    # last resort: nearest AC that passes (guarantees RR but low IP)
    skt_org, anchor = sketch_of(traj)
    sch = Searcher(refpool, anchor)
    for r in topk_modules(skt_org, refpool, sch, 5):
        try:
            patch = ast.unparse(r)
            if Validator.run(patch).passed():
                return patch
        except Exception:
            continue
    return None


# ---------------- M3: expression-level fill (keep student's stmt structure) ----
def _node_path(root, target):
    """Path [(field, index_or_None), ...] from root to target node, or None."""
    if root is target:
        return []
    for field, val in ast.iter_fields(root):
        if isinstance(val, ast.AST):
            p = _node_path(val, target)
            if p is not None:
                return [(field, None)] + p
        elif isinstance(val, list):
            for i, it in enumerate(val):
                if isinstance(it, ast.AST):
                    p = _node_path(it, target)
                    if p is not None:
                        return [(field, i)] + p
    return None

def _get_path(root, path):
    cur = root
    for field, i in path:
        v = getattr(cur, field, None)
        if i is None:
            if not isinstance(v, ast.AST):
                return None
            cur = v
        else:
            if not isinstance(v, list) or i >= len(v) or not isinstance(v[i], ast.AST):
                return None
            cur = v[i]
    return cur

def _set_path(root, path, repl):
    if not path:
        return repl
    parent = _get_path(root, path[:-1])
    field, i = path[-1]
    if i is None:
        setattr(parent, field, repl)
    else:
        getattr(parent, field)[i] = repl
    return root


def fill_stmt_expr(S, D, sch):
    """Deepcopy of statement S with each hole replaced by the donor D node at the
    SAME structural path (the aligned subexpression). None if D's structure does
    not reach a hole's path (then this donor cannot expr-fill S)."""
    holes_S = [n for n in ast.walk(S) if is_hole(n)]
    if not holes_S:
        return None
    fills = []                                       # (path, donor node)
    for h in holes_S:
        path = _node_path(S, h)
        if path is None:
            return None
        dn = _get_path(D, path)
        if dn is None or is_hole(dn):
            return None
        fills.append((path, dn))
    Sc = copy.deepcopy(S)
    for path, dn in fills:
        Sc = _set_path(Sc, path, copy.deepcopy(dn))
    ast.fix_missing_locations(Sc)
    return Sc


def solve_exprfill(traj, refpool, k=6, budget=80, **kw):
    skt_org, anchor = sketch_of(traj)
    if n_holes(skt_org) == 0:
        return None
    sch = Searcher(refpool, anchor)
    walk_idx = {id(n): i for i, n in enumerate(ast.walk(skt_org))}
    units = maximal_hole_stmts(skt_org)
    if not units:
        return None
    plan = []                                        # [(walk_idx, [filled stmt candidates])]
    for S in units:
        donors = topk_same_type(S, sch, k)
        cands = []
        seen = set()
        for D in donors:
            filled = fill_stmt_expr(S, D, sch)
            if filled is None:
                continue
            try:
                key = ast.dump(filled)
            except Exception:
                continue
            if key in seen:
                continue
            seen.add(key); cands.append(filled)
        if not cands:
            return None                              # this unit can't be expr-filled
        plan.append((walk_idx[id(S)], cands))
    ranges = [range(len(c)) for _, c in plan]
    combos = sorted(itertools.product(*ranges), key=lambda c: sum(c))
    best, best_ted = None, float("inf")
    for ci, combo in enumerate(combos):
        if ci >= budget:
            break
        cur = copy.deepcopy(skt_org)
        nodes = list(ast.walk(cur))
        ps = _build_parent_slot(cur)
        for (widx, cands), idx in zip(plan, combo):
            tgt = nodes[widx]
            if id(tgt) in ps:
                _set_node(ps, tgt, copy.deepcopy(cands[idx]))
        ast.fix_missing_locations(cur)
        if n_holes(cur) != 0:
            continue
        try:
            patch = ast.unparse(cur)
        except Exception:
            continue
        try:
            ok = Validator.run(patch).passed()
        except Exception:
            ok = False
        if ok:
            t = _metrics.ted(traj[-1], patch) or 0
            if t < best_ted:
                best_ted, best = t, patch
            break
    return best


# ---------------- M4: donor coherence (fill all holes from ONE donor program) --
def solve_coherent(traj, refpool, k=4, budget=40, **kw):
    """For each donor PROGRAM, fill every hole-statement from that one program's
    aligned statements, so the fills compose. Programs ranked by total alignment
    distance to the student's hole-statements; validate nearest-first."""
    skt_org, anchor = sketch_of(traj)
    if n_holes(skt_org) == 0:
        return None
    sch = Searcher(refpool, anchor)
    walk_idx = {id(n): i for i, n in enumerate(ast.walk(skt_org))}
    units = maximal_hole_stmts(skt_org)
    if not units:
        return None
    unit_idx = [walk_idx[id(S)] for S in units]
    plans = []                                       # (total_dist, [chosen stmt per unit])
    for prog_stmts in sch.ref_roots_list:
        chosen, total, ok = [], 0, True
        for S in units:
            cands = [r for r in prog_stmts if type(r) is type(S)]
            if not cands:
                ok = False; break
            d_best, r_best = float("inf"), None
            for r in cands:
                try:
                    d = sch._apted_dist(S, r)
                except Exception:
                    continue
                if d < d_best:
                    d_best, r_best = d, r
            if r_best is None:
                ok = False; break
            chosen.append(r_best); total += d_best
        if ok:
            plans.append((total, chosen))
    plans.sort(key=lambda x: x[0])
    best, best_ted = None, float("inf")
    for ci, (total, chosen) in enumerate(plans[:budget]):
        cur = copy.deepcopy(skt_org)
        nodes = list(ast.walk(cur))
        ps = _build_parent_slot(cur)
        for widx, st in zip(unit_idx, chosen):
            tgt = nodes[widx]
            if id(tgt) in ps:
                _set_node(ps, tgt, copy.deepcopy(st))
        ast.fix_missing_locations(cur)
        if n_holes(cur) != 0:
            continue
        try:
            patch = ast.unparse(cur)
        except Exception:
            continue
        try:
            ok = Validator.run(patch).passed()
        except Exception:
            ok = False
        if ok:
            t = _metrics.ted(traj[-1], patch) or 0
            if t < best_ted:
                best_ted, best = t, patch
            break
    return best


# ---------------- cascade: try expr-fill (best IP) -> beam -> coherent ----------
def solve_cascade(traj, refpool, k=4, budget=80, **kw):
    for fn in (solve_exprfill,
               lambda t, r, **kw: solve_beam(t, r, allow_module=False, **kw),
               solve_coherent):
        try:
            p = fn(traj, refpool, k=k, budget=budget)
        except Exception:
            p = None
        if p is not None:
            return p
    return None


METHODS = {
    "loop": solve_loop,
    "beam": lambda traj, refpool, **kw: solve_beam(traj, refpool, allow_module=False, **kw),
    "beam_fb": solve_beam_fb,
    "exprfill": solve_exprfill,
    "coherent": solve_coherent,
    "cascade": solve_cascade,
}


# ----------------------------------------------------------------- eval
def run(method, problems_arg, sample, k, budget, out_root):
    fn = METHODS[method]
    problems = DataLoader.run("data")
    if problems_arg:
        problems = [p for p in problems if p[0] in problems_arg]
    per_problem = []
    for pid, timeout, tests, trajs, refs in problems:
        Validator.init_globals(tests, timeout)
        uids = sorted(trajs)[:sample]
        npass, teds, ips = 0, [], []
        t0 = time.time()
        rows = [("user_id", "pass", "ted", "ip", "buggy", "fixed", "oracle")]
        for u in uids:
            was = trajs.get(u) or []
            if not was:
                continue
            buggy, oracle = was[-1], refs.get(u)
            refp = [v for kk, v in refs.items() if kk != u]
            try:
                patch = fn(was, refp, k=k, budget=budget)
            except Exception:
                patch = None
            ok = patch is not None
            ted = _metrics.ted(buggy, patch) if ok else None
            ip = _metrics.intent_preservation(buggy, patch, oracle) if ok and oracle else None
            if ok:
                npass += 1
                if ted is not None: teds.append(ted)
                if ip is not None: ips.append(ip)
            rows.append((u, int(ok), ted if ted is not None else "",
                         ip if ip is not None else "", buggy, patch or "", oracle or ""))
        dur = time.time() - t0
        n = max(len(uids), 1)
        od = os.path.join(out_root, method, pid); os.makedirs(od, exist_ok=True)
        with open(os.path.join(od, "results.csv"), "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(rows)
        rec = {"pid": pid, "n": n, "pass": npass, "rr": npass / n,
               "ted": mean(teds) if teds else None,
               "ip": mean(ips) if ips else None, "sec": dur}
        per_problem.append(rec)
        print(f"[{method}/{pid}] RR={rec['rr']:.0%} ({npass}/{n}) "
              f"IP={rec['ip'] if rec['ip'] is None else round(rec['ip'],2)} "
              f"TED={rec['ted'] if rec['ted'] is None else round(rec['ted'],1)} {dur:.0f}s",
              flush=True)
    # overall
    tot_pass = sum(r["pass"] for r in per_problem)
    tot_n = sum(r["n"] for r in per_problem)
    ips = [r["ip"] for r in per_problem if r["ip"] is not None]
    teds = [r["ted"] for r in per_problem if r["ted"] is not None]
    overall = {"method": method, "k": k, "budget": budget,
               "problems": ",".join(r["pid"] for r in per_problem),
               "rr": tot_pass / tot_n if tot_n else 0,
               "pass": tot_pass, "n": tot_n,
               "ip": mean(ips) if ips else None,
               "ted": mean(teds) if teds else None,
               "per_problem": {r["pid"]: round(r["rr"], 3) for r in per_problem}}
    print(f"\n== {method} OVERALL: RR={overall['rr']:.1%} ({tot_pass}/{tot_n}) "
          f"IP={None if overall['ip'] is None else round(overall['ip'],3)} "
          f"per-problem={overall['per_problem']}")
    return overall


def log_md(overall, sample):
    path = os.path.join(HERE, "METHODS.md")
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8") as f:
        if new:
            f.write("# HISTRA improvement methods — results log\n\n")
            f.write("Dev set, same 50-sample uids (sorted). Baselines on these problems:\n")
            f.write("Refactory p02694=60%/p02659=66%, PaR=54%/40%, orig HISTRA=26%/0%.\n\n")
            f.write("| method | k | budget | sample | problems | RR | IP | per-problem |\n")
            f.write("|---|---|---|---|---|---|---|---|\n")
        ip = "--" if overall["ip"] is None else f"{overall['ip']:+.2f}"
        pp = " ".join(f"{p}={int(r*100)}%" for p, r in overall["per_problem"].items())
        f.write(f"| {overall['method']} | {overall['k']} | {overall['budget']} | "
                f"{sample} | {overall['problems']} | {overall['rr']:.1%} "
                f"({overall['pass']}/{overall['n']}) | {ip} | {pp} |\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--method", required=True, choices=list(METHODS))
    ap.add_argument("--problems", nargs="+", default=["p02694", "p02659"])
    ap.add_argument("-n", "--sample", type=int, default=30)
    ap.add_argument("-k", type=int, default=4)
    ap.add_argument("--budget", type=int, default=80)
    ap.add_argument("-o", "--out", default=os.path.join(HERE, "results_methods"))
    args = ap.parse_args()
    overall = run(args.method, args.problems, args.sample, args.k, args.budget, args.out)
    log_md(overall, args.sample)


if __name__ == "__main__":
    main()
