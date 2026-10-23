"""Analyze the blinded expert ratings (expert_kit.py). Pre-registered analysis (results/expert_eval/PROTOCOL.md,
amended 2026-10-19: two external instructors answer only the pairwise P-Intent and P-Feedback questions):
  agreement before adjudication: linear weighted kappa for P-Intent and P-Feedback (HISTRA-oriented scores -1/0/+1)
  and raw agreement; primary test: exact two-sided sign test on non-tie P-Feedback judgments (HISTRA preferred vs not),
  on the adjudicated labels; secondary: the same test for P-Intent, and Spearman correlation between the preference
  scores and the per-pair metric differences (skeleton loss, TED). Per-patch criteria (AK, SEL, FB) of the original
  protocol are analyzed only if the CSVs contain them.
Usage: python expert_analyze.py KEY.csv RATER1.csv RATER2.csv [ADJUDICATED.csv] [EVAL_DIR]"""
import csv, json, math, os, sys
from collections import Counter

FIELDS = ["P_Intent", "P_Feedback"]                     # required answers per item
PATCH = ["AK", "SEL", "FB"]                              # per-patch criteria of the original protocol (optional)


def read(path):
    return {r["item"]: r for r in csv.DictReader(open(path, newline="", encoding="utf-8-sig"))}   # the kit writes a BOM


def kappa(xs, ys, weights=None, cats=None):
    """Cohen's kappa; weights='linear' for ordinal categories given in order by cats."""
    cats = cats or sorted(set(xs) | set(ys))
    k, n = len(cats), len(xs)
    idx = {c: i for i, c in enumerate(cats)}
    w = [[1.0 if i == j else (1 - abs(i - j) / (k - 1) if weights == "linear" else 0.0) for j in range(k)] for i in range(k)]
    po = sum(w[idx[x]][idx[y]] for x, y in zip(xs, ys)) / n
    px, py = Counter(xs), Counter(ys)
    pe = sum(w[idx[a]][idx[b]] * px[a] * py[b] for a in cats for b in cats) / n ** 2
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def binom_two_sided(k, n):
    """Exact two-sided binomial test with p = 0.5."""
    pmf = [math.comb(n, i) / 2 ** n for i in range(n + 1)]
    return min(1.0, sum(p for p in pmf if p <= pmf[k] * (1 + 1e-9)))


def spearman(xs, ys):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r, i = [0.0] * len(v), 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for t in range(i, j + 1):
                r[order[t]] = (i + j) / 2 + 1
            i = j + 1
        return r
    rx, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sd = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return cov / sd if sd else float("nan")


def oriented(row, key):
    """Ratings re-expressed for HISTRA (h) vs HISTRA with H = {} (n); pairwise answers as +1 (HISTRA), 0, -1."""
    h = "A" if key["A"] == "histra_min" else "B"
    nside = "B" if h == "A" else "A"
    pref = lambda v: 0 if v == "About the same" else (1 if v == h else -1)
    out = dict(P_Intent=pref(row["P_Intent"]), P_Feedback=pref(row["P_Feedback"]))
    for c in PATCH:
        out[f"{c}_h"], out[f"{c}_n"] = row.get(f"{c}_{h}", ""), row.get(f"{c}_{nside}", "")
    return out


def sign_test(scores, name):
    pos, neg = sum(s > 0 for s in scores), sum(s < 0 for s in scores)
    print(f"{name}: HISTRA {pos}, history-free {neg}, same {len(scores) - pos - neg} | "
          f"HISTRA share of non-ties {pos / max(pos + neg, 1):.2f} | exact sign test p = {binom_two_sided(pos, pos + neg):.4f}")


def mcnemar(rows, crit):
    b = sum(r[f"{crit}_h"] == "Yes" and r[f"{crit}_n"] != "Yes" for r in rows)
    c = sum(r[f"{crit}_h"] != "Yes" and r[f"{crit}_n"] == "Yes" for r in rows)
    yes_h, yes_n = sum(r[f"{crit}_h"] == "Yes" for r in rows), sum(r[f"{crit}_n"] == "Yes" for r in rows)
    print(f"{crit}: Yes for HISTRA {yes_h}/{len(rows)}, history-free {yes_n}/{len(rows)} | discordant {b} vs {c} | "
          f"exact McNemar p = {binom_two_sided(min(b, c), b + c) if b + c else 1.0:.4f}")


