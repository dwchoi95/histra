"""Parallel verdict filter over data/<pid>/trajectories.jsonl: drop any trajectory containing a
submission whose Validator verdict disagrees with the recorded verdict (AC must pass all tests;
WA must fail at least one). Early-stop per submission; unique-code dedup; per-worker tests cache.

Usage: .venv/bin/python src/analysis/verdict_filter.py [--apply] [--jobs N] [pid ...]
(dry-run by default; --apply rewrites trajectories.jsonl)
"""
import os, sys, json, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from multiprocessing import Pool
from src.core.validator import Validator
from src.types import TestCase, Status
import warnings; warnings.filterwarnings("ignore")

DATA = os.path.join(ROOT, "data")
AC = "Accepted"
_TC = {}   # per-worker cache: pid -> (testcases, timeout)


def _tests(pid):
    if pid not in _TC:
        tcs = []
        with open(f"{DATA}/{pid}/tests.jsonl", encoding="utf-8") as f:
            for i, ln in enumerate(f):
                d = json.loads(ln); tcs.append(TestCase(id=i, input=d["input"], output=d["output"]))
        timeout = 2.0
        mp = f"{DATA}/{pid}/meta.json"
        if os.path.exists(mp):
            timeout = json.load(open(mp, encoding="utf-8")).get("time_limit_ms", 2000) / 1000.0
        _TC[pid] = (tcs, timeout)
    return _TC[pid]


def _passes(task):
    """task=(pid, code) -> True iff code passes ALL of pid's tests (early-stop)."""
    pid, code = task
    tcs, timeout = _tests(pid)
    Validator.timeout = timeout
    for tc in tcs:
        if Validator.run_case(code, tc).status != Status.PASSED:   # run_case takes CODE (python -c)
            return False
    return True


def main():
    apply = "--apply" in sys.argv
    jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else (os.cpu_count() or 4)
    pids = [a for a in sys.argv[1:] if not a.startswith("--") and not a.isdigit()]
    if not pids:
        pids = sorted(d for d in os.listdir(DATA)
                      if d.startswith("p") and os.path.isdir(f"{DATA}/{d}"))
    trajs_by_pid, tasks = {}, set()
    for pid in pids:
        fp = f"{DATA}/{pid}/trajectories.jsonl"
        if not os.path.exists(fp):
            continue
        ts = [json.loads(ln) for ln in open(fp, encoding="utf-8")]
        trajs_by_pid[pid] = ts
        for t in ts:
            for s in t["submissions"]:
                tasks.add((pid, s["code"]))
    tasks = list(tasks)
    print(f"{len(trajs_by_pid)} problems, {sum(len(v) for v in trajs_by_pid.values())} trajectories, "
          f"{len(tasks)} unique submissions to validate, jobs={jobs}", flush=True)
    t0 = time.time()
    with Pool(jobs) as pool:
        res = pool.map(_passes, tasks, chunksize=8)
    pmap = dict(zip(tasks, res))
    print(f"validated in {time.time()-t0:.0f}s", flush=True)

    tb = ta = 0; sub_after = 0; prob_after = 0; dropped_problems = []
    for pid, ts in trajs_by_pid.items():
        kept = [t for t in ts
                if all(pmap[(pid, s["code"])] == (s["verdict"] == AC) for s in t["submissions"])]
        tb += len(ts); ta += len(kept)
        sub_after += sum(len(t["submissions"]) for t in kept)
        if kept:
            prob_after += 1
        if apply and len(kept) != len(ts):
            with open(f"{DATA}/{pid}/trajectories.jsonl", "w", encoding="utf-8") as f:
                for t in kept:
                    f.write(json.dumps(t, ensure_ascii=False) + "\n")
        if len(kept) < 100:
            dropped_problems.append((pid, len(ts), len(kept)))
    print(f"\ntrajectories: {tb} -> {ta}  (removed {tb-ta} with a verdict mismatch)  "
          f"[{'APPLIED' if apply else 'DRY-RUN'}]")
    print(f"AFTER verdict filter, NO >=100 cap: problems={prob_after}  trajectories={ta}  submissions={sub_after}")
    print(f"problems that fall BELOW 100 after filtering: {len(dropped_problems)}")


if __name__ == "__main__":
    main()
