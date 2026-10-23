"""Regression check for the fault-localization control (histra_eval.py fl): the per-test spectrum of b and
the Ochiai holes on a toy whose bug (line 3) only the failing test executes. Run from the repo root:
    .venv/bin/python tests/test_fl_holes.py"""
import ast, os, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "src", "experiments")]
os.environ["FLCACHE"] = tempfile.mkdtemp()
import histra_eval as H

src = "n = int(input())\nif n > 5:\n    print(n * 3)\nelse:\n    print(n * 2)\n"
c = dict(pid="toy", user="u", was=[src], timeout=2.0,
         tests=[dict(input="1\n", output="2\n"), dict(input="2\n", output="4\n"), dict(input="9\n", output="18\n")])
spec = H.spectrum(c)
assert spec == [[True, [1, 2, 5]], [True, [1, 2, 5]], [False, [1, 2, 3]]], spec
t = ast.parse(src)
lines = lambda ids: {n.lineno for n in ast.walk(t) if id(n) in ids and hasattr(n, "lineno")}
assert lines(H.fl_holes(t, spec)) == {3}                          # only print(n * 3) has Ochiai 1.0
print("ok")
