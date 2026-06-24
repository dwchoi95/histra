"""Sampled comparison harness: deterministic merge-repair (core.merge.MergeRepair) vs
the existing LLM pipeline (core.histra.HISTRA), on N sampled trajectories of one problem.
Repair rate = fraction whose patch passes ALL held-out tests under our Py3.13 validator.
(The all-problems run is src/run_full.py.)

buggy = last WA (submissions[-2]); AC pool = other students' final ACs (the student's
own AC is never used to repair)."""
import json, os, sys, re, ast, time, random

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "src"))
sys.path.insert(0, HERE)

from verify.types import TestCase
from core.validator import Validator
from utils.features import Featurizer
from utils import metrics
from core.merge import MergeRepair

DATA = os.path.join(HERE, "data")


def normalize(code):
    """Neutralize the Python-version artifact: fractions.gcd was removed in 3.9 but
    these were valid at submission time. math.gcd == fractions.gcd on positive ints."""
    code = code.replace("from fractions import gcd", "from math import gcd")
    code = re.sub(r"\bfractions\.gcd\b", "math.gcd", code)
    return code


def load(pid):
    with open(os.path.join(DATA, pid, "trajectories.jsonl"), encoding="utf-8") as f:
        trajs = [json.loads(ln) for ln in f]
    with open(os.path.join(DATA, pid, "tests.jsonl"), encoding="utf-8") as f:
        tests = [TestCase(**json.loads(ln)) for ln in f]
    return trajs, tests


def valid_pool(pid, trajs, tests, *, timeout=3.0):
    """List of (user_id, normalized_code) for ACs that PASS the tests (Py3.13).
    Cached to disk so we pay the validation cost once."""
    cache = os.path.join(DATA, pid, "_ac_valid.json")
    if os.path.exists(cache):
        with open(cache) as f:
            return [tuple(x) for x in json.load(f)]
    pool = []
    for t in trajs:
        ac = t["submissions"][-1]
        if ac["verdict"] != "Accepted":
            continue
        code = normalize(ac["code"])
        if Validator.verify(code, tests, timeout=timeout).passed:
            pool.append((t["user_id"], code))
    with open(cache, "w") as f:
        json.dump(pool, f)
    return pool


def buggy_fails(trajs, tests, idxs, timeout=3.0):
    """Sanity: of the sampled buggies, how many actually fail (a repairable target)."""
    return sum(not Validator.verify(normalize(trajs[i]["submissions"][-2]["code"]),
                                    tests, timeout=timeout).passed for i in idxs)


def run_testpy(trajs, tests, idxs, pool, *, top_k=40, timeout=2.0, verbose=False):
    """Run the deterministic merge-repair over sampled trajectories. Returns metrics."""
    al = MergeRepair(min_height=1)
    users = [u for u, _ in pool]
    codes = [c for _, c in pool]
    feats = [Featurizer.features(c) for c in codes]
    idf = Featurizer.idf(feats)

    n = npass = nskip = 0
    modes = {"min": 0, "ac": 0}
    validated, secs, teds, ips = [], [], [], []
    for ti in idxs:
        t = trajs[ti]
        subs = t["submissions"]
        buggy, oracle = normalize(subs[-2]["code"]), normalize(subs[-1]["code"])  # last WA, AC
        user = t["user_id"]
        try:
            ast.parse(buggy)
        except SyntaxError:
            nskip += 1
            continue
        n += 1
        bf = Featurizer.features(buggy)
        cand = sorted((i for i in range(len(codes)) if users[i] != user),
                      key=lambda i: -Featurizer.wjaccard(bf, feats[i], idf))
        ranked = [codes[i] for i in cand[:top_k]]
        t0 = time.perf_counter()
        r = al.repair(buggy, ranked, tests, Validator, timeout=timeout, fast=False)
        secs.append(time.perf_counter() - t0)
        if r["patch"]:
            npass += 1
            validated.append(r["n_validated"]); modes[r.get("mode", "min")] += 1
            teds.append(metrics.ted(buggy, r["patch"]))             # edits from buggy to patch
            ips.append(metrics.intent_preservation(buggy, r["patch"], oracle))
        if verbose:
            print(f"  {user:12s} {'FIX(' + r.get('mode','?') + ')' if r['patch'] else 'fail':8s} "
                  f"validated={r['n_validated']}", flush=True)
    rr = npass / (n or 1)
    ipv = [x for x in ips if x is not None]
    pos = sum(x > 0 for x in ipv)
    print(f"[test.py] RR={rr:.0%} ({npass}/{n}) skip={nskip} "
          f"| TED(buggy->patch)={_mean(teds):.1f} IP mean={_mean(ips):+.2f} "
          f"med={_median(ipv):+.2f} pos={pos}/{len(ipv)} "
          f"| modes min/ac={modes['min']}/{modes['ac']} val={_mean(validated):.1f} sec={_mean(secs):.2f}")
    return {"RR": rr, "pass": npass, "n": n, "skip": nskip}


