"""Aggregate evaluation over a stratified sample (per-problem) across all problems.

Parallelism is process-per-problem: each worker builds its own AC index and runs
its sampled cases; generates from the concurrent workers hit Ollama's
OLLAMA_NUM_PARALLEL slots, while index-build / pipeline / verification overlap
across processes. This avoids a long serial upfront index build.

Run: .venv/bin/python src/eval.py --per 100 [--seed 42] [--workers 6] [--out log.txt]
"""
import json, os, random, sys, time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

DATA = os.path.join(ROOT, "data")


def _arg(flag, default):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default


def work(args):
    """Build one problem's index and run its sampled trajectories (think=False)."""
    pid, idxs = args
    from core.searcher import Searcher
    from core.histra import HISTRA
    from model.client import ModelClient
    from run import load_problem, ac_pool, MODEL
    try:
        trajs, tests, problem, timeout_s = load_problem(pid)
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(pid=pid, lines=[], passed=0, empty=0, skipped=0,
                    injected=0, done=0, ted_sum=0, ted_n=0, intent_sum=0.0,
                    intent_n=0, secs_sum=0.0, secs_n=0)
    codes, users = ac_pool(trajs)
    pipe = HISTRA(Searcher(codes, users=users), problem, tests,
                  ModelClient(model=MODEL, mode="preflight", timeout=600.0),
                  think=False, timeout=timeout_s)
    out = dict(pid=pid, lines=[], passed=0, empty=0, skipped=0,
               injected=0, done=0, ted_sum=0, ted_n=0, intent_sum=0.0,
               intent_n=0, secs_sum=0.0, secs_n=0)
    prog_dir = os.path.join(ROOT, "results", "evalprog")
    os.makedirs(prog_dir, exist_ok=True)
    pf = open(os.path.join(prog_dir, f"{pid}.txt"), "w", encoding="utf-8")
    for idx in idxs:
        if idx >= len(trajs):
            continue
        r = pipe.run_case(trajs[idx])
        out["done"] += 1
        if r.skip:
            out["skipped"] += 1; tag = f"skip({r.skip})"
        else:
            out["passed"] += r.passed
            out["empty"] += r.empty; out["injected"] += r.injected
            out["secs_sum"] += r.seconds; out["secs_n"] += 1
            if r.passed and r.ted is not None:
                out["ted_sum"] += r.ted; out["ted_n"] += 1
            if r.passed and r.intent is not None:
                out["intent_sum"] += r.intent; out["intent_n"] += 1
            tag = (f"pass={r.passed}"
                   + ("" if r.passed else f" fail({r.fail_reason})"))
        line = f"{pid} {trajs[idx]['user_id']:12s} {tag}"
        out["lines"].append(line)
        pf.write(line + "\n"); pf.flush()          # live per-case progress
    pf.close()
    return out


def sample_per_problem(per, seed):
    grouped = {}
    for pid in sorted(d for d in os.listdir(DATA) if d.startswith("p") and os.path.isdir(os.path.join(DATA, d))):
        fp = os.path.join(DATA, pid, "trajectories.jsonl")
        if not os.path.exists(fp):
            continue
        n = sum(1 for _ in open(fp, encoding="utf-8"))
        idxs = list(range(n))
        random.Random(seed).shuffle(idxs)
        grouped[pid] = sorted(idxs[:per])
    return grouped


def main():
    per = int(_arg("--per", 100)); seed = int(_arg("--seed", 42))
    workers = int(_arg("--workers", 6)); out = _arg("--out", "")
    items = list(sample_per_problem(per, seed).items())
    total = sum(len(v) for _, v in items)
    print(f"{total} cases across {len(items)} problems, workers={workers}", flush=True)
    logf = open(out, "w", encoding="utf-8") if out else None
    agg = {k: 0 for k in ("passed", "empty", "skipped", "injected", "done",
                          "ted_sum", "ted_n", "intent_sum", "intent_n", "secs_sum", "secs_n")}
    t0 = time.time()
    with Pool(workers) as pool:
        for res in pool.imap_unordered(work, items):
            for k in agg:
                agg[k] += res[k]
            for ln in res["lines"]:
                if logf:
                    logf.write(ln + "\n")
            if logf:
                logf.flush()
            d = max(agg["done"], 1); rate = (time.time() - t0) / d
            print(f"[{agg['done']:4d}/{total}] done {res['pid']}  "
                  f"pass={agg['passed']}/{agg['done']} ({agg['passed']/d:.0%})  "
                  f"{rate:.1f}s/case eta={(total-agg['done'])*rate/3600:.1f}h", flush=True)
    if logf:
        logf.close()
    d = max(agg["done"], 1)
    TED = agg["ted_sum"] / agg["ted_n"] if agg["ted_n"] else 0.0
    IP = agg["intent_sum"] / agg["intent_n"] if agg["intent_n"] else 0.0
    ATT = agg["secs_sum"] / agg["secs_n"] if agg["secs_n"] else 0.0
    print(f"\nSUMMARY (n={agg['done']})  %RR={agg['passed']/d:.1%} ({agg['passed']}/{agg['done']})  "
          f"TED={TED:.1f}  IP={IP:+.2f}  ATT={ATT:.1f}s  "
          f"inject={agg['injected']}  skip={agg['skipped']}  empty={agg['empty']}  "
          f"({(time.time()-t0)/60:.0f}min)")


if __name__ == "__main__":
    main()
