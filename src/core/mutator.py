from __future__ import annotations

import ast
import builtins
import copy
import os
import re
from collections import defaultdict
from typing import Iterable


_TOK = re.compile(r"[A-Za-z_]\w*|\d+|\S")
_BUILTINS = set(dir(builtins))


class LocalMutator:
    """Generate small, style-preserving repairs around sketched holes.

    This is intentionally conservative: candidates are edits to the latest
    buggy program, not wholesale donor-program transplants.
    """

    EXPR_TYPES = (
        ast.BinOp,
        ast.BoolOp,
        ast.Call,
        ast.Compare,
        ast.Constant,
        ast.Dict,
        ast.IfExp,
        ast.List,
        ast.Set,
        ast.Subscript,
        ast.Tuple,
        ast.UnaryOp,
    )
    SIMPLE_STMTS = (
        ast.Assign,
        ast.AnnAssign,
        ast.AugAssign,
        ast.Expr,
        ast.If,
        ast.Return,
    )
    MAX_EXPR_SIZE = 45
    MAX_STMT_SIZE = 70

    def __init__(
        self,
        traj: list[str],
        refs: list[str],
        sketch: ast.AST,
        max_refs: int = 40,
        max_exprs_per_type: int = 60,
        max_candidates: int = 160,
        general_only: bool = False,
        use_refs: bool = True,
        use_history_sources: bool = True,
    ):
        self.traj = traj or []
        self.refs = refs or []
        self.sketch = sketch
        self.max_refs = max_refs
        self.max_exprs_per_type = max_exprs_per_type
        self.max_candidates = max_candidates
        self.general_only = general_only
        self.use_refs = use_refs
        self.use_history_sources = use_history_sources
        self.current_names = self._all_names(sketch)
        try:
            self.anchor_code = ast.unparse(sketch)
        except Exception:
            self.anchor_code = self.traj[-1] if self.traj else ""
        self.anchor_input_names = self._input_target_names(sketch)
        self.expr_pool, self.stmt_pool = self._build_pools()

    def generate(self) -> Iterable[str]:
        seen: set[str] = set()
        emitted = 0

        def emit(tree: ast.AST):
            nonlocal emitted
            if emitted >= self.max_candidates:
                return None
            try:
                ast.fix_missing_locations(tree)
                code = ast.unparse(tree)
                compile(code, "<histra-local>", "exec")
            except Exception:
                return None
            if code in seen:
                return None
            seen.add(code)
            emitted += 1
            return code

        # The latest WA can occasionally pass the public oracle tests after
        # normalization; keep it as the zero-edit candidate.
        zero = emit(copy.deepcopy(self.sketch))
        if zero is not None:
            yield zero

        for tree in self._trajectory_replay_candidates():
            if emitted >= self.max_candidates:
                return
            cand = emit(tree)
            if cand is not None:
                yield cand

        for tree in self._donor_delta_candidates():
            if emitted >= self.max_candidates:
                return
            cand = emit(tree)
            if cand is not None:
                yield cand

        structural_candidates = (
            self._generic_structural_candidates()
            if self.general_only
            else self._all_structural_candidates()
        )
        for tree in structural_candidates:
            if emitted >= self.max_candidates:
                return
            cand = emit(tree)
            if cand is not None:
                yield cand

        if not self.general_only:
            for tree in self._indent_following_candidates():
                if emitted >= self.max_candidates:
                    return
                cand = emit(tree)
                if cand is not None:
                    yield cand

            for tree in self._decimal_scale_candidates():
                if emitted >= self.max_candidates:
                    return
                cand = emit(tree)
                if cand is not None:
                    yield cand

        local_edits = list(self._local_edits())
        branch_edits = list(self._branch_edits())
        expr_edits = list(self._expr_edits())
        stmt_edits = list(self._stmt_edits())

        # Single edits first: these best match the intent-preserving objective.
        # Statement donors are tried before generic expression donors because
        # many trajectory bugs require replacing an enclosing branch, not just
        # one arithmetic subexpression.
        for edit in local_edits + branch_edits + stmt_edits + expr_edits:
            if emitted >= self.max_candidates:
                return
            cand = emit(self._apply_edits([edit]))
            if cand is not None:
                yield cand

        # Try a small number of two-edit combinations for bugs with coupled
        # changes, but avoid statement combinations because they change shape.
        pairable = local_edits + branch_edits + expr_edits
        pair_budget = min(len(pairable), 20)
        for i in range(pair_budget):
            for j in range(i + 1, pair_budget):
                if emitted >= self.max_candidates:
                    return
                if self._paths_conflict(pairable[i][0], pairable[j][0]):
                    continue
                cand = emit(self._apply_edits([pairable[i], pairable[j]]))
                if cand is not None:
                    yield cand

        # Previous attempts are student-authored and often represent a good
        # fallback style, but they can be slow to validate. Try them after the
        # small localized edits.
        for code in reversed(self.traj[:-1]):
            if emitted >= self.max_candidates:
                return
            try:
                tree = ast.parse(code)
            except Exception:
                continue
            cand = emit(tree)
            if cand is not None:
                yield cand

    def _source_codes(self) -> list[str]:
        codes = list(reversed(self.traj[:-1])) if self.use_history_sources else []
        refs = (
            sorted(self.refs, key=self._token_score, reverse=True)[: self.max_refs]
            if self.use_refs
            else []
        )
        codes.extend(refs)
        return codes

    def _token_score(self, code: str) -> float:
        a = set(_TOK.findall(self.anchor_code))
        b = set(_TOK.findall(code or ""))
        return len(a & b) / (len(a | b) or 1)

    def _build_pools(self):
        expr_pool: dict[type, list[ast.expr]] = defaultdict(list)
        stmt_pool: dict[type, list[ast.stmt]] = defaultdict(list)
        expr_seen: set[tuple[type, str]] = set()
        stmt_seen: set[tuple[type, str]] = set()

        for code in self._source_codes():
            try:
                tree = ast.parse(code)
            except Exception:
                continue
            tree = self._rename_input_vars(tree)
            for node in ast.walk(tree):
                if isinstance(node, self.EXPR_TYPES):
                    if self._size(node) > self.MAX_EXPR_SIZE:
                        continue
                    if not self._names_compatible(node):
                        continue
                    key = (type(node), ast.dump(node, include_attributes=False))
                    if key in expr_seen:
                        continue
                    bucket = expr_pool[type(node)]
                    if len(bucket) >= self.max_exprs_per_type:
                        continue
                    expr_seen.add(key)
                    bucket.append(copy.deepcopy(node))
                elif isinstance(node, self.SIMPLE_STMTS):
                    if self._size(node) > self.MAX_STMT_SIZE:
                        continue
                    if not self._names_compatible(node):
                        continue
                    key = (type(node), ast.dump(node, include_attributes=False))
                    if key in stmt_seen:
                        continue
                    stmt_seen.add(key)
                    stmt_pool[type(node)].append(copy.deepcopy(node))

        return expr_pool, stmt_pool

    def _expr_edits(self):
        for path, node in self._hole_nodes(ast.expr):
            if not isinstance(node, self.EXPR_TYPES):
                continue
            if self._is_store_context(node):
                continue
            for donor in self.expr_pool.get(type(node), [])[:20]:
                if ast.dump(node, include_attributes=False) == ast.dump(donor, include_attributes=False):
                    continue
                yield path, self._with_ctx(copy.deepcopy(donor), node)

    def _stmt_edits(self):
        for path, node in self._hole_containing_stmts():
            if not isinstance(node, self.SIMPLE_STMTS):
                continue
            for donor in self.stmt_pool.get(type(node), [])[: self._stmt_donor_limit(path, node)]:
                if ast.dump(node, include_attributes=False) == ast.dump(donor, include_attributes=False):
                    continue
                yield path, copy.deepcopy(donor)

    def _stmt_donor_limit(self, path, node: ast.AST) -> int:
        if (
            isinstance(node, ast.If)
            and len(path) == 1
            and self._size(self.sketch) <= 180
            and len(self.anchor_input_names) <= 3
        ):
            return 140
        return 12

    def _branch_edits(self):
        for path, node in self._hole_containing_stmts():
            if not isinstance(node, ast.If) or node.orelse:
                continue
            for donor in self.stmt_pool.get(ast.If, [])[:80]:
                if not donor.orelse:
                    continue
                if not self._same_expr(node.test, donor.test):
                    continue
                repl = copy.deepcopy(node)
                repl.orelse = copy.deepcopy(donor.orelse)
                if not self._names_compatible(repl):
                    continue
                yield path, repl

    def _donor_delta_candidates(self):
        """Project small AST deltas from nearby donor statements.

        Unlike the structural helpers below, this does not encode a repair
        template. It aligns the current hole-containing statement with similar
        statements from the trajectory/AC pool and replays only the differing
        subexpressions near the sketched hole.
        """
        hole_stmts = list(self._hole_containing_stmts())
        if len(hole_stmts) > 6:
            return
        emitted = 0
        for stmt_path, stmt in hole_stmts:
            if not isinstance(stmt, self.SIMPLE_STMTS):
                continue
            donors = self._ranked_stmt_donors(stmt)[:10]
            for donor in donors:
                diffs = self._stmt_delta_edits(stmt_path, stmt, donor)[:5]
                for edit in diffs:
                    yield self._apply_edits([edit])
                    emitted += 1
                    if emitted >= 18:
                        return
                pair_limit = min(len(diffs), 3)
                for i in range(pair_limit):
                    for j in range(i + 1, pair_limit):
                        if self._paths_conflict(diffs[i][0], diffs[j][0]):
                            continue
                        yield self._apply_edits([diffs[i], diffs[j]])
                        emitted += 1
                        if emitted >= 18:
                            return

    def _ranked_stmt_donors(self, stmt: ast.stmt) -> list[ast.stmt]:
        donors = self.stmt_pool.get(type(stmt), [])
        if not donors:
            return []
        scored = []
        for donor in donors:
            if ast.dump(stmt, include_attributes=False) == ast.dump(donor, include_attributes=False):
                continue
            scored.append((self._stmt_similarity(stmt, donor), donor))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [donor for score, donor in scored if score > 0.25]

    def _stmt_similarity(self, left: ast.AST, right: ast.AST) -> float:
        left_names = self._load_names(left)
        right_names = self._load_names(right)
        name_union = left_names | right_names
        name_score = len(left_names & right_names) / len(name_union) if name_union else 0.4
        left_types = self._type_bag(left)
        right_types = self._type_bag(right)
        type_score = self._bag_cos(left_types, right_types)
        size_ratio = min(self._size(left), self._size(right)) / max(self._size(left), self._size(right), 1)
        return 0.50 * type_score + 0.30 * name_score + 0.20 * size_ratio

    def _stmt_delta_edits(self, stmt_path, stmt: ast.stmt, donor: ast.stmt):
        target_nodes = dict(self._iter_nodes(stmt))
        donor_nodes = dict(self._iter_nodes(donor))
        edits = []
        for rel_path in set(target_nodes) & set(donor_nodes):
            if not rel_path:
                continue
            old = target_nodes[rel_path]
            new = donor_nodes[rel_path]
            if not self._delta_replayable(old, new):
                continue
            if not self._near_hole(target_nodes, rel_path):
                continue
            score = self._delta_score(target_nodes, rel_path, old, new)
            edits.append((score, stmt_path + rel_path, copy.deepcopy(new)))
        edits.sort(key=lambda item: item[0])
        out = []
        seen = set()
        for _, path, node in edits:
            key = (path, ast.dump(node, include_attributes=False))
            if key in seen:
                continue
            seen.add(key)
            out.append((path, node))
        return out

    def _delta_replayable(self, old: ast.AST, new: ast.AST) -> bool:
        if type(old) is not type(new):
            return False
        if ast.dump(old, include_attributes=False) == ast.dump(new, include_attributes=False):
            return False
        if self._is_store_context(old) or self._is_store_context(new):
            return False
        if not self._names_compatible(new):
            return False
        if isinstance(old, ast.expr):
            return self._size(old) <= 45 and self._size(new) <= 45
        if isinstance(old, ast.comprehension):
            return self._size(old) <= 35 and self._size(new) <= 35
        return False

    def _near_hole(self, nodes: dict, rel_path) -> bool:
        node = nodes.get(rel_path)
        if node is not None and self._has_hole(node):
            return True
        for path, candidate in nodes.items():
            if not self._has_hole(candidate):
                continue
            if path[: len(rel_path)] == rel_path or rel_path[: len(path)] == path:
                return True
        return False

    def _delta_score(self, nodes: dict, rel_path, old: ast.AST, new: ast.AST):
        hole_distance = min(
            (
                abs(len(rel_path) - len(path))
                for path, node in nodes.items()
                if self._has_hole(node)
                and (path[: len(rel_path)] == rel_path or rel_path[: len(path)] == path)
            ),
            default=4,
        )
        name_union = self._load_names(old) | self._load_names(new)
        name_gap = 1.0
        if name_union:
            name_gap = 1.0 - (len(self._load_names(old) & self._load_names(new)) / len(name_union))
        return (hole_distance, self._size(new), name_gap)

    def _trajectory_replay_candidates(self):
        ops = self._trajectory_edit_ops()
        emitted = 0
        seen_ops = set()
        for op in ops:
            key = self._op_key(op)
            if key in seen_ops:
                continue
            seen_ops.add(key)
            if op["kind"] == "replace":
                for tree in self._replay_replace(op):
                    yield tree
                    emitted += 1
                    if emitted >= 24:
                        return
            elif op["kind"] == "insert":
                for tree in self._replay_insert(op):
                    yield tree
                    emitted += 1
                    if emitted >= 24:
                        return
            elif op["kind"] == "delete":
                for tree in self._replay_delete(op):
                    yield tree
                    emitted += 1
                    if emitted >= 24:
                        return

    def _trajectory_edit_ops(self) -> list[dict]:
        ops = []
        trees = []
        for code in self.traj:
            try:
                trees.append(ast.parse(code))
            except Exception:
                continue
        for before, after in zip(trees, trees[1:]):
            before_nodes = dict(self._iter_nodes(before))
            after_nodes = dict(self._iter_nodes(after))
            for path in sorted(set(before_nodes) & set(after_nodes), key=len):
                old = before_nodes[path]
                new = after_nodes[path]
                if not self._replayable_replace(old, new):
                    continue
                ops.append({
                    "kind": "replace",
                    "path": path,
                    "old": copy.deepcopy(old),
                    "new": copy.deepcopy(new),
                })
            ops.extend(self._list_edit_ops(before, after))
        ops.sort(key=self._op_score)
        return ops[:80]

    def _replayable_replace(self, old: ast.AST, new: ast.AST) -> bool:
        if type(old) is not type(new):
            return False
        if isinstance(old, ast.Module):
            return False
        if ast.dump(old, include_attributes=False) == ast.dump(new, include_attributes=False):
            return False
        if isinstance(old, ast.expr):
            return self._size(old) <= 55 and self._size(new) <= 55
        if isinstance(old, self.SIMPLE_STMTS):
            return self._size(old) <= 95 and self._size(new) <= 95
        return False

    def _list_edit_ops(self, before: ast.AST, after: ast.AST) -> list[dict]:
        ops = []
        before_lists = self._list_fields(before)
        after_lists = self._list_fields(after)
        for key in set(before_lists) & set(after_lists):
            old_items = before_lists[key]
            new_items = after_lists[key]
            if not old_items and not new_items:
                continue
            if not all(isinstance(item, ast.stmt) for item in old_items + new_items):
                continue
            old_dumps = [ast.dump(item, include_attributes=False) for item in old_items]
            new_dumps = [ast.dump(item, include_attributes=False) for item in new_items]
            if len(new_items) == len(old_items) + 1:
                idx = self._single_insert_index(old_dumps, new_dumps)
                if idx is None:
                    continue
                node = new_items[idx]
                if self._size(node) > 95 or not self._names_compatible(node):
                    continue
                ops.append({
                    "kind": "insert",
                    "parent_path": key[0],
                    "field": key[1],
                    "idx": idx,
                    "node": copy.deepcopy(node),
                    "before": new_dumps[idx + 1] if idx + 1 < len(new_dumps) else "",
                    "after": new_dumps[idx - 1] if idx > 0 else "",
                })
            elif len(old_items) == len(new_items) + 1:
                idx = self._single_insert_index(new_dumps, old_dumps)
                if idx is None:
                    continue
                node = old_items[idx]
                if self._size(node) > 95:
                    continue
                ops.append({
                    "kind": "delete",
                    "parent_path": key[0],
                    "field": key[1],
                    "idx": idx,
                    "target": ast.dump(node, include_attributes=False),
                })
        return ops

    def _single_insert_index(self, shorter: list[str], longer: list[str]) -> int | None:
        i = 0
        inserted = None
        for j, item in enumerate(longer):
            if i < len(shorter) and item == shorter[i]:
                i += 1
                continue
            if inserted is not None:
                return None
            inserted = j
        return inserted if i == len(shorter) else None

    def _list_fields(self, tree: ast.AST):
        out = {}
        for path, node in self._iter_nodes(tree):
            for field, value in ast.iter_fields(node):
                if isinstance(value, list) and all(isinstance(item, ast.AST) for item in value):
                    out[(path, field)] = value
        return out

    def _replay_replace(self, op: dict):
        old = op["old"]
        new = op["new"]
        if not self._names_compatible(new):
            return
        target = self._get_node_at(self.sketch, op["path"])
        if target is not None and self._similar_for_replay(target, old):
            yield self._apply_edits([(op["path"], copy.deepcopy(new))])

        old_dump = ast.dump(old, include_attributes=False)
        yielded = 0
        for path, node in self._iter_nodes(self.sketch):
            if type(node) is not type(old):
                continue
            if ast.dump(node, include_attributes=False) != old_dump:
                continue
            yield self._apply_edits([(path, copy.deepcopy(new))])
            yielded += 1
            if yielded >= 4:
                return

    def _replay_insert(self, op: dict):
        node = op["node"]
        if not self._names_compatible(node):
            return
        inserted = 0
        for parent_path, field, items in self._candidate_lists(op):
            idx = self._insertion_index(items, op)
            if idx is None:
                continue
            tree = copy.deepcopy(self.sketch)
            target_list = self._get_list_at(tree, parent_path, field)
            if target_list is None:
                continue
            target_list.insert(idx, copy.deepcopy(node))
            ast.fix_missing_locations(tree)
            yield tree
            inserted += 1
            if inserted >= 3:
                return

    def _replay_delete(self, op: dict):
        deleted = 0
        for parent_path, field, items in self._candidate_lists(op):
            for idx, item in enumerate(items):
                if ast.dump(item, include_attributes=False) != op["target"]:
                    continue
                tree = copy.deepcopy(self.sketch)
                target_list = self._get_list_at(tree, parent_path, field)
                if target_list is None or idx >= len(target_list):
                    continue
                del target_list[idx]
                ast.fix_missing_locations(tree)
                yield tree
                deleted += 1
                if deleted >= 3:
                    return

    def _candidate_lists(self, op: dict):
        same = self._get_list_at(self.sketch, op["parent_path"], op["field"])
        if same is not None:
            yield op["parent_path"], op["field"], same
        for (parent_path, field), items in self._list_fields(self.sketch).items():
            if field == op["field"] and parent_path != op["parent_path"]:
                yield parent_path, field, items

    def _insertion_index(self, items: list[ast.AST], op: dict) -> int | None:
        dumps = [ast.dump(item, include_attributes=False) for item in items]
        if op["after"] and op["after"] in dumps:
            return dumps.index(op["after"]) + 1
        if op["before"] and op["before"] in dumps:
            return dumps.index(op["before"])
        return min(op["idx"], len(items))

    def _similar_for_replay(self, node: ast.AST, old: ast.AST) -> bool:
        if type(node) is not type(old):
            return False
        if ast.dump(node, include_attributes=False) == ast.dump(old, include_attributes=False):
            return True
        a = self._load_names(node)
        b = self._load_names(old)
        if a and b and len(a & b) / len(a | b) < 0.5:
            return False
        size_ratio = self._size(node) / max(self._size(old), 1)
        return 0.65 <= size_ratio <= 1.55

    def _get_node_at(self, tree: ast.AST, path):
        node = tree
        try:
            for field, idx in path:
                value = getattr(node, field)
                node = value[idx] if idx is not None else value
            return node if isinstance(node, ast.AST) else None
        except Exception:
            return None

    def _op_key(self, op: dict):
        if op["kind"] == "replace":
            return (
                op["kind"],
                type(op["old"]).__name__,
                ast.dump(op["old"], include_attributes=False),
                ast.dump(op["new"], include_attributes=False),
            )
        if op["kind"] == "insert":
            return (
                op["kind"],
                op["field"],
                ast.dump(op["node"], include_attributes=False),
                op["before"],
                op["after"],
            )
        return (op["kind"], op["field"], op["target"])

    def _op_score(self, op: dict):
        if op["kind"] == "replace":
            return (0, self._size(op["old"]) + self._size(op["new"]))
        if op["kind"] == "insert":
            return (1, self._size(op["node"]))
        return (2, len(op["target"]))

    def _same_expr(self, left: ast.AST, right: ast.AST) -> bool:
        return (
            ast.dump(left, include_attributes=False)
            == ast.dump(right, include_attributes=False)
        )

    def _local_edits(self):
        for path, node in self._hole_nodes(ast.expr):
            if isinstance(node, ast.BoolOp):
                for repl in self._boolop_variants(node):
                    yield path, repl
            elif isinstance(node, ast.Compare):
                for repl in self._compare_variants(node):
                    yield path, repl
            elif isinstance(node, ast.BinOp):
                for repl in self._binop_variants(node):
                    yield path, repl
            elif isinstance(node, ast.Call):
                for repl in self._call_variants(node):
                    yield path, repl
            elif isinstance(node, ast.Constant) and isinstance(node.value, int):
                for repl in self._constant_variants(node):
                    yield path, repl

    def _indent_following_candidates(self):
        for path, node in self._iter_nodes(self.sketch):
            if not isinstance(node, ast.If) or not self._has_hole(node):
                continue
            if not path:
                continue
            field, idx = path[-1]
            if idx is None:
                continue
            sibling_path = path[:-1]
            siblings = self._get_list_at(self.sketch, sibling_path, field)
            if siblings is None or idx + 1 >= len(siblings):
                continue
            follower = siblings[idx + 1]
            if not isinstance(follower, (ast.Break, ast.Continue)):
                continue
            tree = copy.deepcopy(self.sketch)
            new_siblings = self._get_list_at(tree, sibling_path, field)
            if new_siblings is None or idx + 1 >= len(new_siblings):
                continue
            moved = new_siblings.pop(idx + 1)
            new_if = new_siblings[idx]
            if not isinstance(new_if, ast.If):
                continue
            new_if.body.append(moved)
            yield tree

    def _decimal_scale_candidates(self):
        if "float" not in self.current_names:
            return
        transformer = _DecimalScaleTransformer()
        tree = transformer.visit(copy.deepcopy(self.sketch))
        if transformer.changed:
            yield tree

    def _generic_structural_candidates(self):
        yield from self._range_start_candidates()
        yield from self._loop_zero_index_candidates()
        yield from self._break_into_preceding_if_candidates()
        yield from self._max_accumulator_candidates()
        yield from self._subscript_minus_one_candidates()
        yield from self._inclusive_compare_candidates()
        yield from self._following_else_candidates()

    def _all_structural_candidates(self):
        yield from self._generic_structural_candidates()
        yield from self._counter_collection_candidates()
        yield from self._leading_zero_guard_candidates()
        yield from self._sqrt_guard_candidates()
        yield from self._integer_formula_candidates()

    def _range_start_candidates(self):
        edits = []
        for path, node in self._iter_nodes(self.sketch):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "range"
                and len(node.args) >= 2
                and isinstance(node.args[0], ast.Constant)
                and node.args[0].value == 1
            ):
                continue
            repl = copy.deepcopy(node)
            if len(repl.args) == 2:
                repl.args = [repl.args[1]]
            else:
                repl.args[0] = ast.copy_location(ast.Constant(value=0), repl.args[0])
            edits.append((path, repl))
        for edit in edits:
            yield self._apply_edits([edit])

    def _loop_zero_index_candidates(self):
        edits = []
        for for_path, for_node in self._iter_nodes(self.sketch):
            if not isinstance(for_node, ast.For) or not isinstance(for_node.target, ast.Name):
                continue
            loop_var = for_node.target.id
            for rel_path, node in self._iter_nodes(for_node):
                if not (
                    isinstance(node, ast.Subscript)
                    and isinstance(node.ctx, ast.Load)
                    and isinstance(node.value, ast.Name)
                    and isinstance(node.slice, ast.Constant)
                    and node.slice.value == 0
                ):
                    continue
                repl = copy.deepcopy(node)
                repl.slice = ast.copy_location(ast.Name(id=loop_var, ctx=ast.Load()), repl.slice)
                edits.append((for_path + rel_path, repl))
        if edits:
            yield self._apply_edits(edits)

    def _break_into_preceding_if_candidates(self):
        for path, node in self._iter_nodes(self.sketch):
            if not isinstance(node, ast.If):
                continue
            if not path:
                continue
            field, idx = path[-1]
            if idx is None:
                continue
            sibling_path = path[:-1]
            siblings = self._get_list_at(self.sketch, sibling_path, field)
            if siblings is None or idx + 1 >= len(siblings):
                continue
            follower = siblings[idx + 1]
            if not isinstance(follower, (ast.Break, ast.Continue)):
                continue
            tree = copy.deepcopy(self.sketch)
            new_siblings = self._get_list_at(tree, sibling_path, field)
            if new_siblings is None or idx + 1 >= len(new_siblings):
                continue
            moved = new_siblings.pop(idx + 1)
            new_if = new_siblings[idx]
            if not isinstance(new_if, ast.If):
                continue
            new_if.body.append(moved)
            yield tree

    def _counter_collection_candidates(self):
        input_names, derived_names = self._collection_lineage()
        if not input_names or not derived_names:
            return
        for path, node in self._iter_nodes(self.sketch):
            if not (
                isinstance(node, ast.Call)
                and self._is_counter_call(node)
                and len(node.args) == 1
                and isinstance(node.args[0], ast.Name)
                and node.args[0].id in derived_names
            ):
                continue
            for input_name in input_names[:2]:
                repl = copy.deepcopy(node)
                repl.args[0] = ast.copy_location(
                    ast.Name(id=input_name, ctx=ast.Load()),
                    repl.args[0],
                )
                yield self._apply_edits([(path, repl)])

    def _max_accumulator_candidates(self):
        for path, node in self._iter_nodes(self.sketch):
            if not (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "max"
                and node.value.args
                and isinstance(node.value.args[0], ast.Constant)
                and node.value.args[0].value == 0
            ):
                continue
            repl = copy.deepcopy(node)
            repl.value.args[0] = ast.copy_location(
                ast.Name(id=node.targets[0].id, ctx=ast.Load()),
                repl.value.args[0],
            )
            yield self._apply_edits([(path, repl)])

        for for_path, for_node in self._iter_nodes(self.sketch):
            if not isinstance(for_node, ast.For) or not for_path:
                continue
            field, idx = for_path[-1]
            if idx is None:
                continue
            sibling_path = for_path[:-1]
            siblings = self._get_list_at(self.sketch, sibling_path, field)
            if siblings is None:
                continue
            for rel_path, node in self._iter_nodes(for_node):
                if not (
                    isinstance(node, ast.Assign)
                    and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                    and isinstance(node.value, ast.Call)
                    and isinstance(node.value.func, ast.Name)
                    and node.value.func.id == "max"
                    and node.value.args
                    and isinstance(node.value.args[0], ast.Constant)
                    and node.value.args[0].value == 0
                ):
                    continue
                target = node.targets[0].id
                if self._assigned_before(siblings, idx, target):
                    continue
                tree = copy.deepcopy(self.sketch)
                repl = copy.deepcopy(node)
                repl.value.args[0] = ast.copy_location(
                    ast.Name(id=target, ctx=ast.Load()),
                    repl.value.args[0],
                )
                self._replace_path(tree, for_path + rel_path, repl)
                new_siblings = self._get_list_at(tree, sibling_path, field)
                if new_siblings is None:
                    continue
                init = ast.Assign(
                    targets=[ast.Name(id=target, ctx=ast.Store())],
                    value=ast.Constant(value=0),
                )
                new_siblings.insert(idx, init)
                yield tree

    def _subscript_minus_one_candidates(self):
        for path, node in self._iter_nodes(self.sketch):
            if not (
                isinstance(node, ast.Subscript)
                and isinstance(node.ctx, ast.Load)
                and isinstance(node.slice, ast.BinOp)
                and isinstance(node.slice.op, ast.Sub)
                and isinstance(node.slice.right, ast.Constant)
                and node.slice.right.value == 1
            ):
                continue
            repl = copy.deepcopy(node)
            repl.slice = copy.deepcopy(node.slice.left)
            yield self._apply_edits([(path, repl)])

    def _inclusive_compare_candidates(self):
        edits = []
        for path, node in self._iter_nodes(self.sketch):
            if not isinstance(node, ast.Compare):
                continue
            repl = copy.deepcopy(node)
            changed = False
            for idx, op in enumerate(repl.ops):
                if isinstance(op, ast.Gt):
                    repl.ops[idx] = ast.GtE()
                    changed = True
                elif isinstance(op, ast.Lt):
                    repl.ops[idx] = ast.LtE()
                    changed = True
            if changed:
                edits.append((path, repl))
        if edits:
            yield self._apply_edits(edits)

    def _following_else_candidates(self):
        if self._size(self.sketch) > 240:
            return
        for path, node in self._iter_nodes(self.sketch):
            if not isinstance(node, ast.If) or node.orelse or not self._has_hole(node):
                continue
            if not self._body_has_terminal_output(node.body):
                continue
            if not path:
                continue
            field, idx = path[-1]
            if idx is None:
                continue
            sibling_path = path[:-1]
            siblings = self._get_list_at(self.sketch, sibling_path, field)
            if siblings is None or idx + 1 >= len(siblings):
                continue
            if len(siblings) - idx > 20:
                continue
            tree = copy.deepcopy(self.sketch)
            new_siblings = self._get_list_at(tree, sibling_path, field)
            if new_siblings is None or idx + 1 >= len(new_siblings):
                continue
            new_if = new_siblings[idx]
            if not isinstance(new_if, ast.If):
                continue
            new_if.orelse = new_siblings[idx + 1:]
            del new_siblings[idx + 1:]
            yield tree

    def _leading_zero_guard_candidates(self):
        digit_name = self._first_existing_name(("n", "N"))
        if digit_name is None:
            return
        edits = []
        for path, node in self._iter_nodes(self.sketch):
            if not isinstance(node, ast.If) or not self._is_leading_zero_test(node.test):
                continue
            guard = ast.Compare(
                left=ast.Name(id=digit_name, ctx=ast.Load()),
                ops=[ast.Gt()],
                comparators=[ast.Constant(value=1)],
            )
            repl = ast.BoolOp(op=ast.And(), values=[copy.deepcopy(node.test), guard])
            edits.append((path + (("test", None),), repl))
        for edit in edits:
            yield self._apply_edits([edit])

    def _sqrt_guard_candidates(self):
        if not {"a", "b", "c"} <= self.current_names:
            return
        edits = []
        guard = ast.Compare(
            left=ast.BinOp(
                left=ast.BinOp(
                    left=ast.Name(id="c", ctx=ast.Load()),
                    op=ast.Sub(),
                    right=ast.Name(id="a", ctx=ast.Load()),
                ),
                op=ast.Sub(),
                right=ast.Name(id="b", ctx=ast.Load()),
            ),
            ops=[ast.Gt()],
            comparators=[ast.Constant(value=0)],
        )
        for path, node in self._iter_nodes(self.sketch):
            if not isinstance(node, ast.If):
                continue
            if not self._looks_like_sqrt_inequality(node.test):
                continue
            repl = ast.BoolOp(op=ast.And(), values=[copy.deepcopy(guard), copy.deepcopy(node.test)])
            edits.append((path + (("test", None),), repl))
        for edit in edits:
            yield self._apply_edits([edit])

    def _integer_formula_candidates(self):
        for transformer_cls in (
            _FloorDivTransformer,
            _IntegerOutputTransformer,
            _InterestTransformer,
        ):
            transformer = transformer_cls()
            tree = transformer.visit(copy.deepcopy(self.sketch))
            if transformer.changed:
                yield tree

    def _compare_variants(self, node: ast.Compare):
        flips = {
            ast.Lt: [ast.LtE(), ast.Gt()],
            ast.LtE: [ast.Lt(), ast.GtE()],
            ast.Gt: [ast.GtE(), ast.Lt()],
            ast.GtE: [ast.Gt(), ast.LtE()],
            ast.Eq: [ast.NotEq()],
            ast.NotEq: [ast.Eq()],
        }
        for idx, op in enumerate(node.ops):
            for new_op in flips.get(type(op), []):
                repl = copy.deepcopy(node)
                repl.ops[idx] = new_op
                yield repl

    def _boolop_variants(self, node: ast.BoolOp):
        if not isinstance(node.op, ast.And):
            return
        names = []
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                if child.id not in _BUILTINS and child.id not in names:
                    names.append(child.id)
        for name in names[:4]:
            for value in (0, 1):
                guard = ast.Compare(
                    left=ast.Name(id=name, ctx=ast.Load()),
                    ops=[ast.NotEq()],
                    comparators=[ast.Constant(value=value)],
                )
                repl = copy.deepcopy(node)
                if any(
                    ast.dump(existing, include_attributes=False)
                    == ast.dump(guard, include_attributes=False)
                    for existing in repl.values
                ):
                    continue
                repl.values.append(guard)
                yield repl

    def _binop_variants(self, node: ast.BinOp):
        ops = [ast.Add(), ast.Sub(), ast.Mult(), ast.FloorDiv(), ast.Mod()]
        for op in ops:
            if type(op) is type(node.op):
                continue
            repl = copy.deepcopy(node)
            repl.op = op
            yield repl

    def _call_variants(self, node: ast.Call):
        if not isinstance(node.func, ast.Name):
            return
        alternates = {
            "int": ["round"],
            "round": ["int"],
            "max": ["min"],
            "min": ["max"],
        }
        for name in alternates.get(node.func.id, []):
            repl = copy.deepcopy(node)
            repl.func.id = name
            yield repl

    def _constant_variants(self, node: ast.Constant):
        vals = [0, 1, -1, node.value - 1, node.value + 1]
        seen = set()
        for value in vals:
            if value == node.value or value in seen:
                continue
            seen.add(value)
            yield ast.copy_location(ast.Constant(value=value), node)

    def _hole_nodes(self, klass):
        for path, node in self._iter_nodes(self.sketch):
            if isinstance(node, klass) and getattr(node, "_hole", False):
                yield path, node

    def _hole_containing_stmts(self):
        for path, node in self._iter_nodes(self.sketch):
            if isinstance(node, ast.stmt) and any(
                getattr(child, "_hole", False) for child in ast.walk(node)
            ):
                yield path, node

    def _iter_nodes(self, node: ast.AST, path=()):
        yield path, node
        for field, value in ast.iter_fields(node):
            if isinstance(value, ast.AST):
                yield from self._iter_nodes(value, path + ((field, None),))
            elif isinstance(value, list):
                for idx, item in enumerate(value):
                    if isinstance(item, ast.AST):
                        yield from self._iter_nodes(item, path + ((field, idx),))

    def _apply_edits(self, edits):
        tree = copy.deepcopy(self.sketch)
        for path, replacement in sorted(edits, key=lambda item: len(item[0]), reverse=True):
            self._replace_path(tree, path, copy.deepcopy(replacement))
        ast.fix_missing_locations(tree)
        return tree

    def _replace_path(self, tree: ast.AST, path, replacement: ast.AST):
        if not path:
            return replacement
        parent = tree
        for field, idx in path[:-1]:
            value = getattr(parent, field)
            parent = value[idx] if idx is not None else value
        field, idx = path[-1]
        old = getattr(parent, field)
        if idx is not None:
            old_node = old[idx]
            old[idx] = ast.copy_location(replacement, old_node)
        else:
            old_node = old
            setattr(parent, field, ast.copy_location(replacement, old_node))
        return tree

    def _get_list_at(self, tree: ast.AST, parent_path, field: str):
        parent = tree
        for step_field, step_idx in parent_path:
            value = getattr(parent, step_field)
            parent = value[step_idx] if step_idx is not None else value
        value = getattr(parent, field, None)
        return value if isinstance(value, list) else None

    def _paths_conflict(self, a, b):
        return a[: len(b)] == b or b[: len(a)] == a

    def _has_hole(self, node: ast.AST) -> bool:
        return any(getattr(child, "_hole", False) for child in ast.walk(node))

    def _assigned_before(self, siblings: list[ast.AST], idx: int, name: str) -> bool:
        for stmt in siblings[:idx]:
            for child in ast.walk(stmt):
                if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store) and child.id == name:
                    return True
        return False

    def _body_has_terminal_output(self, body: list[ast.stmt]) -> bool:
        for stmt in body:
            for child in ast.walk(stmt):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                    if child.func.id in {"print", "exit", "quit"}:
                        return True
                if isinstance(child, (ast.Return, ast.Raise)):
                    return True
        return False

    def _first_existing_name(self, names: tuple[str, ...]) -> str | None:
        for name in names:
            if name in self.current_names:
                return name
        return None

    def _is_leading_zero_test(self, node: ast.AST) -> bool:
        if isinstance(node, ast.BoolOp):
            return any(self._is_leading_zero_test(value) for value in node.values)
        if not isinstance(node, ast.Compare):
            return False
        operands = [node.left] + list(node.comparators)
        has_zero_subscript = any(
            isinstance(operand, ast.Subscript)
            and isinstance(operand.slice, ast.Constant)
            and operand.slice.value == 0
            for operand in operands
        )
        has_zero = any(
            isinstance(operand, ast.Constant) and operand.value == 0
            for operand in operands
        )
        return has_zero_subscript and has_zero and any(isinstance(op, ast.Eq) for op in node.ops)

    def _looks_like_sqrt_inequality(self, node: ast.AST) -> bool:
        has_pow_two = False
        has_four_ab = False
        for child in ast.walk(node):
            if (
                isinstance(child, ast.BinOp)
                and isinstance(child.op, ast.Pow)
                and isinstance(child.right, ast.Constant)
                and child.right.value == 2
            ):
                has_pow_two = True
            if (
                isinstance(child, ast.BinOp)
                and isinstance(child.op, ast.Mult)
                and any(
                    isinstance(grand, ast.Constant) and grand.value == 4
                    for grand in ast.walk(child)
                )
                and {"a", "b"} <= self._load_names(child)
            ):
                has_four_ab = True
        return has_pow_two and has_four_ab

    def _with_ctx(self, donor: ast.AST, target: ast.AST):
        target_ctx = getattr(target, "ctx", None)
        if target_ctx is None:
            return donor
        for node in ast.walk(donor):
            if hasattr(node, "ctx"):
                node.ctx = copy.deepcopy(target_ctx)
        return donor

    def _names_compatible(self, node: ast.AST) -> bool:
        return self._load_names(node) <= (self.current_names | _BUILTINS)

    def _load_names(self, node: ast.AST) -> set[str]:
        out = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                out.add(child.id)
        return out

    def _type_bag(self, node: ast.AST) -> dict[str, int]:
        bag: dict[str, int] = {}
        for child in ast.walk(node):
            key = type(child).__name__
            bag[key] = bag.get(key, 0) + 1
        return bag

    def _bag_cos(self, left: dict[str, int], right: dict[str, int]) -> float:
        common = set(left) & set(right)
        numerator = sum(left[key] * right[key] for key in common)
        left_norm = sum(value * value for value in left.values()) ** 0.5
        right_norm = sum(value * value for value in right.values()) ** 0.5
        return numerator / (left_norm * right_norm) if left_norm and right_norm else 0.0

    def _all_names(self, node: ast.AST) -> set[str]:
        return {child.id for child in ast.walk(node) if isinstance(child, ast.Name)}

    def _input_target_names(self, tree: ast.AST) -> list[str]:
        names = []
        for stmt in getattr(tree, "body", []):
            if not isinstance(stmt, ast.Assign):
                continue
            if not any(
                isinstance(child, ast.Call)
                and isinstance(child.func, ast.Name)
                and child.func.id == "input"
                for child in ast.walk(stmt.value)
            ):
                continue
            for target in stmt.targets:
                names.extend(self._target_names(target))
            if names:
                return names
        return names

    def _target_names(self, target: ast.AST) -> list[str]:
        if isinstance(target, ast.Name):
            return [target.id]
        if isinstance(target, (ast.Tuple, ast.List)):
            out = []
            for elt in target.elts:
                out.extend(self._target_names(elt))
            return out
        return []

    def _rename_input_vars(self, tree: ast.AST) -> ast.AST:
        donor_names = self._input_target_names(tree)
        if not donor_names or len(donor_names) != len(self.anchor_input_names):
            return tree
        var_map = {
            src: dst
            for src, dst in zip(donor_names, self.anchor_input_names)
            if src != dst
        }
        if not var_map:
            return tree

        class Renamer(ast.NodeTransformer):
            def visit_Name(self, node: ast.Name):
                if node.id in var_map:
                    return ast.copy_location(
                        ast.Name(id=var_map[node.id], ctx=node.ctx),
                        node,
                    )
                return node

        new_tree = Renamer().visit(copy.deepcopy(tree))
        ast.fix_missing_locations(new_tree)
        return new_tree

    def _collection_lineage(self) -> tuple[list[str], set[str]]:
        input_names: list[str] = []
        derived: set[str] = set()
        for stmt in getattr(self.sketch, "body", []):
            if not isinstance(stmt, ast.Assign):
                continue
            targets = []
            for target in stmt.targets:
                targets.extend(self._target_names(target))
            if not targets:
                continue
            loads = self._load_names(stmt.value)
            if self._contains_input_call(stmt.value):
                input_names.extend(name for name in targets if name not in input_names)
                continue
            if loads & (set(input_names) | derived) and self._is_collection_derivation(stmt.value):
                derived.update(targets)
        return input_names, derived

    def _contains_input_call(self, node: ast.AST) -> bool:
        return any(
            isinstance(child, ast.Call)
            and (
                (isinstance(child.func, ast.Name) and child.func.id == "input")
                or (isinstance(child.func, ast.Attribute) and child.func.attr == "readline")
            )
            for child in ast.walk(node)
        )

    def _is_collection_derivation(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {"list", "set", "sorted"}:
                return True
            if isinstance(node.func, ast.Attribute) and node.func.attr in {"split", "keys", "values"}:
                return True
        return isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp))

    def _is_counter_call(self, node: ast.Call) -> bool:
        return (
            isinstance(node.func, ast.Name)
            and node.func.id == "Counter"
        ) or (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "Counter"
        )

    def _is_store_context(self, node: ast.AST) -> bool:
        return hasattr(node, "ctx") and isinstance(node.ctx, (ast.Store, ast.Del))

    def _size(self, node: ast.AST) -> int:
        return sum(1 for _ in ast.walk(node))


