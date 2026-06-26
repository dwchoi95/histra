import ast
import copy


def is_hole(node: ast.AST) -> bool:
    return isinstance(node, ast.AST) and getattr(node, "_hole", False)


def hole_name(node: ast.AST) -> str:
    hole_type = getattr(node, "_hole_type", type(node).__name__)
    return f"__{hole_type}__"


class HoleUnparser(ast._Unparser):
    def traverse(self, node):
        if isinstance(node, list):
            for item in node:
                self.traverse(item)
            return None
        if is_hole(node):
            self.write(hole_name(node))
            return None
        return super().traverse(node)

    def visit(self, node):
        if is_hole(node):
            self.write(hole_name(node))
            return None
        return super().visit(node)


class _HoleNameTransformer(ast.NodeTransformer):
    def visit(self, node):
        if is_hole(node):
            name = ast.Name(id=hole_name(node), ctx=getattr(node, "ctx", ast.Load()))
            return ast.copy_location(name, node)
        return super().visit(node)


def unparse(tree: ast.AST) -> str:
    if hasattr(ast, "_Unparser"):
        return HoleUnparser().visit(tree)

    fallback_tree = copy.deepcopy(tree)
    fallback_tree = _HoleNameTransformer().visit(fallback_tree)
    ast.fix_missing_locations(fallback_tree)
    return ast.unparse(fallback_tree)


unparse_with_holes = unparse