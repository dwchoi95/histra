"""Run MENTORED (Choi & Lee, ICSE-CSEE&T 2025; baselines/mentored, approach 'mentored' with correct programs) on the
baselines.py sample (PER/ONLY select the TARGET trajectories) so that no target's own AC ever reaches its repair.
MODE=all (default; design A): one MENTORED run per target X at the problem level, as in its paper: wrong programs =
  was[-1] of ALL trajectories of X's problem (X and every peer, one population, regardless of PER/ONLY), correct
  programs = the final ACs of every student of the problem except X; only X's patch is kept.
MODE=fold: per problem, the targets (users sorted, shuffled with seed 0) are dealt into FOLDS (default 5) folds; one run
  per fold repairs the fold's was[-1] together, correct programs = the final ACs of the students not in the fold.
MODE=single: one run per target with wrong programs = {X}, correct programs = refs (MENTORED's population is then 1).
MENTORED's defaults (30 generations, 1 execution), the benchmark's per-test timeout, MSEED (default 0),
PYTHONHASHSEED=0, one BLAS/OpenMP thread; each run is a fresh process, supervised here:
  RUN_CAP (default 3600 s) wall clock and MEM_CAP_GB (default 16) resident memory per run (watchdog on /proc RSS every
  2 s; RLIMIT_AS = 2 x MEM_CAP_GB as a backstop): a run over a cap is killed and its targets get the solutions MENTORED
  had found until then (run_case.py logs each solution at once), by MENTORED's own final-patch rule.
A target's patch is MENTORED's reported one (its smallest-RPS solution), validated here with V.verify.
Usage: [MODE=all|fold|single] [PER=0] [POOL=n runs in parallel] [ONLY=pid,..] [FOLDS=5] [RUN_CAP=s] [MEM_CAP_GB=g]
       [MSEED=k] [JOBS=dir: keep the run inputs/outputs] python run_mentored.py OUT.jsonl       (PER=0: every target)
Rows: pid, user, was, oracle, patch, sec (run wall time / targets in the run), status (ok | reject = MENTORED's patch
failed V.verify | none = the run ended without a patch for this target | timecap | memcap | crash = the run was killed
at a cap or died, without a patch), server_status (= status; validation runs on the server), raw (MENTORED's reported
patch before V.verify), solutions (# passing patches MENTORED found for this target), end (done | timecap | memcap |
crash: how the run ended), rc (its exit code; negative = signal), run_sec, cpu_sec, max_rss_mb (the run's, from
wait4), capped (end == timecap), fold. A run's full stderr goes to OUT.err/<run>.txt (kept only if non-empty).
Resumable: targets already in OUT.jsonl are skipped and new rows are appended. Runs go light problems first (least
test stdin), so the MB-input problems (p03438, p02975, p02686, p02623) run last."""
import json, os, random, signal, subprocess, sys, tempfile, time
from multiprocessing.pool import ThreadPool
sys.path.insert(0, os.path.dirname(__file__))
from baselines import cases, normalize, V, POOL, DATA

MT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "baselines", "mentored"))
MODE, FOLDS, GENS, SEED = os.environ.get("MODE", "all"), int(os.environ.get("FOLDS", 5)), 30, int(os.environ.get("MSEED", 0))
CAP, MEM = float(os.environ.get("RUN_CAP", 3600)), float(os.environ.get("MEM_CAP_GB", 16))
JOBS = os.environ.get("JOBS")
for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(k, "1")                    # MENTORED imports numpy/scipy/sklearn: no BLAS thread pools


def problem(pid):
    """{user: (was[-1], final AC)} for every trajectory of the problem, normalized as in cases()."""
    with open(f"{DATA}/{pid}/trajectories.jsonl", encoding="utf-8") as f:
        ts = [json.loads(l) for l in f]
    return {t["user_id"]: ([normalize(s["code"]) for s in t["submissions"] if s["verdict"] != "Accepted"][-1],
                           normalize(t["submissions"][-1]["code"])) for t in ts}


def runs(cs):
    """[(pid, fold id or None, targets)]."""
    out = []
    for pid in sorted({c["pid"] for c in cs}):
        pc = sorted((c for c in cs if c["pid"] == pid), key=lambda c: c["user"])
        if MODE == "fold":
            random.Random(0).shuffle(pc)
            out += [(pid, i, pc[i::FOLDS]) for i in range(FOLDS) if pc[i::FOLDS]]
        else:
            out += [(pid, None, [c]) for c in pc]
    return out


def rss_gb(pid):
    try:
        return int(open(f"/proc/{pid}/statm").read().split()[1]) * os.sysconf("SC_PAGE_SIZE") / 2 ** 30
    except (OSError, ValueError, IndexError):        # no /proc (macOS) or already gone
        return 0.0


