"""HISTRA (Algorithm 2): Sketch the latest wrong-answer submission with holes derived from the student's own history,
Search other students' accepted programs, and Repair by merging them into the holes first."""
import ast
import copy

from .reformat import Reformatter
from .repair import SHARED, Repair
from .searcher import Searcher
from .sketch import Sketcher
from .standardizer import Standardizer


class HISTRA:
    @staticmethod
    def sketch(std_traj):
        """(sketched original source, (canonical anchor, original anchor), (pristine original anchor, holed ids))."""
        anchor_std, anchor_org = std_traj[-1]
        # Sketcher mutates anchor_std in place: keep an unsketched copy whose _origin still points into anchor_org
        unsketched = copy.deepcopy(anchor_std, {id(n): n for n in ast.walk(anchor_org)})
        skt_std = Sketcher(std_traj).run(anchor_std)
        # contexts/operators are tree-wide shared singletons (one ast.Load for every read): never hole them
        holed = {id(n) for origin, _, _ in Reformatter.walk(unsketched, skt_std) for n in ast.walk(origin)
                 if not isinstance(n, SHARED)}
        memo = {}
        pristine = copy.deepcopy(anchor_org, memo)     # Reformatter edits anchor_org in place
        holed = {id(memo[i]) for i in holed if i in memo}
        skt_org = Reformatter.run((unsketched, anchor_org), skt_std)
        return skt_org, (unsketched, anchor_org), (pristine, holed)

    @staticmethod
    def repair(traj, refs, validate):
        """Patch for traj[-1] (the student's WA submissions in order) or None; refs = other students' ACs."""
        skt_org, _, (pristine, holed) = HISTRA.sketch(Standardizer.run(traj))
        if skt_org is None:
            return None
        return Repair(pristine, holed).run(traj[-1], Searcher(refs).run(traj[-1]), validate)
