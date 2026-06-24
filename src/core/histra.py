import ast
from tqdm import tqdm
from multiprocessing import Process, Manager

from .validator import Validator
from .standardizer import Standardizer
from .sketch import Sketcher
from .reformat import Reformatter
from .searcher import Searcher
from .repair import Repair

class HISTRA:
    def __init__(self, problem, timeout, tests, refs):
        self.problem = problem
        self.refs = refs
        self.tests = tests
        self.timeout = timeout
        Validator.init_globals(tests, timeout)
    
    def _get_ac_pool(self, user_id):
        # 간단/안전: 사본에서 해당 사용자만 제거하고 남은 코드 리스트 반환
        d = self.refs.copy()
        d.pop(user_id, None)
        return list(d.values())

    # ---- Static helpers for multiprocessing-safe execution ----
    @staticmethod
    def _pipeline_run(traj: list[str], refs: list[str]) -> str | None:
        # 1. Standardize: 모든 WA를 동일 규칙으로 정규화 (문자열) + WAn(AST, provenance)
        std_traj = Standardizer.run(traj)
        if not std_traj:
            return None
        anchor = std_traj[-1]
        anchor_std, _ = anchor

        # 2. Sketch: 변형된 부분만 __HOLE_k__ 처리 (canonical space)
        skt_std = Sketcher(std_traj).run(anchor_std)

        # 3. Reformat: Sketch 결과(holes/insert_entries)를 원래 표면으로 투영
        skt_org = Reformatter.run(anchor, skt_std)
        if skt_org is None:
            return None
        skt_org_ast = ast.parse(skt_org)

        # 4. Search: refs에서 최소 수정 패치 재료(부분 서브트리) 검색/매핑
        searcher = Searcher(refs, anchor)
        node_map = searcher.run(skt_org_ast)

        # 5. Repair: 노드 매핑을 이용해 AST 변환으로 스케치 코드 패치
        mod = Repair(node_map)
        patch = mod.run(skt_org_ast)
        if patch is None:
            return None

        # 6. Validate: 모든 테스트케이스 통과 시 패치 반환, 아니면 None
        results = Validator.run(patch)
        if not results.passed(): patch = None
        return patch

    @staticmethod
    def _run_case(user_id: str, traj: list[str], refs: list[str], out_dict):
        # Linux/fork 환경에서는 부모의 Validator 클래스 상태를 자식이 상속
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