def run_dethistra(trajs, tests, idxs, *, top_k=20, timeout=2.0, verbose=False):
    """Deterministic histra: keep standardize+sketch+align+reformat, but fill the holes
    with the aligned AC code (no LLM), try top-k references + validate, then delta-debug
    the patch back toward the buggy's ORIGINAL surface (intent preservation)."""
    from core.searcher import Searcher
    from core.sketch import Sketcher
    from core.merge import MergeRepair
    codes, users = [], []
    for t in trajs:
        ac = t["submissions"][-1]
        if ac["verdict"] == "Accepted":
            codes.append(normalize(ac["code"])); users.append(t["user_id"])
    index = Searcher(codes, users=users)
    mr = MergeRepair()
    print(f"  [det-histra] AC pool {len(index)} (standardized), top_k={top_k}", flush=True)

    n = npass = nskip = 0
    teds, ips, secs, holes_won, tried = [], [], [], [], []
    for ti in idxs:
        t = trajs[ti]
        subs = t["submissions"]
        wa = [normalize(s["code"]) for s in subs[:-1]]
        buggy, oracle, user = wa[-1], normalize(subs[-1]["code"]), t["user_id"]
        prep = Sketcher.standardize_wa(wa)
        if prep is None:
            nskip += 1; continue
        std, common_wa = prep
        n += 1
        cand = index.nearest_k(std[-1], top_k, exclude_user=user, canonical=True)
        t0 = time.perf_counter()
        patch, nh, nt = None, None, 0
        for i in cand:
            try:
                sk = Sketcher.final(std, common_wa, buggy, ref_ac=index.std[i], deterministic=True)
            except Exception:
                continue
            if sk is None or not sk.filled_original or sk.n_holes == 0:
                continue
            src = sk.filled_original
            try:
                ast.parse(src)
            except SyntaxError:
                continue
            nt += 1
            if Validator.verify(src, tests, timeout=timeout).passed:
                patch = mr._minimize_ast(buggy, src, tests, Validator, timeout, budget=20)
                nh = sk.n_holes; break
        secs.append(time.perf_counter() - t0); tried.append(nt)
        if patch:
            npass += 1; holes_won.append(nh)
            teds.append(metrics.ted(buggy, patch))
            ips.append(metrics.intent_preservation(buggy, patch, oracle))
        if verbose:
            print(f"  {user:12s} {'FIX' if patch else 'fail':4s} holes={nh} tried={nt}", flush=True)
    rr = npass / (n or 1)
    ipv = [x for x in ips if x is not None]
    print(f"[det-histra] RR={rr:.0%} ({npass}/{n}) skip={nskip} | TED(buggy->patch)={_mean(teds):.1f} "
          f"IP mean={_mean(ips):+.2f} med={_median(ipv):+.2f} pos={sum(x>0 for x in ipv)}/{len(ipv)} "
          f"| avg holes={_mean(holes_won):.1f} tried={_mean(tried):.1f} sec={_mean(secs):.2f}")
    return {"RR": rr, "pass": npass, "n": n}