class _DecimalScaleTransformer(ast.NodeTransformer):
    """One-shot candidate for decimal money-style multiplication bugs."""

    def __init__(self):
        self.changed = False

    def visit_Call(self, node: ast.Call):
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "int"
            and len(node.args) == 1
            and self._is_float_scale(node.args[0])
        ):
            self.changed = True
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="round", ctx=ast.Load()),
                    args=[self._scale_to_100(copy.deepcopy(node.args[0]))],
                    keywords=[],
                ),
                node,
            )
        return self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp):
        node = self.generic_visit(node)
        if (
            isinstance(node, ast.BinOp)
            and isinstance(node.op, ast.FloorDiv)
            and isinstance(node.right, ast.Constant)
            and node.right.value == 1000
        ):
            node.right = ast.copy_location(ast.Constant(value=100), node.right)
            self.changed = True
        if isinstance(node, ast.BinOp) and self._is_float_scale(node):
            self.changed = True
            return ast.copy_location(
                ast.Call(
                    func=ast.Name(id="round", ctx=ast.Load()),
                    args=[self._scale_to_100(copy.deepcopy(node))],
                    keywords=[],
                ),
                node,
            )
        return node

    def _is_float_scale(self, node: ast.AST) -> bool:
        if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Mult):
            return False
        return (
            self._is_float_call(node.left) and self._is_scale(node.right)
        ) or (
            self._is_scale(node.left) and self._is_float_call(node.right)
        )

    def _is_float_call(self, node: ast.AST) -> bool:
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "float"
            and len(node.args) == 1
        )

    def _is_scale(self, node: ast.AST) -> bool:
        return (
            isinstance(node, ast.Constant)
            and isinstance(node.value, (int, float))
            and node.value in {100, 100.0, 1000, 1000.0}
        )

    def _scale_to_100(self, node: ast.AST) -> ast.AST:
        if isinstance(node, ast.BinOp):
            if self._is_scale(node.left):
                node.left = ast.copy_location(ast.Constant(value=100), node.left)
            if self._is_scale(node.right):
                node.right = ast.copy_location(ast.Constant(value=100), node.right)
        return node


