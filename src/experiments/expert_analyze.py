"""RQ4: agreement (linear weighted Cohen's kappa) and the share of pairs in which the instructors chose HISTRA over
HISTRA_empty, with an exact two-sided sign test. Usage: python src/experiments/expert_analyze.py"""
import csv
import math
import os
from collections import Counter

from common import ROOT

RATINGS = os.path.join(ROOT, "output", "expert", "ratings.csv")
SCORE = {"histra": 1, "same": 0, "nohist": -1}


def kappa(xs, ys, cats=(-1, 0, 1)):
    """Linear weighted Cohen's kappa over ordered categories."""
    k, n = len(cats), len(xs)
    idx = {c: i for i, c in enumerate(cats)}
    w = [[1 - abs(i - j) / (k - 1) for j in range(k)] for i in range(k)]
    po = sum(w[idx[x]][idx[y]] for x, y in zip(xs, ys)) / n
    px, py = Counter(xs), Counter(ys)
    pe = sum(w[idx[a]][idx[b]] * px[a] * py[b] for a in cats for b in cats) / n ** 2
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def sign_test(k, n):
    """Exact two-sided binomial test with p = 0.5."""
    pmf = [math.comb(n, i) / 2 ** n for i in range(n + 1)]
    return min(1.0, sum(p for p in pmf if p <= pmf[k] * (1 + 1e-9)))


if __name__ == "__main__":
    rows = list(csv.DictReader(open(RATINGS, newline="")))
    col = lambda c: [SCORE[r[c]] for r in rows]
    print(f"pairs: {len(rows)}")
    for q in ("feedback", "intent"):
        print(f"{q}: linear weighted kappa {kappa(col('rater1_' + q), col('rater2_' + q)):.2f} (before adjudication)")
    for who in ("", "rater1_", "rater2_"):
        print(f"\n== {who.rstrip('_') or 'adjudicated'}")
        for q in ("feedback", "intent"):
            s = col(who + q)
            pos, neg = s.count(1), s.count(-1)
            print(f"{q}: HISTRA {pos}, HISTRA_empty {neg}, same {len(s) - pos - neg} | HISTRA chosen in "
                  f"{100 * pos / len(s):.1f}% of the pairs | sign test p = {sign_test(pos, pos + neg):.2g}")
        same = sum(f == i for f, i in zip(col(who + "feedback"), col(who + "intent")))
        print(f"the patch chosen as feedback is the one judged to preserve the intent in {same}/{len(rows)} pairs")