def _diff_holes(work, merged, canon2orig, Hole, AstUtils):
    """Diff the standardized buggy `work` against MergeRepair's `merged` tree; each
    MINIMAL changed subtree (that carries provenance) becomes a replace-hole whose
    ref_hint is the merged code renamed back to the student's original variables.
    Unchanged parts get no hole -> reformat keeps the student's ORIGINAL surface there."""
    import ast, copy
    holes = []

    def rename(node):
        for x in ast.walk(node):
            if isinstance(x, ast.Name) and x.id in canon2orig:
                x.id = canon2orig[x.id]
        return node

    def rec(a, b):
        if AstUtils.safe_unparse(a) == AstUtils.safe_unparse(b):
            return                                        # unchanged subtree
        ca, cb = list(ast.iter_child_nodes(a)), list(ast.iter_child_nodes(b))
        if (type(a) is type(b) and len(ca) == len(cb)
                and all(type(x) is type(y) for x, y in zip(ca, cb))):
            for x, y in zip(ca, cb):
                rec(x, y)
            return                                        # recurse to the minimal change
        o = getattr(a, "_origin", None)
        if isinstance(o, (ast.expr, ast.stmt)):
            holes.append(Hole(id=len(holes) + 1, std_stmt="", origin=o, kind="replace",
                              ref_hint=AstUtils.safe_unparse(rename(copy.deepcopy(b)))))

    rec(work, merged)
    return holes


def run_mergehistra(trajs, tests, idxs, *, top_k=20, timeout=2.0, verbose=False):
    """MergeRepair's merge (its way, unconstrained) but on STANDARDIZED inputs, with the
    result REFORMATTED onto the student's original surface (changed subtrees spliced via
    provenance, unchanged parts kept verbatim). Then delta-debug minimize."""
    import ast, copy
    from core.standardizer import Standardizer
    from core.searcher import Searcher
    from core.merge import MergeRepair
    from core.reformat import Reformatter
    from types import Hole
    from utils.ast_utils import AstUtils
    codes, users = [], []
    for t in trajs:
        ac = t["submissions"][-1]
        if ac["verdict"] == "Accepted":
            codes.append(normalize(ac["code"])); users.append(t["user_id"])
    index = Searcher(codes, users=users)
    mr = MergeRepair()
    print(f"  [merge-histra] AC pool {len(index)} (standardized), top_k={top_k}", flush=True)

    n = npass = nskip = 0
    teds, ips, secs = [], [], []
    for ti in idxs:
        t = trajs[ti]
        subs = t["submissions"]
        wa = [normalize(s["code"]) for s in subs[:-1]]
        buggy, oracle, user = wa[-1], normalize(subs[-1]["code"]), t["user_id"]
        pr = Standardizer.standardize_tree(buggy, rename=False)   # canonical structure, ORIGINAL names
        if pr is None:
            nskip += 1; continue
        work, orig = pr
        canon2orig = {}                                  # names unchanged (rename=False) -> identity
        for nd in ast.walk(work):
            o = getattr(nd, "_origin", None)
            if isinstance(nd, ast.Name) and isinstance(o, ast.Name):
                canon2orig.setdefault(nd.id, o.id)
        std_q = Standardizer.standardize(buggy) or ast.unparse(work)   # renamed form for retrieval
        cand = index.nearest_k(std_q, top_k, exclude_user=user, canonical=True)
        n += 1
        t0 = time.perf_counter()
        patch = None
        for i in cand:
            acpr = Standardizer.standardize_tree(index.raw[i], rename=False)   # AC: canon struct, own names
            if acpr is None:
                continue
            ac_work = acpr[0]
            m_ac = mr._match(work, ac_work)
            varmap = {}
            for x in mr.walk(work):
                v = m_ac.get(id(x))
                if isinstance(x, ast.Name) and isinstance(v, ast.Name):
                    varmap.setdefault(v.id, x.id)
            merged = mr._patch_paired(work, ac_work, varmap, False)   # MergeRepair's free merge
            ast.fix_missing_locations(merged)                          # _patch_paired drops locations
            holes = _diff_holes(work, merged, canon2orig, Hole, AstUtils)
            if not holes:
                continue
            src = Reformatter.fill(copy.deepcopy(orig), holes, [])
            if not src:
                continue
            try:
                ast.parse(src)
            except SyntaxError:
                continue
            if Validator.verify(src, tests, timeout=timeout).passed:
                patch = mr._minimize_ast(buggy, src, tests, Validator, timeout, budget=20)
                break
        secs.append(time.perf_counter() - t0)
        if patch:
            npass += 1
            teds.append(metrics.ted(buggy, patch))
            ips.append(metrics.intent_preservation(buggy, patch, oracle))
        if verbose:
            print(f"  {user:12s} {'FIX' if patch else 'fail'}", flush=True)
    rr = npass / (n or 1)
    ipv = [x for x in ips if x is not None]
    print(f"[merge-histra] RR={rr:.0%} ({npass}/{n}) skip={nskip} | TED(buggy->patch)={_mean(teds):.1f} "
          f"IP mean={_mean(ips):+.2f} med={_median(ipv):+.2f} pos={sum(x>0 for x in ipv)}/{len(ipv)} "
          f"| sec={_mean(secs):.2f}")
    return {"RR": rr, "pass": npass, "n": n}


