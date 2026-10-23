import ast
import copy
from .merge import MergeRepair


class Minimizer:
    """Shrink a passing patch back toward the student's own code.

    Every patch node that differs from its aligned node in the student's program is a revert
    candidate, and every statement the merge inserted is a deletion candidate. Candidates in the intent skeleton are tried before those in holes (keep what the
    student settled on first), larger subtrees before smaller ones; a revert is kept whenever the
    patch still passes the tests."""

    def __init__(self, anchor: ast.AST, holed: set, budget: int = 20):
        self.anchor = anchor      # pristine original program of the student (WA_n)
        self.holed = holed        # ids of anchor nodes inside holes
        self.budget = budget      # max number of validation calls

    @staticmethod
    def _slots(tree):
        """id(child) -> (parent, field, index or None), for putting a different subtree in its place."""
        out = {}
        for parent in ast.walk(tree):
            for field, value in ast.iter_fields(parent):
                if isinstance(value, ast.AST):
                    out[id(value)] = (parent, field, None)
                elif isinstance(value, list):
                    for i, v in enumerate(value):
                        if isinstance(v, ast.AST):
                            out[id(v)] = (parent, field, i)
        return out

    @staticmethod
    def _put(slot, node):
        parent, field, i = slot
        if i is None:
            setattr(parent, field, node)
        else:
            getattr(parent, field)[i] = node

    def _candidates(self, patch_tree):
        merger = MergeRepair()
        mapping = merger._match(self.anchor, patch_tree)
        slots = self._slots(patch_tree)
        a_slots = self._slots(self.anchor)
        # a match counts only where the parents match too, so code is never moved in from elsewhere
        pairs = {}
        for an in merger.walk(self.anchor):
            pn = mapping.get(id(an))
            if pn is None or id(pn) not in slots or id(an) not in a_slots:
                continue
            ap, pp = a_slots[id(an)][0], slots[id(pn)][0]
            if (ap is self.anchor and pp is patch_tree) or mapping.get(id(ap)) is pp:
                pairs[id(pn)] = (pn, an)
        pos = {id(n): i for i, n in enumerate(ast.walk(patch_tree))}   # deterministic tie-break (not id())
        cands = []
        for pn, an in pairs.values():
            if type(an) is not type(pn) or not isinstance(pn, (ast.stmt, ast.expr)):
                continue
            try:
                if ast.unparse(an) == ast.unparse(pn):
                    continue
            except Exception:
                continue
            size = sum(1 for _ in ast.walk(pn))
            cands.append((self._region(an), -size, pos[id(pn)], pn, an))
        # statements the merge inserted into the student's code (no counterpart): try dropping them
        for pn in ast.walk(patch_tree):
            if isinstance(pn, ast.stmt) and id(pn) not in pairs and id(pn) in slots:
                parent, field, _ = slots[id(pn)]
                if (id(parent) in pairs or parent is patch_tree) and len(getattr(parent, field)) > 1:
                    cands.append((2, -sum(1 for _ in ast.walk(pn)), pos[id(pn)], pn, None))
        cands.sort(key=lambda c: c[:3])           # skeleton first, then larger subtrees first
        return cands, slots

    def _region(self, an):
        """0: pure skeleton, 1: skeleton node containing holes, 2: inside a hole."""
        if id(an) in self.holed:
            return 2
        return 1 if any(id(x) in self.holed for x in ast.walk(an)) else 0

    def run(self, patch: str, passes) -> str:
        """`passes(src) -> bool` validates a candidate program against the tests."""
        cur, spent, progress = patch, 0, True
        while progress and spent < self.budget:
            progress = False
            try:
                tree = ast.parse(cur)
            except SyntaxError:
                break
            cands, slots = self._candidates(tree)
            for _, _, _, pn, an in cands:
                if spent >= self.budget:
                    break
                parent, field, i = slot = slots[id(pn)]
                if an is None:                    # inserted statement: drop it
                    getattr(parent, field).pop(i)
                    undo = lambda: getattr(parent, field).insert(i, pn)
                else:                             # put the student's code back
                    self._put(slot, copy.deepcopy(an))
                    undo = lambda: self._put(slot, pn)
                ast.fix_missing_locations(tree)
                try:
                    src = ast.unparse(tree)
                except Exception:
                    undo()
                    continue
                spent += 1
                if src != cur and passes(src):
                    cur, progress = src, True
                    break                         # re-align against the smaller patch
                undo()
        return cur
