import ast
from collections import Counter


class AstUtils:
    @staticmethod
    def safe_unparse(node):
        """Unparse a node; None if it can't stand alone (e.g. inside an f-string)."""
        try:
            return ast.unparse(node)
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def root_leaf_paths(code):
        """Bag of root->leaf AST-type paths. Each leaf contributes one path string of
        node TYPE names from the (Module-stripped) root down to it. e.g. `x = a + b` ->
        {"Assign/Name":1, "Assign/BinOp/Name":2, "Assign/BinOp/Add":1}. Expression
        contexts (Load/Store/Del) are ignored so Name is a leaf. Returns a Counter."""
        try:
            tree = ast.parse(code)
        except (SyntaxError, ValueError):
            return Counter()
        out = Counter()

        def rec(node, prefix):
            kids = [c for c in ast.iter_child_nodes(node)
                    if not isinstance(c, ast.expr_context)]
            pref = prefix if isinstance(node, ast.Module) else prefix + [type(node).__name__]
            if not kids:                       # leaf
                out["/".join(pref)] += 1
            else:
                for c in kids:
                    rec(c, pref)

        rec(tree, [])
        return out

    @staticmethod
    def subtree_size(node):
        """AST node count of a single node's subtree (root included)."""
        return sum(1 for _ in ast.walk(node))

    @staticmethod
    def node_count(code):
        """Total AST nodes of `code` excluding the Module wrapper. 0 if unparsable."""
        try:
            return sum(1 for n in ast.walk(ast.parse(code))
                       if not isinstance(n, ast.Module))
        except (SyntaxError, ValueError):
            return 0

    @staticmethod
    def subtree_sizes(code):
        """Map each expr/stmt subtree's unparse -> its AST node count. {} if unparsable."""
        try:
            tree = ast.parse(code)
        except (SyntaxError, ValueError):
            return {}
        sizes = {}

        def count(n):
            c = 1
            for ch in ast.iter_child_nodes(n):
                c += count(ch)
            if isinstance(n, (ast.expr, ast.stmt)):
                u = AstUtils.safe_unparse(n)
                if u is not None:
                    sizes[u] = c
            return c

        count(tree)
        return sizes

    @staticmethod
    def subtree_sigs(code):
        """Set of expr/stmt subtree unparses (the keys of subtree_sizes). None if
        unparsable -- callers distinguish that from 'no subtrees'."""
        try:
            tree = ast.parse(code)
        except (SyntaxError, ValueError):
            return None
        out = set()
        for n in ast.walk(tree):
            if isinstance(n, (ast.expr, ast.stmt)):
                u = AstUtils.safe_unparse(n)
                if u is not None:
                    out.add(u)
        return out