def main():
    key = {r["item"]: r for r in csv.DictReader(open(sys.argv[1], newline="")) if r["set"] == "rating"}
    r1, r2 = read(sys.argv[2]), read(sys.argv[3])
    adj = read(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].endswith(".csv") else None
    ev = sys.argv[5] if len(sys.argv) > 5 else "results/eval"
    items = [i for i in key if i in r1 and i in r2 and all(r1[i][f] and r2[i][f] for f in FIELDS)]
    print(f"items rated by both: {len(items)} / {len(key)}")
    for name, r in (("rater 1", r1), ("rater 2", r2)):
        print(f"{name}: P-Feedback changed after seeing the history in {sum(r[i].get('fb_changed') in ('1', 1) for i in items)} pairs")
    o1 = {i: oriented(r1[i], key[i]) for i in items}
    o2 = {i: oriented(r2[i], key[i]) for i in items}
    print("\n== agreement before adjudication")
    patch_crit = [c for c in PATCH if all(o[i][f"{c}_h"] for o in (o1, o2) for i in items)]
    for f in patch_crit:
        xs = [o1[i][f"{f}_{s}"] for i in items for s in "hn"]
        ys = [o2[i][f"{f}_{s}"] for i in items for s in "hn"]
        print(f"{f}: kappa {kappa(xs, ys):.2f} | raw {sum(a == b for a, b in zip(xs, ys)) / len(xs):.2f} | prevalence {dict(Counter(xs + ys))}")
    for f in ("P_Intent", "P_Feedback"):
        xs, ys = [o1[i][f] for i in items], [o2[i][f] for i in items]
        print(f"{f}: linear weighted kappa {kappa(xs, ys, 'linear', [-1, 0, 1]):.2f} | raw {sum(a == b for a, b in zip(xs, ys)) / len(xs):.2f}")
    final = {i: oriented(adj[i], key[i]) for i in items if i in adj} if adj else None
    for label, ratings in ([("adjudicated", final)] if final else []) + [("rater 1", o1), ("rater 2", o2)]:
        rows = list(ratings.values())
        print(f"\n== {label} ({len(rows)} pairs)")
        sign_test([r["P_Feedback"] for r in rows], "P-Feedback (primary)")
        sign_test([r["P_Intent"] for r in rows], "P-Intent")
        same = sum(r["P_Feedback"] == r["P_Intent"] for r in rows)
        print(f"P-Feedback equals P-Intent in {same}/{len(rows)} pairs ({100 * same / len(rows):.0f}%)")
        for crit in patch_crit:
            mcnemar(rows, crit)
    # correlation with automatic metrics (HISTRA minus history-free; negative = HISTRA better for loss and TED)
    ret = {n: {(r["pid"], r["user"]): r for r in map(json.loads, open(f"{ev}/{n}.ret.jsonl")) if r}
           for n in ("histra_min", "histra_nohist") if os.path.exists(f"{ev}/{n}.ret.jsonl")}
    em = json.load(open(f"{ev}/edit_metrics.json")) if os.path.exists(f"{ev}/edit_metrics.json") else {}
    src = final or o1
    pts = []
    for i in items:
        k = (key[i]["pid"], key[i]["user"])
        dl = dt = None
        if len(ret) == 2 and k in ret["histra_min"] and k in ret["histra_nohist"]:
            a, b = ret["histra_min"][k]["ret_patch"], ret["histra_nohist"][k]["ret_patch"]
            if a is not None and b is not None:
                dl = (1 - a) - (1 - b)
        e = em.get(f"{k[0]}/{k[1]}", {})
        if "histra_min" in e and "histra_nohist" in e:
            dt = e["histra_min"]["ted"] - e["histra_nohist"]["ted"]
        pts.append((src[i]["P_Intent"], src[i]["P_Feedback"], dl, dt))
    print("\n== Spearman correlation of preference with metric differences (HISTRA minus history-free)")
    for mi, mname in ((2, "skeleton loss"), (3, "TED to b")):
        for pi, pname in ((0, "P-Intent"), (1, "P-Feedback")):
            xy = [(p[pi], p[mi]) for p in pts if p[mi] is not None]
            if len(xy) > 2:
                print(f"{pname} vs d{mname}: rho {spearman([x for x, _ in xy], [y for _, y in xy]):.2f} (n = {len(xy)})")


if __name__ == "__main__":
    main()
