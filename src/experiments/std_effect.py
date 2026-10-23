"""RQ3: share of the trajectories whose intent skeleton normalization changes (HISTRA-Norm).
Usage: [POOL=16] python src/experiments/std_effect.py"""
from multiprocessing import Pool

from common import POOL, cases
from skel import holed_ids, units


def skeleton(was, standardize):
    org, holed = holed_ids(was, standardize=standardize)
    return [i for i, n in enumerate(units(org)) if id(n) not in holed]


def one(c):
    try:
        return skeleton(c["was"], True) != skeleton(c["was"], False)
    except Exception:
        return None


if __name__ == "__main__":
    with Pool(POOL) as p:
        diff = p.map(one, cases(), chunksize=4)
    print(f"skeleton changed by normalization: {sum(bool(d) for d in diff)}/{len(diff)} = "
          f"{100 * sum(bool(d) for d in diff) / len(diff):.1f}%")
