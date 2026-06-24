import ast
import copy


class Reformatter(ast.NodeTransformer):
    """Reformat sketched anchor std_ast back onto original surface, preserving holes."""

    def __init__(self, replace_map: dict[int, tuple[str, bool]]):
        """replace_map: id(origin_node_in_anchor_org) -> (hole_id, is_stmt)."""
        self.replace_map = replace_map or {}

    def visit(self, node: ast.AST):
        if isinstance(node, (ast.expr, ast.stmt)):
            info = self.replace_map.get(id(node))
            if info is not None:
                hid, is_stmt = info
                if is_stmt:
                    return ast.copy_location(ast.Expr(value=ast.Name(id=hid, ctx=ast.Load())), node)
                else:
                    return ast.copy_location(ast.Name(id=hid, ctx=ast.Load()), node)
        return super().visit(node)

    @classmethod
    def is_hole(cls, node):
        # stmt-hole: Expr(Name('__HOLE_k__')) ; expr-hole: Name('__HOLE_k__')
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Name) and node.value.id.startswith("__HOLE_"):
            return True, node.value.id, True
        if isinstance(node, ast.Name) and node.id.startswith("__HOLE_"):
            return True, node.id, False
        return False, None, False

    @classmethod
    def walk(cls, an, sn):
        pairs = []  # (origin_node_in_anchor_org, hole_id, is_stmt)
        if not isinstance(an, ast.AST) or not isinstance(sn, ast.AST):
            return pairs
        hole, hid, is_stmt = cls.is_hole(sn)
        if hole:
            origin = getattr(an, "_origin", None)
            if isinstance(origin, (ast.expr, ast.stmt)) and isinstance(hid, str):
                pairs.append((origin, hid, is_stmt))
            return pairs
        # recurse through fields
        for (f1, v1), (_, v2) in zip(ast.iter_fields(an), ast.iter_fields(sn)):
            if isinstance(v1, ast.AST) and isinstance(v2, ast.AST):
                pairs.extend(cls.walk(v1, v2))
            elif isinstance(v1, list) and isinstance(v2, list):
                for a_item, s_item in zip(v1, v2):
                    pairs.extend(cls.walk(a_item, s_item))
        return pairs

    @classmethod
    def run(cls, anchor, sketched_std):
        anchor_std, anchor_org = anchor

        # Walk anchor_std and sketched in parallel to locate which anchor_std nodes were holed
        pairs = cls.walk(anchor_std, sketched_std)
        if not pairs:
            return ast.unparse(anchor_org)

        # Work on original object: ids in replace_map refer to anchor_org nodes.
        replace_map = {id(origin): (hid, is_stmt) for origin, hid, is_stmt in pairs}
        new_org = cls(replace_map).visit(anchor_org)
        ast.fix_missing_locations(new_org)
        return new_org
        