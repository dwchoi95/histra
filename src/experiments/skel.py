"""Intent skeleton of the buggy program, as HISTRA computes it, and the skeleton loss of a program (Section II-B)."""
import ast
import copy
import sys

from apted import APTED, Config

import common  # noqa: F401  (puts the repository root on sys.path)
from src.core.standardizer import Standardizer
from src.core.sketch import Sketcher
from src.core.reformat import Reformatter

sys.setrecursionlimit(100000)


def naive_pair(code):
    """No standardization: std is a plain copy whose nodes point to their original twins."""
    org, std = ast.parse(code), ast.parse(code)
    for o, w in zip(ast.walk(org), ast.walk(std)):
        w._origin = o
    return std, org


def units(tree):
    return [n for n in ast.walk(tree) if isinstance(n, (ast.stmt, ast.expr))]


def holed_ids(was, standardize=True):
    """(original anchor, ids of its stmt/expr nodes inside holes), as HISTRA's Sketch and projection compute them."""
    traj = Standardizer.run(was) if standardize else [naive_pair(c) for c in was]
    a_std, a_org = traj[-1]
    # Sketcher mutates a_std in place: keep an unsketched copy (sharing the _origin targets)
    pre = copy.deepcopy(a_std, {id(x): x for x in ast.walk(a_org)})
    skt_std = Sketcher(traj).run(a_std)
    return a_org, {id(n) for origin, _, _ in Reformatter.walk(pre, skt_std) for n in ast.walk(origin)}


class _N:
    __slots__ = ("name", "children", "node")
    def __init__(self, name, children, node):
        self.name, self.children, self.node = name, children, node


def _label(n):
    if isinstance(n, ast.Name): return "Name:" + n.id
    if isinstance(n, ast.Constant): return "Const:" + repr(n.value)
    if isinstance(n, ast.arg): return "arg:" + (n.arg or "")
    if isinstance(n, ast.Attribute): return "Attr:" + n.attr
    # operators are outside units(): fold them into the parent's label so `n < 3` -> `n <= 3` counts as a change
    if isinstance(n, (ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.AugAssign)): return f"{type(n).__name__}:{type(n.op).__name__}"
    if isinstance(n, ast.Compare): return "Compare:" + ",".join(type(o).__name__ for o in n.ops)
    return type(n).__name__


def _tree(n):
    return _N(_label(n), [_tree(c) for c in ast.iter_child_nodes(n)], n)


class _Cfg(Config):
    def rename(self, a, b): return 0 if a.name == b.name else 1
    def children(self, n): return n.children


def retention(anchor_org, holed, patch_src):
    """(share of the anchor's skeleton stmt/expr nodes kept under the value-aware APTED mapping, skeleton size)."""
    skel = [n for n in units(anchor_org) if id(n) not in holed]
    if not skel:
        return None, 0
    try:
        P = ast.parse(patch_src)
    except (SyntaxError, ValueError):
        return None, len(skel)
    A, B = _tree(anchor_org), _tree(P)
    mp = APTED(A, B, _Cfg()).compute_edit_mapping()
    kept = {id(a.node) for a, b in mp if a is not None and b is not None and a.name == b.name}
    return sum(id(n) in kept for n in skel) / len(skel), len(skel)