def run_trajmerge(trajs, tests, idxs, *, top_k=20, timeout=2.0, verbose=False):
    """Compare MergeRepair on two buggy INPUTS (same AC pool, same retrieval, same merge):
      (raw)  buggy = last WA (original MergeRepair)
      (traj) buggy = the WA trajectory standardize->sketch->reformat'd: intent skeleton
             (churn-stable) kept on the student's surface, churned parts left as __HOLE__
             for MergeRepair's merge to fill."""
    from core.sketch import Sketcher
    from core.merge import MergeRepair
    codes, users = [], []
    for t in trajs:
        ac = t["submissions"][-1]
        if ac["verdict"] == "Accepted":
            codes.append(normalize(ac["code"])); users.append(t["user_id"])
    feats = [Featurizer.features(c) for c in codes]
    idf = Featurizer.idf(feats)
    al = MergeRepair()
    print(f"  [trajmerge] AC pool {len(codes)}, top_k={top_k}", flush=True)

    n = nskip = 0
    agg = {"raw": {"pass": 0, "ted": [], "ip": []}, "traj": {"pass": 0, "ted": [], "ip": []}}
    nholes = []
    for ti in idxs:
        t = trajs[ti]
        subs = t["submissions"]
        wa = [normalize(s["code"]) for s in subs[:-1]]
        buggy, oracle, user = wa[-1], normalize(subs[-1]["code"]), t["user_id"]
        try:
            ast.parse(buggy)
        except SyntaxError:
            nskip += 1; continue
        # trajectory-sketched buggy (churn skeleton frozen, churned parts -> holes)
        buggy_traj, nh = buggy, 0
        prep = Sketcher.standardize_wa(wa)
        if prep is not None:
            std, common_wa = prep
            sk = Sketcher.final(std, common_wa, buggy, ref_ac=None, reformat=True)
            if sk is not None and sk.sketched_original:
                try:
                    ast.parse(sk.sketched_original); buggy_traj = sk.sketched_original; nh = sk.n_holes
                except SyntaxError:
                    pass
        nholes.append(nh)
        n += 1
        bf = Featurizer.features(buggy)                   # SAME retrieval for both (by raw buggy)
        cand = sorted((i for i in range(len(codes)) if users[i] != user),
                      key=lambda i: -Featurizer.wjaccard(bf, feats[i], idf))
        ranked = [codes[i] for i in cand[:top_k]]
        for tag, b in (("raw", buggy), ("traj", buggy_traj)):
            r = al.repair(b, ranked, tests, Validator, timeout=timeout, fast=True, minimize=True)
            if r["patch"]:
                agg[tag]["pass"] += 1
                agg[tag]["ted"].append(metrics.ted(buggy, r["patch"]))
                agg[tag]["ip"].append(metrics.intent_preservation(buggy, r["patch"], oracle))
        if verbose:
            print(f"  {user:12s} holes={nh}", flush=True)
    for tag in ("raw", "traj"):
        a = agg[tag]; ipv = [x for x in a["ip"] if x is not None]
        print(f"[trajmerge:{tag:4s}] RR={a['pass']/(n or 1):.0%} ({a['pass']}/{n}) | "
              f"TED(buggy->patch)={_mean(a['ted']):.1f} IP mean={_mean(a['ip']):+.2f} "
              f"med={_median(ipv):+.2f} pos={sum(x>0 for x in ipv)}/{len(ipv)}", flush=True)
    print(f"  (avg holes in traj-buggy: {_mean(nholes):.1f}; skip={nskip})", flush=True)


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else 0.0


