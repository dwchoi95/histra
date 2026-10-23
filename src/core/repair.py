import ast
from .merge import MergeRepair
from .minimize import Minimizer

SHARED = (ast.expr_context, ast.boolop, ast.operator, ast.unaryop, ast.cmpop)


class Repair:
    """History-guided merge repair.

    Each retrieved program is merged into the student's program (keeping the student's aligned
    structure and identifiers, taking the reference's code where they diverge). The history guides
    the repair in three ways: (1) the merge is first confined to the holes, copying the intent
    skeleton verbatim, and only if no such patch passes may it also touch the skeleton; (2) within
    each phase, candidates that keep more of the skeleton are validated first; (3) the first passing
    patch is minimized back toward the student's code, skeleton first."""

    def __init__(self, pristine: ast.AST, holed: set, budget: int = 20):
        self.pristine = pristine
        self.minimizer = Minimizer(pristine, holed, budget)
        # pure-skeleton nodes: neither inside a hole nor containing one
        # ponytail: O(n^2) walk, fine for submission-sized trees
        # Operators/contexts are tree-wide singletons: freezing one would freeze it inside the holes too
        # (final review K1); inside frozen parents they are copied with the parent anyway.
        self.skeleton = frozenset(id(n) for n in ast.walk(pristine)
                                  if not isinstance(n, SHARED) and not any(id(x) in holed for x in ast.walk(n)))
        self.units = [n for n in ast.walk(pristine)
                      if isinstance(n, (ast.stmt, ast.expr)) and id(n) not in holed]

    def kept(self, src: str) -> int:
        """Skeleton statements/expressions that the candidate keeps unchanged."""
        merger = MergeRepair()
        mapping = merger._match(self.pristine, ast.parse(src))
        return sum(1 for n in self.units
                   if id(n) in mapping and merger.local_label(n) == merger.local_label(mapping[id(n)]))

    def run(self, code: str, ranked: list[str], validate, *, holes_first=True, kept_order=True, minimize=True):
        merger = MergeRepair()
        phases = ([self.skeleton] if holes_first else []) + [frozenset()]
        seen, cands = set(), []
        for phase, frozen in enumerate(phases):
            for ac_order in (False, True):             # minimal-edit alignment first, then AC order
                for ref in ranked:
                    src = merger._merge_patch(self.pristine, ref, ac_order, frozen)
                    if src is None or src in seen:
                        continue
                    seen.add(src)
                    cands.append((phase, -self.kept(src) if kept_order else 0, len(cands), src))
        self.phase = None
        for phase, *_, src in sorted(cands):           # hole-only first, then most skeleton kept
            if validate(src):
                self.phase = "hole" if holes_first and phase == 0 else "free"
                return self.minimizer.run(src, validate) if minimize else src
        return None
