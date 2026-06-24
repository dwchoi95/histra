"""Deterministic, LLM-free repair by reference-AC tree merge (Sarfgen-style).

Given the buggy program (last WA) and similarity-ranked correct ACs, align buggy<->AC,
merge field-by-field (keep the student's aligned structure + variable names, take the
AC's version where they diverge) with similarity-based statement-sequence alignment, run
the held-out tests, and return the first passing patch (optionally delta-debugged back
toward the buggy to minimise the edit). No model calls.

Empirically (p03061/p02700/p02696/p03042, 50-sample): 94-100% repair rate vs the LLM
pipeline's 36%. Intent preservation is bounded (we adopt other-students' structure); the
trajectory/intent-skeleton signal did NOT help IP and is intentionally not used here.
"""
import ast
import copy
import hashlib
from collections import Counter


class MergeRepair:
    SKIP_FIELDS = ("ctx",)            # Load/Store/Del contexts: noise

    def __init__(self, min_height=1):
        self.min_height = min_height

    # ---- labels / structure -------------------------------------------------
    def local_label(self, node):
        if isinstance(node, ast.Name):        return f"Name:{node.id}"
        if isinstance(node, ast.Constant):    return f"Const:{node.value!r}"
        if isinstance(node, ast.arg):         return f"arg:{node.arg}"
        if isinstance(node, ast.keyword):     return f"keyword:{node.arg}"
        if isinstance(node, ast.Attribute):   return f"Attribute:{node.attr}"
        if isinstance(node, ast.ImportFrom):  return f"ImportFrom:{node.module}"
        if isinstance(node, ast.alias):       return f"alias:{node.name}:{node.asname}"
        if isinstance(node, ast.FunctionDef): return f"FunctionDef:{node.name}"
        return type(node).__name__            # operators -> 'Add'/'Lt'/...; BinOp -> 'BinOp'

    def slot_children(self, node):
        out = []
        for fname, value in ast.iter_fields(node):
            if fname in self.SKIP_FIELDS:
                continue
            if isinstance(value, list):
                for i, v in enumerate(value):
                    if isinstance(v, ast.AST):
                        out.append((f"{fname}[{i}]", v))
            elif isinstance(value, ast.AST):
                out.append((fname, value))
        return out

    def children(self, node):
        return [c for _, c in self.slot_children(node)]

    def walk(self, node):
        yield node
        for c in self.children(node):
            yield from self.walk(c)

    def subtree_height(self, node, memo):
        if id(node) in memo:
            return memo[id(node)]
        kids = self.children(node)
        h = 0 if not kids else 1 + max(self.subtree_height(c, memo) for c in kids)
        memo[id(node)] = h
        return h

    def subtree_hash(self, node, memo):
        if id(node) in memo:
            return memo[id(node)]
        parts = [self.local_label(node)]
        for slot, c in self.slot_children(node):
            parts.append(slot + "=" + self.subtree_hash(c, memo))
        h = hashlib.md5("(".join(parts).encode()).hexdigest()[:12]
        memo[id(node)] = h
        return h

    def _set_slot(self, parent, slot, new_node):
        if "[" in slot:
            fname, idx = slot[:-1].split("["); getattr(parent, fname)[int(idx)] = new_node
        else:
            setattr(parent, slot, new_node)

    def _get_slot(self, parent, slot):
        if "[" in slot:
            fname, idx = slot[:-1].split("["); return getattr(parent, fname)[int(idx)]
        return getattr(parent, slot)

    # ---- node alignment (anchor -> ver) -------------------------------------
    def _match(self, anchor, ver):
        a_h, v_h, a_ht = {}, {}, {}
        ver_by_hash = {}
        for n in self.walk(ver):
            ver_by_hash.setdefault(self.subtree_hash(n, v_h), []).append(n)
        v_par = {id(c): n for n in self.walk(ver) for _, c in self.slot_children(n)}
        a_par = {id(c): n for n in self.walk(anchor) for _, c in self.slot_children(n)}
        a_slot = {id(c): slot for n in self.walk(anchor) for slot, c in self.slot_children(n)}
        mapping, used = {}, set()

        # (1) top-down: largest identical subtrees first (no lone-leaf matches)
        for a in sorted(self.walk(anchor), key=lambda n: self.subtree_height(n, a_ht), reverse=True):
            if id(a) in mapping or self.subtree_height(a, a_ht) < self.min_height:
                continue
            cands = [v for v in ver_by_hash.get(self.subtree_hash(a, a_h), []) if id(v) not in used]
            if cands:
                for an, vn in zip(self.walk(a), self.walk(cands[0])):
                    mapping[id(an)] = vn; used.add(id(vn))

        # (2) identifying-leaf match (func/name nodes by label)
        ver_leaf = {}
        for n in self.walk(ver):
            if id(n) not in used and not self.children(n):
                ver_leaf.setdefault(self.local_label(n), []).append(n)
        for a in self.walk(anchor):
            if id(a) in mapping or self.children(a):
                continue
            cands = [v for v in ver_leaf.get(self.local_label(a), []) if id(v) not in used]
            if cands:
                mapping[id(a)] = cands[0]; used.add(id(cands[0]))

        # (3) bottom-up: vote ancestors of matched children
        def idkids(n):
            return {self.local_label(c) for s, c in self.slot_children(n)
                    if s in ("func", "target") or s.startswith("targets")}
        changed = True
        while changed:
            changed = False
            for a in sorted(self.walk(anchor), key=lambda n: self.subtree_height(n, a_ht)):
                if id(a) in mapping:
                    continue
                votes = {}
                for _, c in self.slot_children(a):
                    p = v_par.get(id(mapping.get(id(c)))) if id(c) in mapping else None
                    d = 0
                    while p is not None:
                        votes.setdefault(id(p), [0, p, d]); votes[id(p)][0] += 1
                        p = v_par.get(id(p)); d += 1
                a_id = idkids(a)
                def key(item):
                    cnt, vp, d = item
                    return (not ((not a_id) or bool(a_id & idkids(vp))), -cnt, d)
                best = None
                for cnt, vp, d in sorted(votes.values(), key=key):
                    if type(vp).__name__ != type(a).__name__ or id(vp) in used:
                        continue
                    if a_id and idkids(vp) and not (a_id & idkids(vp)):
                        continue
                    best = vp; break
                if best is not None:
                    mapping[id(a)] = best; used.add(id(best)); changed = True

        # (4) slot match: parent matched and same slot -> same position
        for a in self.walk(anchor):
            if id(a) in mapping or id(a) not in a_par:
                continue
            vp = mapping.get(id(a_par[id(a)]))
            if vp is None:
                continue
            for slot, vc in self.slot_children(vp):
                if slot == a_slot[id(a)] and id(vc) not in used:
                    mapping[id(a)] = vc; used.add(id(vc)); break
        return mapping

    # ---- merge --------------------------------------------------------------
    def _rename(self, node, varmap):
        for x in ast.walk(node):
            if isinstance(x, ast.Name) and x.id in varmap:
                x.id = varmap[x.id]
        return node

    def _label_bag(self, node):
        return Counter(self.local_label(d) for d in ast.walk(node))

    def _sim(self, a, b):
        ca, cb = self._label_bag(a), self._label_bag(b)
        inter, union = sum((ca & cb).values()), sum((ca | cb).values())
        return inter / union if union else 0.0

    def _seq_align(self, blist, alist, thr=0.34):
        """Needleman-Wunsch alignment of two AST lists by structural similarity."""
        n, m = len(blist), len(alist)
        sc = [[self._sim(blist[i], alist[j]) if isinstance(blist[i], ast.AST)
               and isinstance(alist[j], ast.AST) else 0.0 for j in range(m)] for i in range(n)]
        NEG = -1e9
        dp = [[0.0] * (m + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                s = sc[i - 1][j - 1]
                dp[i][j] = max(dp[i - 1][j - 1] + (s if s >= thr else NEG),
                               dp[i - 1][j], dp[i][j - 1])
        ops, i, j = [], n, m
        while i > 0 and j > 0:
            s = sc[i - 1][j - 1]
            if dp[i][j] == dp[i - 1][j - 1] + (s if s >= thr else NEG):
                ops.append(("m", i - 1, j - 1)); i -= 1; j -= 1
            elif dp[i][j] == dp[i - 1][j]:
                ops.append(("d", i - 1, None)); i -= 1
            else:
                ops.append(("i", None, j - 1)); j -= 1
        while i > 0:
            ops.append(("d", i - 1, None)); i -= 1
        while j > 0:
            ops.append(("i", None, j - 1)); j -= 1
        ops.reverse()
        return ops

    def _merge_list(self, blist, alist, varmap, ac_order):
        out = []
        for op, bi, aj in self._seq_align(blist, alist):
            if op == "m":
                out.append(self._patch_paired(blist[bi], alist[aj], varmap, ac_order))
            elif op == "d":
                if not ac_order and isinstance(blist[bi], ast.AST):
                    out.append(copy.deepcopy(blist[bi]))      # keep the student's stmt
                elif not isinstance(blist[bi], ast.AST):
                    out.append(blist[bi])
            else:                                             # AC-only stmt -> insert
                out.append(self._rename(copy.deepcopy(alist[aj]), varmap)
                           if isinstance(alist[aj], ast.AST) else alist[aj])
        return out

    def _patch_paired(self, b, a, varmap, ac_order):
        if a is None:
            return copy.deepcopy(b)
        if type(a) is not type(b):
            return self._rename(copy.deepcopy(a), varmap)
        new = type(b)()
        for f in b._fields:
            bv, av = getattr(b, f, None), getattr(a, f, None)
            if isinstance(bv, list):
                if any(isinstance(x, ast.AST) for x in bv) and isinstance(av, list):
                    setattr(new, f, self._merge_list(bv, av, varmap, ac_order))
                else:
                    setattr(new, f, list(bv))
            elif isinstance(bv, ast.AST):
                setattr(new, f, self._patch_paired(bv, av if isinstance(av, ast.AST) else None,
                                                   varmap, ac_order))
            elif f in ("id", "arg"):
                setattr(new, f, bv)                           # keep the student's identifier
            elif bv == av or av is None:
                setattr(new, f, bv)
            else:
                setattr(new, f, av)                           # AC's correct scalar (op/attr/const)
        return new

    def _merge_patch(self, anchor, ac_src, ac_order):
        try:
            ac = ast.parse(ac_src)
        except (SyntaxError, ValueError):
            return None
        m_ac = self._match(anchor, ac)
        varmap = {}
        for x in self.walk(anchor):
            v = m_ac.get(id(x))
            if isinstance(x, ast.Name) and isinstance(v, ast.Name):
                varmap.setdefault(v.id, x.id)
        patched = self._patch_paired(anchor, ac, varmap, ac_order)
        ast.fix_missing_locations(patched)
        try:
            return ast.unparse(patched)
        except Exception:
            return None

    def _dist(self, src_a, src_b):
        try:
            ba, bb = self._label_bag(ast.parse(src_a)), self._label_bag(ast.parse(src_b))
        except (SyntaxError, ValueError):
            return float("inf")
        return sum((ba - bb).values()) + sum((bb - ba).values())

    def _minimize_ast(self, buggy, patch, tests, validator, timeout, budget=40):
        """Revert patch subtrees back to the buggy's aligned version (largest first)
        while tests still pass -> smaller edit -> better intent preservation."""
        bt = ast.parse(buggy)
        cur, spent, progress = patch, 0, True
        while progress and spent < budget:
            progress = False
            try:
                pt = ast.parse(cur)
            except (SyntaxError, ValueError):
                break
            m = self._match(pt, bt)
            psl = {}
            for p in ast.walk(pt):
                for s, c in self.slot_children(p):
                    psl[id(c)] = (p, s)
            cands = []
            for nd in ast.walk(pt):
                b = m.get(id(nd))
                if (b is None or id(nd) not in psl or type(b) is not type(nd)
                        or not isinstance(nd, (ast.stmt, ast.expr))):
                    continue
                try:
                    if ast.unparse(nd) != ast.unparse(b):
                        cands.append(nd)
                except Exception:
                    pass
            cands.sort(key=lambda nd: -sum(1 for _ in ast.walk(nd)))
            for nd in cands:
                if spent >= budget:
                    break
                p, s = psl[id(nd)]
                saved = self._get_slot(p, s)
                self._set_slot(p, s, copy.deepcopy(m[id(nd)]))
                ast.fix_missing_locations(pt)
                try:
                    src = ast.unparse(pt)
                except Exception:
                    self._set_slot(p, s, saved); continue
                spent += 1
                if src != cur and validator.verify(src, tests, timeout=timeout).passed:
                    cur, progress = src, True; break
                self._set_slot(p, s, saved)
        return cur

    def repair(self, buggy, ranked_acs, tests, validator, *, timeout=3.0,
               fast=True, minimize=True, min_budget=40):
        """Return the first/best passing merged patch (delta-debugged). `fast`=True
        returns the first passing AC's merge; `fast`=False scans all ranked ACs and keeps
        the smallest-edit passing one (better IP, slower). RR is identical either way."""
        try:
            anchor = ast.parse(buggy)
        except (SyntaxError, ValueError):
            return {"patch": None, "n_validated": 0}
        n = 0
        for ac_order in (False, True):                    # minimal-edit first, robust fallback
            seen, best = set(), None
            for ac_src in ranked_acs:
                src = self._merge_patch(anchor, ac_src, ac_order)
                if src is None or src in seen:
                    continue
                seen.add(src); n += 1
                if validator.verify(src, tests, timeout=timeout).passed:
                    if fast:
                        best = (0, src, ac_src); break
                    d = self._dist(buggy, src)
                    if best is None or d < best[0]:
                        best = (d, src, ac_src)
                    if ac_order:
                        break
            if best is not None:
                patch = self._minimize_ast(buggy, best[1], tests, validator, timeout,
                                           budget=min_budget) if minimize else best[1]
                return {"patch": patch, "ac": best[2], "mode": "ac" if ac_order else "min",
                        "n_validated": n}
        return {"patch": None, "n_validated": n}