def supervise(cmd, env, err):
    """Run cmd; kill it at RUN_CAP wall seconds or MEM_CAP_GB resident GB. -> (end, rc, wall s, cpu s, peak RSS MB)."""
    t0, end = time.time(), None
    with open(err, "w") as ef:
        p = subprocess.Popen(cmd, cwd=MT, stdout=subprocess.DEVNULL, stderr=ef, env=env)
    while True:
        pid, st, ru = os.wait4(p.pid, os.WNOHANG)
        if pid:
            break
        if end is None and (time.time() - t0 > CAP or rss_gb(p.pid) > MEM):
            end = "timecap" if time.time() - t0 > CAP else "memcap"
            os.kill(p.pid, signal.SIGKILL)
        time.sleep(0.5 if time.time() - t0 < 10 else 2)
    p.returncode = rc = os.waitstatus_to_exitcode(st)   # reaped here; tell Popen
    rss = ru.ru_maxrss / (2 ** 20 if sys.platform == "darwin" else 2 ** 10)
    return end or ("done" if rc == 0 else "crash"), rc, time.time() - t0, ru.ru_utime + ru.ru_stime, rss


def run(job):
    pid, k, targets = job
    ts, prob = {c["user"] for c in targets}, problem(pid)
    wrongs = {u: w for u, (w, _) in prob.items()} if MODE == "all" else {}
    wrongs.update({c["user"]: c["was"][-1] for c in targets})
    corrects = {u: a for u, (_, a) in prob.items() if u not in ts}
    d = JOBS or tempfile.mkdtemp()
    os.makedirs(d, exist_ok=True)
    name = f"{pid}_{k if k is not None else targets[0]['user']}"
    inp, res = f"{d}/{name}.json", f"{d}/{name}.out.json"
    for f in (res, res + ".sols.jsonl"):
        if os.path.exists(f):
            os.remove(f)
    with open(inp, "w") as f:
        json.dump(dict(wrongs=wrongs, corrects=corrects, targets=sorted(ts), testcases=targets[0]["tests"],
                       timeout=targets[0]["timeout"], generations=GENS, seed=SEED), f)
    py = f"{MT}/.venv/bin/python"
    env = dict(os.environ, PYTHONHASHSEED="0", TQDM_DISABLE="1", MEM_AS_GB=str(2 * MEM))
    os.makedirs(ERRS, exist_ok=True)
    err = f"{ERRS}/{name}.txt"
    end, rc, sec, cpu, rss = supervise([py, "run_case.py", inp, res], env, err)
    if not os.path.exists(res):                      # killed or died: the final-patch rule over the solutions so far
        subprocess.run([py, "run_case.py", "--finalize", inp, res], cwd=MT, env=env, capture_output=True, timeout=900)
    if os.path.getsize(err) == 0:
        os.remove(err)
    try:
        out = json.load(open(res))
    except (OSError, ValueError):
        out, end = {}, end if end != "done" else "crash"
    rows = []
    for c in targets:
        r = out.get(c["user"], {})
        raw = r.get("patch")
        st = ("ok" if V.verify(raw, c["tests"], c["timeout"]).passed else "reject") if raw is not None else \
             "none" if end == "done" else end
        rows.append(dict(pid=pid, user=c["user"], was=c["was"], oracle=c["oracle"], patch=raw if st == "ok" else None,
                         sec=sec / len(targets), status=st, server_status=st, raw=raw, solutions=r.get("solutions"),
                         end=end, rc=rc, run_sec=sec, cpu_sec=cpu, max_rss_mb=rss, capped=end == "timecap", fold=k))
    if not JOBS:
        for f in (inp, res, res + ".sols.jsonl"):
            if os.path.exists(f):
                os.remove(f)
        os.rmdir(d)
    return rows


if __name__ == "__main__":
    out, cs = sys.argv[1], cases()
    ERRS = out + ".err"
    done = {(r["pid"], r["user"]) for r in map(json.loads, open(out))} if os.path.exists(out) else set()
    jobs = [j for j in runs(cs) if any((j[0], c["user"]) not in done for c in j[2])]
    jobs.sort(key=lambda j: sum(len(t["input"]) for t in j[2][0]["tests"]))      # stable: light problems first
    print(f"MODE={MODE} POOL={POOL} RUN_CAP={CAP:.0f}s MEM_CAP_GB={MEM:g} targets {len(cs)}, already done {len(done)},"
          f" runs to do {len(jobs)}", flush=True)
    res = []
    with ThreadPool(POOL) as pool, open(out, "a") as f:
        for rows in pool.imap_unordered(run, jobs):
            res += rows
            f.writelines(json.dumps(r) + "\n" for r in rows)
            f.flush()
            r = rows[0]
            print(time.strftime("%m-%d %H:%M"), r["pid"], r["user"] if MODE != "fold" else f"fold {r['fold']}",
                  f"{sum(x['patch'] is not None for x in rows)}/{len(rows)} repaired, end {r['end']} rc {r['rc']},"
                  f" wall {r['run_sec']:.0f}s cpu {r['cpu_sec']:.0f}s rss {r['max_rss_mb']:.0f}MB", flush=True)
    print("mentored", f"MODE={MODE} passed {sum(r['patch'] is not None for r in res)}/{len(res)} |",
          {k: sum(r["status"] == k for r in res) for k in ("ok", "reject", "none", "timecap", "memcap", "crash")})
    if os.path.isdir(ERRS) and not os.listdir(ERRS):
        os.rmdir(ERRS)
