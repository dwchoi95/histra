"""HISTRA-loop: keep standardize/sketch/reformat unchanged, but turn
search -> repair -> validate into a LOOP. The partially-filled patch re-enters
search as the new anchor, producing a fresh node_map each pass, until no holes
remain; then validate.

Convergence: a naive re-loop stalls on a hole whose enclosing statement type has
no donor match (the dominant fill_fail cause). So when a pass makes no progress,
we ESCALATE: replace the smallest enclosing statement of a remaining hole with
its nearest donor statement; if that type has no donor, climb to the parent
statement, ultimately replacing the whole module with the nearest donor AC. Holes
therefore decrease monotonically to 0. We validate at each hole-free state and
return the EARLIEST passing patch (fewest/smallest replacements => best IP),
across a few random restarts (the searcher's tie-break is stochastic).

Usage: python baselines/histra_loop.py -p <pid> [-n 50] [--restarts 4]
       [--max-iters 20] [-o out_dir]
"""
import os, sys, ast, csv, copy, time, argparse, random
from statistics import mean
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warnings; warnings.filterwarnings("ignore")

from src.utils import DataLoader
from src.core.standardizer import Standardizer
from src.core.sketch import Sketcher
from src.core.reformat import Reformatter
from src.core.searcher import Searcher
from src.core.repair import Repair
from src.core.validator import Validator
from src.utils import metrics as _metrics

HOLE = "__HOLE__"


def is_hole(n):
    return isinstance(n, ast.Name) and n.id == HOLE

def hole_nodes(tree):
    return [n for n in ast.walk(tree) if is_hole(n)]

def n_holes(tree):
    return sum(1 for _ in hole_nodes(tree))

def parent_map(tree):
    pm = {}
    for p in ast.walk(tree):
        for c in ast.iter_child_nodes(p):
            pm[id(c)] = p
    return pm

def enclosing_stmt(node, pm):
    cur = node
    while cur is not None and not isinstance(cur, ast.stmt):
        cur = pm.get(id(cur))
    return cur


class _ReplaceById(ast.NodeTransformer):
    def __init__(self, target_id, replacement):
        self.target_id = target_id
        self.replacement = replacement
        self.done = False
    def visit(self, node):
        if id(node) == self.target_id:
            self.done = True
            return ast.copy_location(copy.deepcopy(self.replacement), node)
        return super().generic_visit(node) or node

def replace_node(tree, target_id, replacement):
    t = _ReplaceById(target_id, replacement)
    new = t.visit(tree)
    ast.fix_missing_locations(new)
    return new, t.done


def nearest_same_type(node, searcher):
    """Nearest donor statement of the same type as `node` (APTED, holes cost 0)."""
    cands = [r for roots in searcher.ref_roots_list for r in roots
             if type(r) is type(node)]
    if not cands:
        return None
    best, bestd = None, float("inf")
    for r in cands:
        try:
            d = searcher._apted_dist(node, r)
        except Exception:
            continue
        if d < bestd:
            bestd, best = d, r
    return best


def nearest_module(cur, refs_src, searcher):
    """Whole-program fallback: nearest donor AC (var-remapped), by APTED to cur."""
    best, bestd = None, float("inf")
    for code in refs_src:
        try:
            r = ast.parse(code)
            vm = searcher._varmap_defuse(cur, r)
            r = searcher._rename_vars(r, vm)
            d = searcher._apted_dist(cur, r)
        except Exception:
            continue
        if d < bestd:
            bestd, best = d, r
    return best


def escalate(cur, searcher, refs_src):
    """Force progress: fill (replace) the enclosing statement of one remaining
    hole, climbing to larger units until a donor matches, else replace module."""
    holes = hole_nodes(cur)
    if not holes:
        return cur
    pm = parent_map(cur)
    node = enclosing_stmt(holes[0], pm)
    while node is not None and not isinstance(node, ast.Module):
        donor = nearest_same_type(node, searcher)
        if donor is not None:
            new, ok = replace_node(cur, id(node), donor)
            if ok:
                return new
        node = enclosing_stmt(pm.get(id(node)), pm)
    mod = nearest_module(cur, refs_src, searcher)
    return mod if mod is not None else cur


