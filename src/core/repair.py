import ast
import copy

class Repair(ast.NodeTransformer):
    def __init__(self, node_map: dict):
        self.node_map = node_map
        self._covered = set()
    
    def visit(self, node: ast.AST):
        nid = id(node)
        if nid in self.node_map and nid not in self._covered:
            replacement = copy.deepcopy(self.node_map[nid])
            self._covered.update(id(n) for n in ast.walk(node))
            return ast.copy_location(replacement, node)
        return super().visit(node)

    def run(self, tree: ast.AST):
        new_tree = self.visit(tree)
        ast.fix_missing_locations(new_tree)
        return new_tree