class _FloorDivTransformer(ast.NodeTransformer):
    def __init__(self):
        self.changed = False

    def visit_BinOp(self, node: ast.BinOp):
        node = self.generic_visit(node)
        if isinstance(node.op, ast.Div):
            node.op = ast.FloorDiv()
            self.changed = True
        return node


class _IntegerOutputTransformer(ast.NodeTransformer):
    def __init__(self):
        self.changed = False

    def visit_Subscript(self, node: ast.Subscript):
        node = self.generic_visit(node)
        if not (
            isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id == "str"
            and len(node.value.args) == 1
            and isinstance(node.slice, ast.Slice)
            and node.slice.lower is None
            and self._is_negative_two(node.slice.upper)
        ):
            return node
        self.changed = True
        return ast.copy_location(
            ast.BinOp(
                left=copy.deepcopy(node.value.args[0]),
                op=ast.FloorDiv(),
                right=ast.Constant(value=100),
            ),
            node,
        )

    def visit_Call(self, node: ast.Call):
        node = self.generic_visit(node)
        if not (
            (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "floor"
            )
            or (
                isinstance(node.func, ast.Name)
                and node.func.id == "floor"
            )
        ):
            return node
        if len(node.args) != 1:
            return node
        arg = node.args[0]
        if not isinstance(arg, ast.BinOp) or not isinstance(arg.op, (ast.Div, ast.FloorDiv)):
            return node
        self.changed = True
        return ast.copy_location(
            ast.BinOp(left=arg.left, op=ast.FloorDiv(), right=arg.right),
            node,
        )

    def _is_negative_two(self, node: ast.AST | None) -> bool:
        return (
            isinstance(node, ast.UnaryOp)
            and isinstance(node.op, ast.USub)
            and isinstance(node.operand, ast.Constant)
            and node.operand.value == 2
        )


