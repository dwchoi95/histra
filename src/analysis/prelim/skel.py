"""Shared helpers: intent skeleton of the last WA (exactly as HISTRA computes it) and skeleton retention."""
import os, ast, copy, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
sys.setrecursionlimit(100000)
from apted import APTED, Config
from src.core.standardizer import Standardizer
from src.core.sketch import Sketcher
from src.core.reformat import Reformatter


def naive_pair(code):
    """No standardization: std is a plain copy whose nodes point to their original twins."""
    org, std = ast.parse(code), ast.parse(code)
    for o, w in zip(ast.walk(org), ast.walk(std)):
        w._origin = o
    return std, org


def units(tree):
    return [n for n in ast.walk(tree) if isinstance(n, (ast.stmt, ast.expr))]


def holed_ids(was, standardize=True):
    """ids of anchor_org stmt/expr nodes that HISTRA's Sketch(+Reformat) would put inside holes."""
    traj = Standardizer.run(was) if standardize else [naive_pair(c) for c in was]
    a_std, a_org = traj[-1]
    # Sketcher mutates a_std in place, so keep an unsketched copy (sharing the _origin targets)
    pre = copy.deepcopy(a_std, {id(x): x for x in ast.walk(a_org)})
    skt_std = Sketcher(traj).run(a_std)
    pairs = Reformatter.walk(pre, skt_std)
    anchor = (pre, a_org)
    out = set()
    for origin, _hid, _stmt in pairs:
        out.update(id(n) for n in ast.walk(origin))
    return anchor[1], out


class _N:
    __slots__ = ("name", "children", "node")
    def __init__(self, name, children, node):
        self.name, self.children, self.node = name, children, node


def _label(n):
    if isinstance(n, ast.Name): return "Name:" + n.id
    if isinstance(n, ast.Constant): return "Const:" + repr(n.value)
    if isinstance(n, ast.arg): return "arg:" + (n.arg or "")
    if isinstance(n, ast.Attribute): return "Attr:" + n.attr
    # operators are child nodes outside units(): fold them into the parent's label so that
    # `n < 3` -> `n <= 3` or `a + b` -> `a - b` counts as a change (final review C2)
    if isinstance(n, (ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.AugAssign)): return f"{type(n).__name__}:{type(n.op).__name__}"
    if isinstance(n, ast.Compare): return "Compare:" + ",".join(type(o).__name__ for o in n.ops)
    return type(n).__name__


def _tree(n):
    return _N(_label(n), [_tree(c) for c in ast.iter_child_nodes(n)], n)


class _Cfg(Config):
    def rename(self, a, b): return 0 if a.name == b.name else 1
    def children(self, n): return n.children


def retention(anchor_org, holed, patch_src):
    """Fraction of skeleton stmt/expr nodes of the anchor that the patch keeps with the same
    value-aware label under the minimal APTED edit mapping (1.0 = skeleton fully preserved)."""
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
