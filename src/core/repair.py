import ast
from .merge import MergeRepair
from .minimize import Minimizer

SHARED = (ast.expr_context, ast.boolop, ast.operator, ast.unaryop, ast.cmpop)   # tree-wide singletons


class Repair:
    """Merge repair: hole-only merges before free ones, most skeleton kept first; minimizes the first passing patch."""

    def __init__(self, pristine: ast.AST, holed: set, budget: int = 20):
        self.pristine = pristine
        self.minimizer = Minimizer(pristine, holed, budget)
        # pure skeleton; shared operator/context singletons stay out, or freezing one would freeze it in the holes too
        self.skeleton = frozenset(id(n) for n in ast.walk(pristine)
                                  if not isinstance(n, SHARED) and not any(id(x) in holed for x in ast.walk(n)))
        self.units = [n for n in ast.walk(pristine)
                      if isinstance(n, (ast.stmt, ast.expr)) and id(n) not in holed]

    def kept(self, src: str) -> int:
        """Number of skeleton stmt/expr nodes that the candidate keeps unchanged."""
        merger = MergeRepair()
        mapping = merger._match(self.pristine, ast.parse(src))
        return sum(1 for n in self.units
                   if id(n) in mapping and merger.local_label(n) == merger.local_label(mapping[id(n)]))

    def run(self, code: str, ranked: list[str], validate, *, holes_first=True, kept_order=True, minimize=True):
        merger = MergeRepair()
        phases = ([self.skeleton] if holes_first else []) + [frozenset()]
        seen, cands = set(), []
        for phase, frozen in enumerate(phases):
            for ac_order in (False, True):             # first keep the student's unaligned statements, then drop them
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
