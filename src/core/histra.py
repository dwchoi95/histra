import ast
import copy
from tqdm import tqdm

from .validator import Validator
from .standardizer import Standardizer
from .sketch import Sketcher
from .reformat import Reformatter
from .searcher import Searcher
from .repair import Repair

class HISTRA:
    def __init__(self, timeout, tests, refs):
        self.refs = refs
        Validator.init_globals(tests, timeout)
    
    def _get_ac_pool(self, user_id):
        # 간단/안전: 사본에서 해당 사용자만 제거하고 남은 코드 리스트 반환
        d = self.refs.copy()
        d.pop(user_id, None)
        return list(d.values())
    
    def _has_hole(self, node: ast.AST) -> bool:
        return any(getattr(n, "_hole", False) for n in ast.walk(node))

    # ---- Static helpers for multiprocessing-safe execution ----
    def _pipeline_run(self, traj: list[str], refs: list[str]) -> str | None:
        # 1. Standardize: 모든 WA를 동일 규칙으로 정규화 (문자열) + WAn(AST, provenance)
        std_traj = Standardizer.run(traj)
        anchor = std_traj[-1]

        # 2. Sketch: 변형된 부분만 __HOLE_k__ 처리 (canonical space)
        skt_std = Sketcher.run(std_traj)

        # 3. Reformat: Sketch 결과(holes/insert_entries)를 원래 표면으로 투영
        skt_org = Reformatter.run(anchor, skt_std)

        # 4-6. Search top-k refs one by one, repair with a single ref, then validate.
        searcher = Searcher(refs, anchor)
        for rank in range(len(searcher)):
            candidate = copy.deepcopy(skt_org)
            node_map, var_map = searcher.run(candidate, rank)
            if not node_map:
                continue

            mod = Repair(node_map, var_map)
            repaired = mod.run(candidate)
            patch = ast.unparse(repaired)
            results = Validator.run(patch)
            if results.passed():
                return patch

        return None

    def run(self, trajectories:dict) -> dict:
        out = {}
        for user_id, traj in tqdm(trajectories.items(), total=len(trajectories), desc="Buggys", leave=False):
            refs = self._get_ac_pool(user_id)
            out[user_id] = self._pipeline_run(traj, refs)
        return dict(out)