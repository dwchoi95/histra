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

    # ---- Static helpers for multiprocessing-safe execution ----
    def _pipeline_run(self, traj: list[str], refs: list[str]) -> str | None:
        # 1. Standardize: 모든 WA를 동일 규칙으로 정규화 (문자열) + WAn(AST, provenance)
        std_traj = Standardizer.run(traj)
        anchor = std_traj[-1]

        # 2. Sketch: 변형된 부분만 __HOLE_k__ 처리 (canonical space)
        skt_std = Sketcher.run(std_traj)

        # 3. Reformat: Sketch 결과(holes/insert_entries)를 원래 표면으로 투영
        skt_org = Reformatter.run(anchor, skt_std)

        # 4. Search: refs에서 최소 수정 패치 재료(부분 서브트리) 검색/매핑
        searcher = Searcher(refs, anchor)
        node_map = searcher.run(skt_org)

        # 5. Repair: 노드 매핑을 이용해 AST 변환으로 스케치 코드 패치
        mod = Repair(node_map)
        patch = mod.run(skt_org)

        # 6. Validate: 모든 테스트케이스 통과 시 패치 반환, 아니면 None
        results = Validator.run(patch)
        if not results.passed(): patch = None
        return patch

    def run(self, trajectories:dict) -> dict:
        out = {}
        for user_id, traj in tqdm(trajectories.items(), total=len(trajectories), desc="Buggys", leave=False):
            refs = self._get_ac_pool(user_id)
            out[user_id] = self._pipeline_run(traj, refs)
        return dict(out)