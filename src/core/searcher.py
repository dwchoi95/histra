from __future__ import annotations

import ast
import builtins
import re
from typing import Dict
from apted import APTED, Config
from src.utils import Node

_TOK = re.compile(r"[A-Za-z_]\w*|\d+|\S")


class NConfig(Config):
    @staticmethod
    def _hole_type(node):
        name = getattr(node, "name", "")
        if isinstance(name, str) and name.startswith("Hole:"):
            return name.split(":", 1)[1]
        return None

    def rename(self, a, b):
        a_hole = self._hole_type(a)
        b_hole = self._hole_type(b)
        if a_hole is not None and b_hole is not None:
            return 0 if a_hole == b_hole else 1
        if a_hole is not None:
            return 0 if type(b.node).__name__ == a_hole else 1
        if b_hole is not None:
            return 0 if type(a.node).__name__ == b_hole else 1
        return 0 if a.name == b.name else 1


class Searcher:
    def __init__(
        self,
        refs: list[str],
        anchor: tuple[ast.AST, ast.AST],
        top_k: int = 10,
        prefilter_k: int | None = None,
        hole_only: bool = False,
        stmt_prefilter_k: int = 8,
        cluster_mode: str | None = None,
        cluster_threshold: float = 0.45,
    ):
        self.refs_src = refs
        _, self.anchor_org = anchor
        self.ref_asts = [ast.parse(code) for code in refs]
        self.ref_roots_list = [[r for r in self._stmts(R)] for R in self.ref_asts]
        self.top_k = min(top_k, len(self.ref_asts)) if self.ref_asts else 0
        self.prefilter_k = (
            min(prefilter_k, len(self.ref_asts))
            if prefilter_k is not None and self.ref_asts else None
        )
        self._bag_cache = {}
        self.ref_tokens = [
            self._tokens(code) | self._ast_tokens(tree)
            for code, tree in zip(refs, self.ref_asts)
        ]
        self.ref_bags = [
            self._code_bag(code, tree)
            for code, tree in zip(refs, self.ref_asts)
        ]
        self.ref_sizes = [self._size(tree) for tree in self.ref_asts]
        self.ref_shape_nodes = [self._shape_node(tree) for tree in self.ref_asts]
        self.ref_shape_sizes = [self._node_tree_size(node) for node in self.ref_shape_nodes]
        self.hole_only = hole_only
        self.stmt_prefilter_k = stmt_prefilter_k
        self.cluster_mode = cluster_mode
        self.cluster_threshold = cluster_threshold
        self.cluster_count = 0
        self.selected_cluster_size = 0
        self._ranked = None
        self._clusters = None

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
                if self._is_hole(n):
                    continue
                if n.id in dir(builtins):
                    continue
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
        pa = self._var_profiles(anchor)
        pr = self._var_profiles(refer)
        ref_names = list(pr.keys())
        anchor_names = list(pa.keys())
        nr, na = len(ref_names), len(anchor_names)
        if nr == 0 or na == 0:
            return {}
        sim = [[self._vcos(pr[ref_names[i]], pa[anchor_names[j]]) for j in range(na)] for i in range(nr)]
        n = max(nr, na)
        cost = [[1.0 for _ in range(n)] for _ in range(n)]
        for i in range(nr):
            for j in range(na):
                cost[i][j] = 1.0 - sim[i][j]
        assign = self._hungarian(cost)
        vm = {}
        for i in range(nr):
            j = assign[i]
            if j < na and (1.0 - cost[i][j]) > 0.0:
                vm[ref_names[i]] = anchor_names[j]
        return vm

    def _hungarian(self, cost: list[list[float]]) -> list[int]:
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

    # ---------------- Hole helpers and stmt enumeration ----------------
    def _is_hole(self, n: ast.AST) -> bool:
        return isinstance(n, ast.AST) and getattr(n, "_hole", False)

    def _hole_type(self, n: ast.AST) -> str | None:
        if not self._is_hole(n):
            return None
        return getattr(n, "_hole_type", type(n).__name__)

    def _stmts(self, tree: ast.AST):
        return [n for n in ast.walk(tree) if isinstance(n, ast.stmt)]

    def _repair_roots(self, tree: ast.AST):
        if not self.hole_only:
            return self._stmts(tree)
        roots = [
            n for n in ast.walk(tree)
            if isinstance(n, ast.stmt)
            and any(getattr(c, "_hole", False) for c in ast.walk(n))
        ]
        return roots or self._stmts(tree)

    def _size(self, n: ast.AST) -> int:
        return sum(1 for _ in ast.walk(n))

    def _node_bag(self, n: ast.AST) -> dict[str, int]:
        cached = self._bag_cache.get(id(n))
        if cached is not None:
            return cached
        bag = {}
        for child in ast.walk(n):
            keys = ["t:" + type(child).__name__]
            if isinstance(child, ast.Name):
                keys.append("id:" + child.id.lower())
            elif isinstance(child, ast.arg):
                keys.append("id:" + child.arg.lower())
            elif isinstance(child, ast.Constant):
                keys.append("const:" + type(child.value).__name__)
            elif isinstance(child, ast.operator):
                keys.append("op:" + type(child).__name__)
            elif isinstance(child, ast.cmpop):
                keys.append("cmp:" + type(child).__name__)
            elif isinstance(child, ast.boolop):
                keys.append("bool:" + type(child).__name__)
            for key in keys:
                bag[key] = bag.get(key, 0) + 1
        self._bag_cache[id(n)] = bag
        return bag

    def _bag_cos(self, a: dict[str, int], b: dict[str, int]) -> float:
        keys = set(a) & set(b)
        num = sum(a[k] * b[k] for k in keys)
        da = sum(v * v for v in a.values()) ** 0.5
        db = sum(v * v for v in b.values()) ** 0.5
        return num / (da * db) if da and db else 0.0

    def _code_bag(self, code: str, tree: ast.AST) -> dict[str, int]:
        bag = self._node_bag(tree).copy()
        for tok in _TOK.findall(code or ""):
            key = "lex:" + (tok.lower() if tok.isidentifier() else tok)
            bag[key] = bag.get(key, 0) + 1
        return bag

    def _tokens(self, code: str) -> set[str]:
        return {tok.lower() if tok.isidentifier() else tok for tok in _TOK.findall(code or "")}

    def _ast_tokens(self, tree: ast.AST) -> set[str]:
        tokens = set()
        for node in ast.walk(tree):
            tokens.add("t:" + type(node).__name__)
            if isinstance(node, ast.Name):
                tokens.add("id:" + node.id.lower())
            elif isinstance(node, ast.arg):
                tokens.add("id:" + node.arg.lower())
            elif isinstance(node, ast.Constant):
                tokens.add("const:" + type(node.value).__name__)
            elif isinstance(node, ast.operator):
                tokens.add("op:" + type(node).__name__)
            elif isinstance(node, ast.cmpop):
                tokens.add("cmp:" + type(node).__name__)
            elif isinstance(node, ast.boolop):
                tokens.add("bool:" + type(node).__name__)
        return tokens

    def _cheap_ref_indices(self, skt_org: ast.AST) -> list[int]:
        if self.prefilter_k is None or self.prefilter_k >= len(self.ref_asts):
            return list(range(len(self.ref_asts)))
        try:
            bug_code = ast.unparse(skt_org)
        except Exception:
            bug_code = ""
        bug_tokens = self._tokens(bug_code) | self._ast_tokens(skt_org)
        bug_bag = self._node_bag(skt_org).copy()
        for tok in _TOK.findall(bug_code or ""):
            key = "lex:" + (tok.lower() if tok.isidentifier() else tok)
            bug_bag[key] = bug_bag.get(key, 0) + 1
        scored = []
        for idx, tokens in enumerate(self.ref_tokens):
            inter = len(bug_tokens & tokens)
            union = len(bug_tokens | tokens) or 1
            overlap = inter / (len(bug_tokens) or 1)
            jaccard = inter / union
            bag_score = self._bag_cos(bug_bag, self.ref_bags[idx])
            scored.append((0.90 * bag_score + 0.07 * overlap + 0.03 * jaccard, idx))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [idx for _, idx in scored[: self.prefilter_k]]

    def _candidate_ref_indices(self, skt_org: ast.AST) -> list[int]:
        if self.cluster_mode == "apted":
            return self._cluster_ref_indices(skt_org)
        return self._cheap_ref_indices(skt_org)

    def _cluster_ref_indices(self, skt_org: ast.AST) -> list[int]:
        clusters = self._ref_clusters()
        if not clusters:
            self.cluster_count = 0
            self.selected_cluster_size = 0
            return []
        self.cluster_count = len(clusters)
        scored = []
        bug_shape = self._shape_node(skt_org)
        bug_shape_size = self._node_tree_size(bug_shape)
        for cluster in clusters:
            rep_idx = cluster[0]
            size_score = abs(bug_shape_size - self.ref_shape_sizes[rep_idx])
            dist = self._node_dist(bug_shape, self.ref_shape_nodes[rep_idx])
            norm = dist / max(bug_shape_size, self.ref_shape_sizes[rep_idx], 1)
            scored.append((norm, size_score, cluster))
        scored.sort(key=lambda item: (item[0], item[1]))
        selected = list(scored[0][2])
        self.selected_cluster_size = len(selected)
        return selected

    def _ref_clusters(self) -> list[list[int]]:
        if self._clusters is not None:
            return self._clusters
        clusters: list[list[int]] = []
        reps: list[int] = []
        for idx, tree in enumerate(self.ref_asts):
            size = self.ref_shape_sizes[idx]
            best_cluster = None
            best_norm = float("inf")
            for cluster_idx, rep_idx in enumerate(reps):
                rep_size = self.ref_shape_sizes[rep_idx]
                ratio = size / rep_size if rep_size else 1.0
                if ratio < 0.55 or ratio > 1.85:
                    continue
                dist = self._node_dist(self.ref_shape_nodes[idx], self.ref_shape_nodes[rep_idx])
                norm = dist / max(size, rep_size, 1)
                if norm < best_norm:
                    best_norm = norm
                    best_cluster = cluster_idx
            if best_cluster is not None and best_norm <= self.cluster_threshold:
                clusters[best_cluster].append(idx)
            else:
                reps.append(idx)
                clusters.append([idx])
        self._clusters = clusters
        return clusters
    

    # --------- Fine alignment helpers (APTED label=type, holes cost 0) ---------
    def _label_for(self, n: ast.AST) -> str:
        if self._is_hole(n):
            return f"Hole:{self._hole_type(n)}"
        fields = []
        for name, value in ast.iter_fields(n):
            if isinstance(value, ast.AST):
                continue
            if isinstance(value, list) and any(isinstance(item, ast.AST) for item in value):
                continue
            if name == "ctx":
                continue
            fields.append((name, value))
        return repr((type(n).__name__, tuple(fields)))
        
    def _node(self, n: ast.AST):
        return Node(self._label_for(n), [self._node(c) for c in ast.iter_child_nodes(n)], n)

    def _apted_dist(self, a: ast.AST, b: ast.AST) -> int:
        A = self._node(a)
        B = self._node(b)
        return self._node_dist(A, B)

    def _node_dist(self, a: Node, b: Node) -> int:
        return APTED(a, b, NConfig()).compute_edit_distance()

    def _shape_node(self, n: ast.AST, depth: int = 5, width: int = 8):
        if depth <= 0:
            return Node("...", [], n)
        children = list(ast.iter_child_nodes(n))[:width]
        return Node(
            type(n).__name__,
            [self._shape_node(child, depth - 1, width) for child in children],
            n,
        )

    def _node_tree_size(self, node: Node) -> int:
        return 1 + sum(self._node_tree_size(child) for child in node.children)

    def _best_map_for_ref(self, bug_roots, ref_roots):
        node_map = {}
        total_dist = 0
        for s in bug_roots:
            ss = self._size(s)
            sbag = self._node_bag(s)
            cands = []
            for r in ref_roots:
                if type(r) is not type(s): continue
                sr = self._size(r)
                if sr == 0 or ss == 0: continue
                ratio = sr / ss
                if 0.5 <= ratio <= 2.0:
                    size_score = min(ss, sr) / max(ss, sr)
                    sim = 0.7 * self._bag_cos(sbag, self._node_bag(r)) + 0.3 * size_score
                    cands.append((sim, sr, r))
            
            if cands:
                cands.sort(key=lambda item: item[0], reverse=True)
                cands = cands[: self.stmt_prefilter_k]
                max_sr = 0
                min_dist = float('inf')
                best_pairs = []
                for _, sr, r in cands:
                    dist = self._apted_dist(s, r)
                    if dist < min_dist:
                        max_sr = sr
                        min_dist = dist
                        best_pairs = [r]
                    elif dist == min_dist:
                        if sr > max_sr:
                            max_sr = sr
                            best_pairs = [r]
                        elif sr == max_sr:
                            best_pairs.append(r)
                
                if not best_pairs: best_pairs = list(cands.values())
                # B4: deterministic tie-break (source order) instead of random.choice,
                # so every A/B below is single-shot reproducible (no RR change expected).
                node_map[id(s)] = best_pairs[0]
                total_dist += min_dist
            else:
                total_dist += ss

        return total_dist, node_map

    def _rank_refs(self, skt_org: ast.AST):
        if self._ranked is not None:
            return self._ranked
        bug_roots = [s for s in self._repair_roots(skt_org)]
        ranked = []
        for idx in self._candidate_ref_indices(skt_org):
            ref_roots = self.ref_roots_list[idx]
            dist, _ = self._best_map_for_ref(bug_roots, ref_roots)
            ranked.append((dist, idx))
        ranked.sort(key=lambda x: x[0])
        self._ranked = ranked[:self.top_k]
        return self._ranked

    def __len__(self):
        if self.cluster_mode == "apted":
            return self.top_k
        if self.prefilter_k is None:
            return self.top_k
        return min(self.top_k, self.prefilter_k)

    def run(self, skt_org: ast.AST, rank: int = 0):
        ranked = self._rank_refs(skt_org)
        if not ranked or rank >= len(ranked):
            return {}, {}
        _, ref_idx = ranked[rank]
        bug_roots = [s for s in self._repair_roots(skt_org)]
        _, node_map = self._best_map_for_ref(bug_roots, self.ref_roots_list[ref_idx])
        var_map = self._varmap_defuse(skt_org, self.ref_asts[ref_idx])
        return node_map, var_map