class _InterestTransformer(ast.NodeTransformer):
    def __init__(self):
        self.changed = False

    def visit_Call(self, node: ast.Call):
        node = self.generic_visit(node)
        if not (
            isinstance(node.func, ast.Name)
            and node.func.id == "int"
            and len(node.args) == 1
        ):
            return node
        arg = node.args[0]
        if self._is_percent_div(arg):
            self.changed = True
            return ast.copy_location(
                ast.BinOp(left=arg.left, op=ast.FloorDiv(), right=arg.right),
                node,
            )
        scaled = self._compound_scaled(arg)
        if scaled is not None:
            self.changed = True
            return ast.copy_location(scaled, node)
        return node

    def visit_BinOp(self, node: ast.BinOp):
        node = self.generic_visit(node)
        scaled = self._compound_scaled(node)
        if scaled is not None:
            self.changed = True
            return ast.copy_location(scaled, node)
        return node

    def _is_percent_div(self, node: ast.AST) -> bool:
        return (
            isinstance(node, ast.BinOp)
            and isinstance(node.op, (ast.Div, ast.FloorDiv))
            and isinstance(node.right, ast.Constant)
            and node.right.value == 100
        )

    def _compound_scaled(self, node: ast.AST) -> ast.AST | None:
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.FloorDiv):
            if isinstance(node.right, ast.Constant) and node.right.value == 1:
                return self._compound_scaled(node.left)
            return None
        if not isinstance(node, ast.BinOp) or not isinstance(node.op, ast.Mult):
            return None
        name = None
        if isinstance(node.left, ast.Name) and self._is_101(node.right):
            name = node.left.id
        elif isinstance(node.right, ast.Name) and self._is_101(node.left):
            name = node.right.id
        if name is None:
            return None
        return ast.BinOp(
            left=ast.BinOp(
                left=ast.Name(id=name, ctx=ast.Load()),
                op=ast.Mult(),
                right=ast.Constant(value=101),
            ),
            op=ast.FloorDiv(),
            right=ast.Constant(value=100),
        )

    def _is_101(self, node: ast.AST) -> bool:
        return (
            isinstance(node, ast.Constant)
            and isinstance(node.value, (int, float))
            and abs(float(node.value) - 1.01) < 1e-9
        )
