import ast
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore")

from src.utils import DataLoader
from src.core import Standardizer
from src.core import Sketcher
from src.core import Reformatter
from src.core import Searcher
from src.core import Repair
from src.core import Validator


problems = DataLoader.run("data")
total = 0
checked = 0
passed = 0
for data in tqdm(problems, total=len(problems), desc="Problems"):
    pid, problem, timeout, trajectories, refs, tests = DataLoader.parse(data)

    Validator.init_globals(tests, timeout)

    # print(pid)
    for user_id, traj in tqdm(
                        trajectories.items(), 
                        total=len(trajectories), 
                        desc="Trajectories", 
                        leave=False):
        # traj의 모든 코드가 동일하면 스킵
        all_same = all(code == traj[0] for code in traj)
        if all_same: continue

        all_parsable = True
        for code in traj:
            try:
                ast.parse(code)
            except Exception as e:
                all_parsable = False
                break
        if not all_parsable: continue

        total += 1

        # Standardize 테스트
        std_traj = Standardizer.run(traj)
        anchor = std_traj[-1]
        anchor_std, anchor_org = anchor
        for std, org in std_traj:
            ast.unparse(std)
            ast.unparse(org)

        # Sketcher 테스트
        skt_std = Sketcher.run(std_traj)
        ast.unparse(skt_std)

        # Reformatter 테스트
        skt_org = Reformatter.run(anchor, skt_std)
        ast.unparse(skt_org)

        # Searcher 테스트
        searcher = Searcher(refs, anchor)
        node_map = searcher.run(skt_org)

        # Repair 테스트
        mod = Repair(node_map)
        patch = mod.run(skt_org)
        checked += 1

        # Validator 테스트
        if patch is not None:
            results = Validator.run(patch)
            if results.passed():
                passed += 1


print(f"total {total} trajectories")
print(f"checked {checked} trajectories")
print(f"passed {passed} trajectories")