def _median(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return 0.0
    m = len(xs) // 2
    return xs[m] if len(xs) % 2 else (xs[m - 1] + xs[m]) / 2


def problem_meta(pid):
    text = timeout_s = None
    p = os.path.join(DATA, pid, "problem.html")
    if os.path.exists(p):
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", open(p, encoding="utf-8").read())).strip()[:1200]
    m = os.path.join(DATA, pid, "meta.json")
    timeout_s = json.load(open(m)).get("time_limit_ms", 2000) / 1000.0 if os.path.exists(m) else 2.0
    return text or "", timeout_s


def run_existing(trajs, tests, idxs, pool, problem_text, timeout_s):
    """Existing LLM pipeline (HISTRA) on the SAME sample + same valid pool + same
    normalization, for an apples-to-apples comparison."""
    from core.searcher import Searcher
    from core.histra import HISTRA
    from model.client import ModelClient
    from types import Config
    users = [u for u, _ in pool]
    codes = [c for _, c in pool]
    index = Searcher(codes, users=users)
    client = ModelClient(model="gemma4:e4b", mode="preflight", timeout=120.0)
    pipe = HISTRA(index, problem_text, tests, client, timeout=timeout_s)

    n = npass = nskip = 0
    teds, ips, secs = [], [], []
    for ti in idxs:
        t = trajs[ti]
        t2 = {"user_id": t["user_id"],
              "submissions": [{**s, "code": normalize(s["code"])} for s in t["submissions"]]}
        r = pipe.run_case(t2, config=Config())
        if r.skip:
            nskip += 1
            continue
        n += 1
        npass += r.passed
        secs.append(r.seconds)
        if r.passed:
            teds.append(r.ted); ips.append(r.intent)
    rr = npass / (n or 1)
    print(f"[existing] RR={rr:.0%} ({npass}/{n}) skip={nskip} "
          f"| TED(buggy->patch)={_mean(teds):.1f} IP={_mean(ips):+.2f} "
          f"| avg sec={_mean(secs):.2f}")
    return {"RR": rr, "pass": npass, "n": n}


if __name__ == "__main__":
    pid = sys.argv[1] if len(sys.argv) > 1 else "p03061"
    k = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 50
    top_k = int(sys.argv[sys.argv.index("--topk") + 1]) if "--topk" in sys.argv else 40
    verbose = "-v" in sys.argv

    trajs, tests = load(pid)
    print(f"problem {pid}: {len(trajs)} trajectories, {len(tests)} tests")

    random.seed(0)
    idxs = sorted(random.sample(range(len(trajs)), k))

    if "--trajmerge" in sys.argv:                      # MergeRepair on raw vs trajectory-sketched buggy
        run_trajmerge(trajs, tests, idxs, top_k=top_k, verbose=verbose)
    elif "--merge" in sys.argv:                        # MergeRepair + standardize + reformat
        run_mergehistra(trajs, tests, idxs, top_k=top_k, verbose=verbose)
    elif "--det" in sys.argv:                          # deterministic histra (builds own pool)
        run_dethistra(trajs, tests, idxs, top_k=top_k, verbose=verbose)
    else:
        pool = valid_pool(pid, trajs, tests)
        print(f"valid AC pool: {len(pool)}/{len(trajs)}")
        nfail = buggy_fails(trajs, tests, idxs)
        print(f"sample n={len(idxs)} | buggies that fail tests (repairable): {nfail}/{len(idxs)}\n")
        if "--existing" in sys.argv:
            text, tout = problem_meta(pid)
            run_existing(trajs, tests, idxs, pool, text, tout)
        else:
            run_testpy(trajs, tests, idxs, pool, top_k=top_k, verbose=verbose)
