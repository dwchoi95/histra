import ast
import copy
import random
from typing import Dict
from apted import APTED, Config


class Node:
    __slots__ = ("name", "children", "node")

    def __init__(self, name, children, node):
        self.name = name
        self.children = children
        self.node = node


class NConfig(Config):
    def rename(self, a, b):
        if a.name == "Hole" or b.name == "Hole":
            return 0
        return 0 if a.name == b.name else 1

    def insert(self, node):
        return 0 if node.name == "Hole" else 1

    def delete(self, node):
        return 0 if node.name == "Hole" else 1

class Searcher:
    def __init__(self, refs:list[str], anchor:tuple[ast.AST, ast.AST]):
        self.refs_src = refs
        _, anchor_org = anchor
        parsed = [ast.parse(code) for code in refs]
        ref_asts = [self._rename_vars(r, self._varmap_defuse(anchor_org, r)) for r in parsed]
        self.ref_roots_list = [[r for r in self._stmts(R)] for R in ref_asts]

    # ---------------- Var mapping helpers (def-use profiles + greedy matching) ----------------
    
    def _parent_map(self, tree: ast.AST) -> Dict[ast.AST, ast.AST]:
        pm = {}
        for p in ast.walk(tree):
            for c in ast.iter_child_nodes(p):
                pm[c] = p
        return pm

    def _var_profiles(self, tree: ast.AST) -> Dict[str, Dict[str, int]]:
        pm = self._parent_map(tree)
        prof: Dict[str, Dict[str, int]] = {}
        for n in ast.walk(tree):
            if isinstance(n, ast.Name):
                d = prof.setdefault(n.id, {"store": 0, "load": 0})
                d["store" if isinstance(n.ctx, ast.Store) else "load"] += 1
                par = pm.get(n)
                if par is not None:
                    key = "p:" + type(par).__name__
                    d[key] = d.get(key, 0) + 1
                    g = pm.get(par)
                    if g is not None:
                        gk = "g:" + type(g).__name__
                        d[gk] = d.get(gk, 0) + 1
        return prof

    def _vcos(self, a: Dict[str, int], b: Dict[str, int]) -> float:
        ks = set(a) & set(b)
        num = sum(a[k] * b[k] for k in ks)
        da = sum(v * v for v in a.values()) ** 0.5
        db = sum(v * v for v in b.values()) ** 0.5
        return num / (da * db) if da and db else 0.0

    def _varmap_defuse(self, anchor: ast.AST, refer: ast.AST) -> Dict[str, str]:
        """Build a 1:1 var mapping (ref -> anchor) using Hungarian assignment
        on cosine similarities of def-use profiles. Pads to square with dummy costs.
        """
        pa = self._var_profiles(anchor)
        pr = self._var_profiles(refer)
        Ra = list(pr.keys())
        Aa = list(pa.keys())
        nr, na = len(Ra), len(Aa)
        if nr == 0 or na == 0:
            return {}
        # build similarity matrix (rows=ref vars, cols=anchor vars)
        sim = [[self._vcos(pr[Ra[i]], pa[Aa[j]]) for j in range(na)] for i in range(nr)]
        # convert to cost; pad to square with cost=1 (i.e., sim=0)
        n = max(nr, na)
        cost = [[1.0 for _ in range(n)] for _ in range(n)]
        for i in range(nr):
            for j in range(na):
                cost[i][j] = 1.0 - sim[i][j]

        assign = self._hungarian(cost)  # list of length n: col index for each row
        vm: Dict[str, str] = {}
        for i in range(nr):
            j = assign[i]
            if j < na and (1.0 - cost[i][j]) > 0.0:  # sim > 0
                vm[Ra[i]] = Aa[j]
        return vm

    def _hungarian(self, cost: list[list[float]]) -> list[int]:
        """Hungarian algorithm for square cost matrix (min). Returns assignment col per row."""
        n = len(cost)
        u = [0.0] * (n + 1)
        v = [0.0] * (n + 1)
        p = [0] * (n + 1)
        way = [0] * (n + 1)
        for i in range(1, n + 1):
            p[0] = i
            j0 = 0
            minv = [float('inf')] * (n + 1)
            used = [False] * (n + 1)
            while True:
                used[j0] = True
                i0 = p[j0]
                delta = float('inf')
                j1 = 0
                for j in range(1, n + 1):
                    if used[j]:
                        continue
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j
                for j in range(0, n + 1):
                    if used[j]:
                        u[p[j]] += delta
                        v[j] -= delta
                    else:
                        minv[j] -= delta
                j0 = j1
                if p[j0] == 0:
                    break
            while True:
                j1 = way[j0]
                p[j0] = p[j1]
                j0 = j1
                if j0 == 0:
                    break
        assign = [0] * n
        for j in range(1, n + 1):
            if p[j] != 0:
                assign[p[j] - 1] = j - 1
        return assign

    def _rename_vars(self, tree: ast.AST, vm: Dict[str, str]) -> ast.AST:
        t = copy.deepcopy(tree)

        class R(ast.NodeTransformer):
            def visit_Name(self, n: ast.Name):
                if n.id in vm:
                    return ast.copy_location(ast.Name(id=vm[n.id], ctx=n.ctx), n)
                return n

            def visit_arg(self, n: ast.arg):
                if n.arg in vm:
                    n.arg = vm[n.arg]
                return n

        return R().visit(t)

    # ---------------- Hole helpers and stmt enumeration ----------------
    def _is_hole_name(self, n: ast.AST) -> bool:
        return isinstance(n, ast.Name) and isinstance(n.id, str) and n.id.startswith("__HOLE_")

    def _stmts(self, tree: ast.AST):
        return [n for n in ast.walk(tree) if isinstance(n, ast.stmt)]

    def _size(self, n: ast.AST) -> int:
        return sum(1 for _ in ast.walk(n))
    

    # --------- Fine alignment helpers (APTED label=type, holes cost 0) ---------
    def _label_for(self, n: ast.AST) -> str:
        if self._is_hole_name(n):
            return "Hole"
        return type(n).__name__
        
    def _node(self, n: ast.AST):
        return Node(self._label_for(n), [self._node(c) for c in ast.iter_child_nodes(n)], n)

    def _apted_dist(self, a: ast.AST, b: ast.AST) -> int:
        A = self._node(a)
        B = self._node(b)
        return APTED(A, B, NConfig()).compute_edit_distance()

    def run(self, skt_org: ast.AST):
        bug_roots = [s for s in self._stmts(skt_org)]
        node_map = {}
        for s in bug_roots:
            ss = self._size(s)
            cands = []
            for ref_roots in self.ref_roots_list:
                for r in ref_roots:
                    if type(r) is not type(s): continue
                    sr = self._size(r)
                    if sr == 0 or ss == 0: continue
                    ratio = sr / ss
                    if 0.5 <= ratio <= 2.0:
                        cands.append(r)
            
            if cands:
                min_dist = float('inf')
                best_pairs = []
                for r in cands:
                    dist = self._apted_dist(s, r)
                    if dist < min_dist:
                        min_dist = dist
                        best_pairs = [r]
                    elif dist == min_dist:
                        best_pairs.append(r)

                if not best_pairs: best_pairs = cands
                node_map[id(s)] = random.choice(best_pairs)

        return node_map
