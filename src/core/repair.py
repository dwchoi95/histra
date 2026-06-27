import ast
import copy

class Repair(ast.NodeTransformer):
    def __init__(self, node_map: dict, var_map: dict = None):
        self.node_map = node_map
        self._covered = set()
        self.varmap = var_map or {}

    def _rename_vars(self, tree: ast.AST) -> ast.AST:
        if not self.varmap:
            return tree

        class R(ast.NodeTransformer):
            def __init__(self, vm):
                self.vm = vm

            def visit_Name(self, n: ast.Name):
                if n.id in self.vm:
                    return ast.copy_location(ast.Name(id=self.vm[n.id], ctx=n.ctx), n)
                return n

            def visit_arg(self, n: ast.arg):
                if n.arg in self.vm:
                    n.arg = self.vm[n.arg]
                return n

        return R(self.varmap).visit(tree)
    
    def visit(self, node: ast.AST):
        nid = id(node)
        if nid in self.node_map and nid not in self._covered:
            replacement = copy.deepcopy(self.node_map[nid])
            replacement = self._rename_vars(replacement)
            self._covered.update(id(n) for n in ast.walk(node))
            return ast.copy_location(replacement, node)
        return super().visit(node)

    def run(self, tree: ast.AST):
        new_tree = self.visit(tree)
        ast.fix_missing_locations(new_tree)
        return new_tree