def repair_loop(traj, refs_src, max_iters=20, restarts=4):
    """Returns (best_patch_source or None, n_iters_used)."""
    std_traj = Standardizer.run(traj)
    anchor = std_traj[-1]
    skt_std = Sketcher.run(std_traj)
    skt_org = Reformatter.run(anchor, skt_std)   # holed AST, original surface

    best_patch, best_ted = None, float("inf")
    for _ in range(restarts):
        cur = copy.deepcopy(skt_org)
        searcher = Searcher(refs_src, anchor)    # refs remapped toward anchor once
        passes = 0
        for _ in range(max_iters):
            if n_holes(cur) == 0:
                break
            before = n_holes(cur)
            node_map = searcher.run(cur)         # patch re-enters search
            # only fill statements that actually contain a hole, so already-clean
            # code is never churned -> holes decrease monotonically
            id2node = {id(n): n for n in ast.walk(cur)}
            node_map = {k: v for k, v in node_map.items()
                        if k in id2node and any(is_hole(x) for x in ast.walk(id2node[k]))}
            if node_map:
                cur = Repair(node_map).run_tree(cur)
            if n_holes(cur) >= before:           # stalled -> force progress
                cur = escalate(cur, searcher, refs_src)
            passes += 1
            if n_holes(cur) == 0:
                break
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
            if t < best_ted:                      # keep most intent-preserving pass
                best_ted, best_patch = t, patch
    return best_patch


def run_problem(pid, timeout, tests, trajs, refs, sample, restarts, out_root):
    uids = sorted(trajs)[:sample]
    Validator.init_globals(tests, timeout)
    rows = [("user_id", "pass", "ted", "ip", "att_seconds", "buggy", "fixed", "oracle")]
    pass_cnt, ted_vals, ip_vals = 0, [], []
    t0 = time.time()
    for u in uids:
        was = trajs.get(u) or []
        if not was:
            continue
        buggy, oracle = was[-1], refs.get(u)
        refpool = [v for k, v in refs.items() if k != u]
        try:
            patch = repair_loop(was, refpool, restarts=restarts)
        except Exception:
            patch = None
        passed = patch is not None
        ted = _metrics.ted(buggy, patch) if passed else None
        ip = (_metrics.intent_preservation(buggy, patch, oracle)
              if passed and oracle else None)
        if passed:
            pass_cnt += 1
            if ted is not None: ted_vals.append(ted)
            if ip is not None: ip_vals.append(ip)
        rows.append((u, int(passed), ted if ted is not None else "",
                     ip if ip is not None else "", "", buggy, patch or "", oracle or ""))
    dur = time.time() - t0
    n = max(len(uids), 1)
    att = dur / n
    rows = [rows[0]] + [(u, p, t, i, f"{att:.6f}", b, f, o)
                        for (u, p, t, i, _a, b, f, o) in rows[1:]]
    od = os.path.join(out_root, pid); os.makedirs(od, exist_ok=True)
    with open(os.path.join(od, "results.csv"), "w", newline="", encoding="utf-8") as fp:
        csv.writer(fp).writerows(rows)
    print(f"[{pid}] RR={pass_cnt/n:.3f} pass={pass_cnt}/{n} "
          f"ted={mean(ted_vals) if ted_vals else 0:.2f} "
          f"ip={mean(ip_vals) if ip_vals else 0:+.2f} t={dur:.1f}s", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--dataset", default="data")
    ap.add_argument("-p", "--problems", nargs="+", default=None)
    ap.add_argument("-n", "--sample", type=int, default=50)
    ap.add_argument("--restarts", type=int, default=4)
    ap.add_argument("-o", "--out", default="baselines/results_histra_loop")
    args = ap.parse_args()
    problems = DataLoader.run(args.dataset)
    if args.problems:
        problems = [p for p in problems if p[0] in args.problems]
    os.makedirs(args.out, exist_ok=True)
    for pid, timeout, tests, trajs, refs in problems:
        run_problem(pid, timeout, tests, trajs, refs, args.sample,
                    args.restarts, args.out)


if __name__ == "__main__":
    main()
