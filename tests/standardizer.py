import os
import sys
import ast
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from core.standardizer import Standardizer


def std_src(code: str) -> str:
    std, _ = Standardizer.standardize(code)
    ast.fix_missing_locations(std)
    return ast.unparse(std)


class TestStandardizerOnePass(unittest.TestCase):
    def test_empty_container_literals(self):
        code = """
a = list()
b = tuple()
c = dict()
d = set()
"""
        out = std_src(code)
        self.assertIn("a = []", out)
        self.assertIn("b = ()", out)
        self.assertIn("c = {}", out)
        # set() stays as is
        self.assertIn("d = set()", out)

    def test_range_normalization(self):
        code = """
a = list(range(0, n))
b = list(range(0, n, 1))
c = list(range(x, y, 1))
d = list(range(x, y, 2))
e = list(range(n))
f = list(range(start=0, stop=n, step=1))
"""
        out = std_src(code)
        self.assertIn("a = list(range(0, n, 1))", out)
        self.assertIn("b = list(range(0, n, 1))", out)
        self.assertIn("c = list(range(x, y, 1))", out)
        self.assertIn("d = list(range(x, y, 2))", out)
        self.assertIn("e = list(range(0, n, 1))", out)
        self.assertIn("f = list(range(0, n, 1))", out)

    def test_augassign_expansion(self):
        code = """
x = 1
x += 2
"""
        out = std_src(code)
        self.assertIn("x = 1", out)
        self.assertIn("x = x + 2", out)

    def test_compare_single_flip(self):
        code = """
u = (a > b)
v = (a >= b)
w = (a < b)
"""
        out = std_src(code)
        # parentheses may be omitted by unparse; accept both
        self.assertRegex(out, r"u = \(?b < a\)?")
        self.assertRegex(out, r"v = \(?b <= a\)?")
        # '<' left untouched
        self.assertRegex(out, r"w = \(?a < b\)?")

    def test_compare_chain_flip_safe(self):
        code = """
ok = a > b > c
stay = a < b < c
call_stay = f() > g() > h()
"""
        out = std_src(code)
        # descending-only names/constants chain flipped to ascending reversed
        self.assertIn("ok = c < b < a", out)
        # mixed ops remain
        self.assertIn("stay = a < b < c", out)
        # calls are not flipped (side-effects/ordering)
        self.assertIn("call_stay = f() > g() > h()", out)

    def test_while_guard_break(self):
        code = """
while x:
    do()
"""
        out = std_src(code)
        # while True with leading guard
        self.assertIn("while True:", out)
        self.assertIn("if not x:", out)
        self.assertIn("break", out)
        self.assertIn("do()", out)

    def test_for_to_while(self):
        code = """
for i in a:
    body(i)
"""
        out = std_src(code)
        # iterator assignment and while True loop
        self.assertRegex(out, r"_it\d+ = iter\(a\)")
        self.assertIn("while True:", out)
        self.assertIn("i = next", out)  # assignment via next(_itN)
        self.assertIn("except StopIteration:", out)
        self.assertIn("break", out)
        self.assertIn("body(i)", out)


if __name__ == "__main__":
    unittest.main()
