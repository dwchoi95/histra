import ast


class Reformatter(ast.NodeTransformer):
    def __init__(self, replace_map: dict[int, str]):
        self.replace_map = replace_map or {}

    def visit(self, node: ast.AST):
        hid = self.replace_map.get(id(node))
        if hid is not None:
            ctx = getattr(node, "ctx", ast.Load())
            return ast.copy_location(ast.Name(id=hid, ctx=ctx), node)
        return super().visit(node)

    @classmethod
    def is_hole(cls, node):
        if isinstance(node, ast.Name) and node.id == "__HOLE__":
            return node.id
        return None

    @classmethod
    def walk(cls, an, sn):
        pairs = {}
        cls._walk(an, sn, pairs)
        return pairs

    @classmethod
    def _walk(cls, an, sn, pairs):
        if not isinstance(an, ast.AST) or not isinstance(sn, ast.AST):
            return

        hole = cls.is_hole(sn)
        if hole:
            origin = getattr(sn, "_origin", None) or getattr(an, "_origin", None)
            if isinstance(origin, ast.expr):
                pairs[id(origin)] = hole
            return

        for (name1, value1), (name2, value2) in zip(ast.iter_fields(an), ast.iter_fields(sn)):
            if name1 != name2:
                continue
            if isinstance(value1, ast.AST) and isinstance(value2, ast.AST):
                cls._walk(value1, value2, pairs)
            elif isinstance(value1, list) and isinstance(value2, list):
                for item1, item2 in zip(value1, value2):
                    cls._walk(item1, item2, pairs)

    @classmethod
    def run(cls, anchor, sketched_std):
        anchor_std, anchor_org = anchor

        # Walk anchor_std and sketched in parallel to locate which anchor_std nodes were holed
        pairs = cls.walk(anchor_std, sketched_std)
        if not pairs:
            return anchor_org

        # Work on original object: ids in replace_map refer to anchor_org nodes.
        new_org = cls(pairs).visit(anchor_org)
        ast.fix_missing_locations(new_org)
        return new_org
        