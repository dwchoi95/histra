import ast
import copy
from tqdm import tqdm
from multiprocessing import Process, Manager

from .validator import Validator
from .standardizer import Standardizer
from .sketch import Sketcher
from .reformat import Reformatter
from .searcher import Searcher
from .repair import Repair
from .minimize import Minimizer

class HISTRA:
    def __init__(self, problem, timeout, tests, refs):
        self.problem = problem
        self.refs = refs
        Validator.init_globals(tests, timeout)
    
    def _get_ac_pool(self, user_id):
        # 간단/안전: 사본에서 해당 사용자만 제거하고 남은 코드 리스트 반환
        d = self.refs.copy()
        d.pop(user_id, None)
        return list(d.values())

    # ---- Static helpers for multiprocessing-safe execution ----
    @staticmethod
    def _sketch(std_traj):
        """Sketch the latest WA and project its holes onto the student's original code.
        Returns (sketched original source, (unsketched std anchor, original anchor),
                 (pristine copy of the original anchor, ids of its nodes inside holes))."""
        anchor_std, anchor_org = std_traj[-1]
        # Sketcher mutates anchor_std in place, so keep an unsketched copy for Reformat's
        # parallel walk; the memo keeps _origin pointing at the original anchor's nodes.
        unsketched = copy.deepcopy(anchor_std, {id(n): n for n in ast.walk(anchor_org)})

        # 2. Sketch: 변형된 부분만 __HOLE_k__ 처리 (canonical space)
        skt_std = Sketcher(std_traj).run(anchor_std)

        # Hole region on a pristine copy of the original anchor (Reformat edits anchor_org in place).
        # Contexts and operators are tree-wide shared singletons (one ast.Load for every read), so
        # they are left out; otherwise every node containing a read would count as holed.
        shared = (ast.expr_context, ast.boolop, ast.operator, ast.unaryop, ast.cmpop)
        holed = {id(n) for origin, _, _ in Reformatter.walk(unsketched, skt_std) for n in ast.walk(origin)
                 if not isinstance(n, shared)}
        memo = {}
        pristine = copy.deepcopy(anchor_org, memo)
        holed = {id(memo[i]) for i in holed if i in memo}

        # 3. Reformat: Sketch 결과(holes/insert_entries)를 원래 표면으로 투영
        skt_org = Reformatter.run((unsketched, anchor_org), skt_std)
        return skt_org, (unsketched, anchor_org), (pristine, holed)

    @staticmethod
    def _pipeline_run(traj: list[str], refs: list[str], validate=None, minimize=True) -> str | None:
        """`validate(src) -> bool` defaults to running the held-out tests via Validator."""
        validate = validate or (lambda src: Validator.run(src).passed())
        # 1. Standardize: 모든 WA를 동일 규칙으로 정규화 (문자열) + WAn(AST, provenance)
        std_traj = Standardizer.run(traj)
        if not std_traj:
            return None

        # 2-3. Sketch + Reformat: intent skeleton vs holes on the student's original code
        skt_org, _, (pristine, holed) = HISTRA._sketch(std_traj)
        if skt_org is None:
            return None

        # 4. Search: other students' accepted programs most similar to the student's program
        ranked = Searcher(refs).run(traj[-1])

        # 5-7. Repair: merge into holes first (skeleton kept), then anywhere; validate; minimize
        return Repair(pristine, holed).run(traj[-1], ranked, validate, minimize=minimize)

    @staticmethod
    def _run_case(user_id: str, traj: list[str], refs: list[str], out_dict):
        out_dict[user_id] = HISTRA._pipeline_run(traj, refs)

    def run(self, trajectories:dict) -> dict:
        manager = Manager()
        out = manager.dict()
        procs = []
        for user_id, traj in tqdm(trajectories.items(), total=len(trajectories), desc="Buggys", leave=False):
            refs = self._get_ac_pool(user_id)
            p = Process(target=HISTRA._run_case,
                        args=(user_id, traj, refs, out))
            p.start()
            procs.append(p)
        for p in procs:
            p.join()
        # Convert managed dict to a plain dict for return
        return dict(out)