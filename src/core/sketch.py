import ast
from apted import APTED
from src.utils import Node

class Sketcher(ast.NodeTransformer):
    def visit(self, node: ast.AST):
        if isinstance(node, ast.expr) and id(node) in self.changed:
            return self._hole(node)
        self.generic_visit(node)
        return node

    @classmethod
    def _expr_node(cls, n: ast.AST):
        return Node(cls._expr_label(n), cls._expr_children(n), n)

    @classmethod
    def _expr_label(cls, n: ast.AST):
        if not isinstance(n, ast.expr):
            return type(n).__name__
        fields = []
        for name, value in ast.iter_fields(n):
            value_label = cls._field_label(value)
            if value_label is not None:
                fields.append((name, value_label))
        return repr((type(n).__name__, tuple(fields)))

    @classmethod
    def _field_label(cls, value):
        if isinstance(value, ast.expr):
            return None
        if isinstance(value, ast.AST):
            fields = []
            for name, child in ast.iter_fields(value):
                child_label = cls._field_label(child)
                if child_label is not None:
                    fields.append((name, child_label))
            return (type(value).__name__, tuple(fields))
        if isinstance(value, list):
            items = [cls._field_label(item) for item in value]
            items = [item for item in items if item is not None]
            return tuple(items) if items else None
        return value

    @classmethod
    def _expr_children(cls, n: ast.AST):
        children = []
        for child in ast.iter_child_nodes(n):
            if isinstance(child, ast.expr):
                children.append(cls._expr_node(child))
            else:
                children.extend(cls._expr_children(child))
        return children

    @classmethod
    def align(cls, std_traj):
        anchor_node_set = {id(n) for n in ast.walk(cls.anchor) if isinstance(n, ast.expr)}
        B = cls._expr_node(cls.anchor)
        matched_sets = []
        for i in range(len(std_traj) - 1):
            A = cls._expr_node(std_traj[i][0])
            mapping = APTED(A, B).compute_edit_mapping()
            # collect anchor-side nodes that label-match
            anchor_matched = set()
            for n1, n2 in mapping:
                if n1 is not None and n2 is not None and n1.name == n2.name and isinstance(n2.node, ast.expr):
                    anchor_matched.add(id(n2.node))
            matched_sets.append(anchor_matched)
        stable_ids = set.intersection(*matched_sets) if matched_sets else set()
        preserved = stable_ids & anchor_node_set
        changed = anchor_node_set - preserved
        return preserved, changed

    @classmethod
    def _hole(cls, node: ast.AST) -> ast.AST:
        node._hole = True
        node._hole_type = type(node).__name__
        return node

    @classmethod
    def run(cls, std_traj):
        cls.anchor = std_traj[-1][0]
        cls.preserved, cls.changed = cls.align(std_traj)
        skt = cls().visit(cls.anchor)
        ast.fix_missing_locations(skt)
        return skt
    