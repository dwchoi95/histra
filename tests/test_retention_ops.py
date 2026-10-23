"""Skeleton retention must count operator changes (final review C2): `<`->`<=`, `+`->`-` are losses."""
import ast, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "experiments"))
from skel import retention

src = "n = int(input())\nif n < 3:\n    print(n + 1)\n"
a = ast.parse(src)
assert retention(a, set(), src)[0] == 1.0
for patch in ("n = int(input())\nif n <= 3:\n    print(n + 1)\n", "n = int(input())\nif n < 3:\n    print(n - 1)\n"):
    r, _ = retention(a, set(), patch)
    assert r < 1.0, (patch, r)
print("ok")
