import json, os, random, sys

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # src/ (import root)
ROOT = os.path.dirname(SRC)                                          # repo root
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from core.sketch import Sketcher
from utils.ast_utils import AstUtils

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(x, **k):
        return x

DATA = os.path.join(ROOT, "data")


def holes_ratio(traj):
    """Fraction of the standardized buggy's AST nodes that are holed. None if
    unparsable. Returns (ratio, n_holes)."""
    wa = [s["code"] for s in traj["submissions"][:-1]]      # WA sequence (Sn = buggy)
    if len(wa) < 2:
        return None
    sk = Sketcher.build(wa)
    if sk is None:
        return None
    total = AstUtils.node_count(sk.std_sn)
    if not total:
        return None
    holed = sum(AstUtils.node_count(h.std_stmt) for h in sk.holes)
    return min(1.0, holed / total), len(sk.holes)


def main():
    n_prob = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    probs = sorted(d for d in os.listdir(DATA) if d.startswith("p"))
    random.Random(42).shuffle(probs)
    probs = probs[:n_prob]

    ratios, n_nohole, n_skip, n_traj = [], 0, 0, 0
    for pid in tqdm(probs, desc="problems", unit="prob"):
        path = os.path.join(DATA, pid, "trajectories.jsonl")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for ln in f:
                n_traj += 1
                r = holes_ratio(json.loads(ln))
                if r is None:
                    n_skip += 1
                    continue
                ratio, nh = r
                if nh == 0:
                    n_nohole += 1
                ratios.append(ratio)

    print(f"\nproblems={len(probs)}  trajectories={n_traj}  "
          f"analyzed={len(ratios)}  unparsable_skip={n_skip}  no_hole={n_nohole}")
    if not ratios:
        return
    ratios.sort(); m = len(ratios)
    ps = {p: ratios[min(m - 1, p * m // 100)] for p in (10, 25, 50, 75, 90, 95)}
    print("holes ratio (holed AST nodes / buggy AST nodes):")
    print("  mean={:.3f}  ".format(sum(ratios) / m)
          + "  ".join(f"p{p}={v:.2f}" for p, v in ps.items()))
    # buckets
    edges = [0.0, 1e-9, 0.1, 0.25, 0.5, 0.75, 1.0001]
    labels = ["=0 (no hole)", "(0,0.10]", "(0.10,0.25]", "(0.25,0.50]", "(0.50,0.75]", "(0.75,1.0]"]
    counts = [0] * (len(edges) - 1)
    for r in ratios:
        for i in range(len(edges) - 1):
            if edges[i] <= r < edges[i + 1] or (i == 0 and r == 0):
                counts[i] += 1
                break
    print("distribution:")
    peak = max(counts) or 1
    for lab, c in zip(labels, counts):
        bar = "#" * int(50 * c / peak)
        print(f"  {lab:14s} {c:6d} ({c/m:5.1%}) {bar}")
    high = sum(1 for r in ratios if r >= 0.5)
    print(f"\nbuggy mostly holed (ratio>=0.5): {high}/{m} ({high/m:.0%})  "
          "<- high => statement-level sketch too coarse")


if __name__ == "__main__":
    main()
