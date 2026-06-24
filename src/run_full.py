"""Full experiment: deterministic merge-repair (core.merge.MergeRepair) over ALL
problems x ALL trajectories x ALL tests. No LLM.

Per problem: AC pool = every accepted final submission (normalized); buggy = the last
WA (submissions[-2]); retrieve top-k ACs by weighted-Jaccard to the buggy (excluding the
student's own); merge-repair; validate against all held-out tests. Trajectories run in
parallel; AC pool is NOT pre-validated (the final test run guarantees correctness).

Run:  PYTHONPATH=src .venv/bin/python src/run_full.py [--topk 25] [--procs 8] [--limit N]
"""
import json, os, re, sys, ast, time, math
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from core.merge import MergeRepair
from verify.types import TestCase
from verify.runner import Validator
from utils.features import Featurizer
from utils import metrics

DATA = os.path.join(ROOT, "data")


def normalize(code):
    code = code.replace("from fractions import gcd", "from math import gcd")
    return re.sub(r"\bfractions\.gcd\b", "math.gcd", code)


def problems():
    out = []
    for pid in sorted(os.listdir(DATA)):
        d = os.path.join(DATA, pid)
        if os.path.isfile(os.path.join(d, "trajectories.jsonl")) and \
           os.path.isfile(os.path.join(d, "tests.jsonl")):
            out.append(pid)
    return out


def load(pid):
    with open(os.path.join(DATA, pid, "trajectories.jsonl"), encoding="utf-8") as f:
        trajs = [json.loads(ln) for ln in f]
    with open(os.path.join(DATA, pid, "tests.jsonl"), encoding="utf-8") as f:
        tests = [TestCase(**json.loads(ln)) for ln in f]
    tout = 3.0
    mp = os.path.join(DATA, pid, "meta.json")
    if os.path.exists(mp):
        tout = min(json.load(open(mp)).get("time_limit_ms", 2000) / 1000.0, 4.0)
    return trajs, tests, tout


# ---- worker (one trajectory) -------------------------------------------------
G = {}


def _init(codes, users, feats, idf, tests, targets, top_k, timeout, min_budget):
    G.update(codes=codes, users=users, feats=feats, idf=idf, tests=tests,
             targets=targets, top_k=top_k, timeout=timeout, min_budget=min_budget,
             rep=MergeRepair())


def _work(ti):
    buggy, oracle, user = G["targets"][ti]
    try:
        ast.parse(buggy)
    except SyntaxError:
        return ("skip", None, None)
    bf = Featurizer.features(buggy)
    cand = sorted((i for i in range(len(G["codes"])) if G["users"][i] != user),
                  key=lambda i: -Featurizer.wjaccard(bf, G["feats"][i], G["idf"]))
    ranked = [G["codes"][i] for i in cand[:G["top_k"]]]
    r = G["rep"].repair(buggy, ranked, G["tests"], Validator, timeout=G["timeout"],
                        fast=True, minimize=True, min_budget=G["min_budget"])
    if r["patch"]:
        return ("pass", metrics.ted(buggy, r["patch"]),
                metrics.intent_preservation(buggy, r["patch"], oracle))
    return ("fail", None, None)


def _stat(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return 0.0, 0.0
    mean = sum(xs) / len(xs)
    mid = len(xs) // 2
    med = xs[mid] if len(xs) % 2 else (xs[mid - 1] + xs[mid]) / 2
    return mean, med


def run_problem(pid, top_k, procs, out, min_budget):
    trajs, tests, tout = load(pid)
    codes, users = [], []
    for t in trajs:
        ac = t["submissions"][-1]
        if ac["verdict"] == "Accepted":
            codes.append(normalize(ac["code"])); users.append(t["user_id"])
    targets = [(normalize(t["submissions"][-2]["code"]),
                normalize(t["submissions"][-1]["code"]), t["user_id"])
               for t in trajs if len(t["submissions"]) >= 2]
    if not codes or not targets:
        return None
    feats = [Featurizer.features(c) for c in codes]
    idf = Featurizer.idf(feats)
    args = (codes, users, feats, idf, tests, targets, top_k, tout, min_budget)

    t0 = time.perf_counter()
    with Pool(procs, initializer=_init, initargs=args) as pool:
        res = pool.map(_work, range(len(targets)), chunksize=4)
    secs = time.perf_counter() - t0

    npass = sum(r[0] == "pass" for r in res)
    nskip = sum(r[0] == "skip" for r in res)
    n = len(res) - nskip
    teds = [r[1] for r in res if r[0] == "pass"]
    ips = [r[2] for r in res if r[0] == "pass"]
    rr = npass / (n or 1)
    ted_m, _ = _stat(teds)
    ip_m, ip_med = _stat(ips)
    pos = sum(1 for x in ips if x is not None and x > 0)
    line = (f"{pid:8s} RR={rr:5.1%} ({npass}/{n}) skip={nskip} | TED={ted_m:6.1f} "
            f"IP mean={ip_m:+.2f} med={ip_med:+.2f} pos={pos}/{len(ips)} "
            f"| tests={len(tests)} pool={len(codes)} {secs:5.0f}s")
    print(line, flush=True)
    out.write(line + "\n"); out.flush()
    return {"pid": pid, "n": n, "pass": npass, "teds": teds, "ips": ips}


def main():
    top_k = int(sys.argv[sys.argv.index("--topk") + 1]) if "--topk" in sys.argv else 20
    procs = int(sys.argv[sys.argv.index("--procs") + 1]) if "--procs" in sys.argv \
        else max(1, (os.cpu_count() or 4) - 2)
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    min_budget = int(sys.argv[sys.argv.index("--minbudget") + 1]) if "--minbudget" in sys.argv else 10

    pids = problems()
    if limit:
        pids = pids[:limit]
    print(f"FULL EXPERIMENT: {len(pids)} problems, procs={procs}, topk={top_k}, "
          f"minbudget={min_budget}\n", flush=True)

    rows = []
    with open(os.path.join(ROOT, "results_full.txt"), "w") as out:
        out.write(f"# deterministic merge-repair: {len(pids)} problems, topk={top_k}\n")
        for pid in pids:
            try:
                r = run_problem(pid, top_k, procs, out, min_budget)
            except Exception as e:
                print(f"{pid:8s} ERROR {type(e).__name__}: {e}", flush=True)
                continue
            if r:
                rows.append(r)
        N = sum(r["n"] for r in rows)
        P = sum(r["pass"] for r in rows)
        all_ips = [x for r in rows for x in r["ips"] if x is not None]
        all_teds = [x for r in rows for x in r["teds"] if x is not None]
        ip_m, ip_med = _stat(all_ips)
        ted_m, _ = _stat(all_teds)
        macro = sum(r["pass"] / (r["n"] or 1) for r in rows) / (len(rows) or 1)
        summary = (f"\n=== OVERALL: micro-RR={P/(N or 1):.1%} ({P}/{N}) "
                   f"macro-RR={macro:.1%} over {len(rows)} problems "
                   f"| TED={ted_m:.1f} IP mean={ip_m:+.2f} med={ip_med:+.2f} "
                   f"pos={sum(1 for x in all_ips if x>0)}/{len(all_ips)} ===")
        print(summary, flush=True)
        out.write(summary + "\n")


if __name__ == "__main__":
    main()
