"""Regression check: Minimizer keeps only the changes the tests need, reverting the rest to the
student's own code (skeleton region first). Run from the repo root:
    .venv/bin/python tests/test_minimize.py"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.histra import HISTRA
from src.core.minimize import Minimizer
from src.core.standardizer import Standardizer

WA1 = "n = int(input())\ns = 0\nfor i in range(n):\n    s += i\nprint(s)\n"
WA2 = "n = int(input())\ns = 0\nfor i in range(n):\n    s += i * 2\nprint(s + 1)\n"   # bug: the + 1
# A passing patch assembled from another student's code: correct, but it also rewrote code that
# was already right (a skeleton statement and a hole that needed no change).
PATCH = "n = int(input().strip())\ns = 0\nfor i in range(n):\n    s += 2 * i\nprint(s)\n"


def passes(src):  # spec: print the sum of 2*i for i < n
    for n in (0, 3, 5):
        out = subprocess.run([sys.executable, "-c", src], input=f"{n}\n", capture_output=True, text=True).stdout
        if out.strip() != str(sum(2 * i for i in range(n))):
            return False
    return True


_, _, (pristine, holed) = HISTRA.sketch(Standardizer.run([WA1, WA2]))
assert passes(PATCH)
out = Minimizer(pristine, holed).run(PATCH, passes)
assert out == "n = int(input())\ns = 0\nfor i in range(n):\n    s += i * 2\nprint(s)", out
print("ok\n" + out)

# Repair: a reference fixes the bug and also rewrites a skeleton statement; the hole-only phase
# must keep the student's skeleton statement and still return a passing, minimized patch.
from src.core.repair import Repair
REF = "n = int(input().strip())\ntotal = 0\nfor k in range(n):\n    total += 2 * k\nprint(total)\n"
out = Repair(pristine, holed).run(WA2, [REF], passes)
assert out is not None and "n = int(input())" in out and "print(s)" in out, out
print("ok (repair)\n" + out)

# Minimizer drops a statement the merge inserted that the tests do not need (here a dead `s = 0`
# and an unused import), returning the student's program with only the needed fix.
PATCH2 = "import math\nn = int(input())\ns = 0\ns = 0\nfor i in range(n):\n    s += i * 2\nprint(s)\n"
out = Minimizer(pristine, holed).run(PATCH2, passes)
assert out == "n = int(input())\ns = 0\nfor i in range(n):\n    s += i * 2\nprint(s)", out
print("ok (drop inserted)")

# Paper running example (p02742, u353548710): the hole-only merge inserts a reference statement
# `s = w // 2 * h` that is overwritten anyway. The Minimizer must drop it, not "revert" it to the
# student's `s = 0` from inside the if (a match whose parents differ).
B = ["h, w = map(int, input().split())\nhd, hm, wd, wm = h // 2, h % 2, w // 2, w % 2\n"
     "s = hd * wd * 2  + hm * wd + wm * hd + hm * wm\nprint(s)\n"] * 2
B.append("h, w = map(int, input().split())\nhd, hm, wd, wm = h // 2, h % 2, w // 2, w % 2\n"
         "s = hd * wd * 2  + hm * wd + wm * hd + hm * wm\nif h == 1 or w == 1:\n    s = 0\nprint(s)\n")
CAND = ("h, w = map(int, input().split())\ns = w // 2 * h\nhd, hm, wd, wm = (h // 2, h % 2, w // 2, w % 2)\n"
        "s = hd * wd * 2 + hm * wd + wm * hd + hm * wm\nif h == 1 or w == 1:\n    s = 1\nprint(s)\n")


def bishop(src):  # p02742: squares a bishop can reach from the corner of an h x w board
    for h, w in ((1, 1), (1, 5), (4, 5), (7, 3), (2, 2)):
        out = subprocess.run([sys.executable, "-c", src], input=f"{h} {w}\n", capture_output=True, text=True).stdout
        if out.strip() != str(1 if h == 1 or w == 1 else (h * w + 1) // 2):
            return False
    return True


_, _, (pristine, holed) = HISTRA.sketch(Standardizer.run(B))
out = Minimizer(pristine, holed).run(CAND, bishop)
assert out == ("h, w = map(int, input().split())\nhd, hm, wd, wm = (h // 2, h % 2, w // 2, w % 2)\n"
               "s = hd * wd * 2 + hm * wd + wm * hd + hm * wm\nif h == 1 or w == 1:\n    s = 1\nprint(s)"), out
print("ok (running example)")
