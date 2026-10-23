"""Regression check: holes found by Sketch must reach the student's original code.
Run from the repo root:  .venv/bin/python tests/test_sketch_holes.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.histra import HISTRA
from src.core.standardizer import Standardizer

WA1 = "n = int(input())\ns = 0\nfor i in range(n):\n    s += i\nprint(s)\n"
WA2 = "n = int(input())\ns = 0\nfor i in range(n):\n    s += i * 2\nprint(s + 1)\n"

skt_org, (_, anchor_org), _ = HISTRA.sketch(Standardizer.run([WA1, WA2]))
assert "__HOLE_" in skt_org, skt_org                      # changed parts are holed on the original surface
assert "n = int(input())" in skt_org, skt_org             # stable parts keep the student's own code
assert "for i in range(n):" in skt_org, skt_org           # original (non-standardized) loop form survives
print("ok\n" + skt_org)

# Shared ast.Load/operator singletons must not leak into the hole set, or nothing gets frozen.
from src.core.repair import Repair
_, _, (pristine, holed) = HISTRA.sketch(Standardizer.run([WA1, WA2]))
assert id(pristine.body[0]) in Repair(pristine, holed).skeleton   # n = int(input()) is frozen
print("ok (frozen skeleton)")
