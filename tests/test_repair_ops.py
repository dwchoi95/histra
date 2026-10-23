"""Hole-only merge must take the reference's operators inside the holes and keep the student's outside
(final review K1: operator singletons must not be frozen). Also checks the matched random-hole control (J7)."""
import ast, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "experiments"))
from src.core.repair import Repair, SHARED
from src.core.merge import MergeRepair

b = "n = int(input())\nm = n * 2\nif n < 3:\n    print(n + 1)\nelse:\n    print(m)\n"
r = "n = int(input())\nm = n // 2\nif n <= 3:\n    print(n - 1)\nelse:\n    print(m)\n"
t = ast.parse(b)
ifn = t.body[2]
holed = {id(x) for part in (ifn.test, ifn.body[0]) for x in ast.walk(part) if not isinstance(x, SHARED)}
rep = Repair(t, holed)
out = MergeRepair()._merge_patch(t, r, False, rep.skeleton)
assert "n - 1" in out and "n <= 3" in out, out          # operators inside the holes follow r
assert "m = n * 2" in out, out                           # the frozen statement keeps the student's operator
print("ok ops")

from histra_eval import random_holes
units = lambda tree: [n for n in ast.walk(tree) if isinstance(n, (ast.stmt, ast.expr))]
for seed in ("u:0", "u:1", "u:2"):
    rh = random_holes(t, holed, seed)
    assert rh == random_holes(t, holed, seed)            # deterministic per seed
    roots = [n for n in units(t) if id(n) in rh and not any(id(p) in rh for p in ast.walk(t) if n in list(ast.iter_child_nodes(p)))]
    assert len(roots) == 2, (seed, len(roots))           # as many roots as the history's holes (test + print)
    assert sorted(isinstance(n, ast.stmt) for n in roots) == [False, True], seed   # same kinds: one expr, one stmt
print("ok randhole")
