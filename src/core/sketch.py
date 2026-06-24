import ast
from apted import APTED


        
class Node:
    __slots__ = ("name", "children", "node")

    def __init__(self, name, children, node):
        self.name = name
        self.children = children
        self.node = node

class Sketcher(ast.NodeTransformer):
    def __init__(self, std_traj):
        self.preserved, self.changed = self.align(std_traj)
        self.k = 0

    def _node(self, n: ast.AST):
        return Node(type(n).__name__, [self._node(c) for c in ast.iter_child_nodes(n)], n)

    def align(self, std_traj):
        if not std_traj:
            return set(), set()
        anchor = std_traj[-1][0]
        anchor_node_set = {id(n) for n in ast.walk(anchor)}
        B = self._node(anchor)
        matched_sets = []
        for i in range(len(std_traj) - 1):
            A = self._node(std_traj[i][0])
            mapping = APTED(A, B).compute_edit_mapping()
            # collect anchor-side nodes that label-match
            anchor_matched = set()
            for n1, n2 in mapping:
                if n1 is not None and n2 is not None and n1.name == n2.name:
                    anchor_matched.add(id(n2.node))
            matched_sets.append(anchor_matched)
        stable_ids = set.intersection(*matched_sets) if matched_sets else set()
        preserved = stable_ids & anchor_node_set
        changed = anchor_node_set - preserved
        return preserved, changed

    def _hole(self, node: ast.AST) -> ast.AST:
        self.k += 1
        name = ast.Name(id=f"__HOLE_{self.k}__", ctx=getattr(node, "ctx", None) or ast.Load())
        return ast.Expr(value=name) if isinstance(node, ast.stmt) else name

    def visit(self, node: ast.AST):
        if isinstance(node, (ast.expr, ast.stmt)):
            nid = id(node)
            if nid in self.preserved:
                return node
            if nid in self.changed:
                return self._hole(node)
            self.generic_visit(node)
            return node
        self.generic_visit(node)
        return node

    def run(self, anchor):
        sketched = self.visit(anchor)
        ast.fix_missing_locations(sketched)
        return sketched
    