"""Evaluation metrics. TED = type-label AST tree edit distance (APTED)."""
import ast, sys
from apted import APTED, Config

sys.setrecursionlimit(100000)


class _Node:
    __slots__ = ("name", "children")

    def __init__(self, name, children):
        self.name = name
        self.children = children


class _Cfg(Config):
    def rename(self, a, b):
        return 0 if a.name == b.name else 1

    def children(self, node):
        return node.children


def _label(n):
    """Value-aware label: leaves carry their value so e.g. `x=1` vs `x=2` differ."""
    if isinstance(n, ast.Name):
        return "Name:" + n.id
    if isinstance(n, ast.Constant):
        return "Const:" + repr(n.value)
    if isinstance(n, ast.arg):
        return "arg:" + (n.arg or "")
    if isinstance(n, ast.Attribute):
        return "Attr:" + n.attr
    return type(n).__name__


def _to_node(a):
    return _Node(_label(a), [_to_node(c) for c in ast.iter_child_nodes(a)])


def ted(code_a, code_b):
    """Value-aware AST tree edit distance. None if either side fails to parse."""
    try:
        ta, tb = ast.parse(code_a), ast.parse(code_b)
    except (SyntaxError, ValueError):
        return None
    return APTED(_to_node(ta), _to_node(tb), _Cfg()).compute_edit_distance()


def intent_preservation(buggy, fixed, oracle):
    """(TED_s - TED_f) / (TED_s + TED_f), where TED_s = TED(buggy, oracle AC) and
    TED_f = TED(buggy, fixed). Higher = the fix stays closer to the student's buggy
    program than adopting the AC would (more intent-preserving). None if unparsable."""
    ts, tf = ted(buggy, oracle), ted(buggy, fixed)
    if ts is None or tf is None:
        return None
    return (ts - tf) / (ts + tf) if (ts + tf) else 0.0
