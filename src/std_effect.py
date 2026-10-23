"""RQ3: share of the trajectories whose intent skeleton normalization changes (HISTRA-Norm).
Usage: [POOL=16] python paper/src/std_effect.py"""
import os
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src", "experiments"))   # <repo>/paper/src/
from common import POOL, cases  # noqa: E402
from skel import holed_ids, units  # noqa: E402


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
