"""Run Brafar (Xie et al., ISSTA'24; stdin/stdout fork in baselines/brafar) on the baselines.py sample.
Usage: [PER=0] [POOL=n] [ONLY=pid,..] [CAP=sec] [KEEP=dir] python run_brafar.py OUT.jsonl     (PER=0: full benchmark)
Each trajectory is one Brafar question, laid out like run_refactory.py: was[-1] in code/wrong, the other students' ACs
(refs, never the oracle) in code/correct with the first one as code/reference/reference.py (Brafar always adds it), the
tests in ans/ (input_i = stdin, output_i = expected stdout). Programs are written wrapped as `def stdin_main(): ...`, the
fork runs them on stdin (basic_framework/stdin_io.py), and the repaired function is unwrapped back into a stdin/stdout
program. Brafar runs in its paper setting (-s 100: all correct programs); its in-process tests use the problem's time
limit. CAP (default 300 s) is a wall-clock kill. Its patch is re-validated with V.verify. Each row records `timeouts`,
the test and fault-localization timeouts inside Brafar (stdin_io marks them in its log): only a case without timeouts
is independent of the machine's load, so the others are rerun on an idle machine (RERUN=rows.jsonl reruns those rows).
KEEP=dir keeps each question directory and Brafar's log there."""
import csv, json, os, shutil, subprocess, sys, tempfile, time
from multiprocessing.pool import ThreadPool
sys.path.insert(0, os.path.dirname(__file__))
from baselines import cases, V, POOL

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "baselines", "brafar"))
RPY = os.path.join(ROOT, ".venv", "bin", "python")
CAP, KEEP = float(os.environ.get("CAP", 300)), os.environ.get("KEEP")
sys.path.insert(0, ROOT)
from basic_framework import stdin_io

csv.field_size_limit(sys.maxsize)


def run(c):
    t0, d, to = time.time(), tempfile.mkdtemp(prefix=f"brfr_{c['pid']}_{c['user']}_"), None
    q = os.path.join(d, "q")
    try:
        for sub in ("ans", "code/reference", "code/correct", "code/wrong"):
            os.makedirs(os.path.join(q, sub))
        for i, t in enumerate(c["tests"]):
            open(f"{q}/ans/input_{i}.txt", "w").write(t["input"])
            open(f"{q}/ans/output_{i}.txt", "w").write(t["output"])
        open(f"{q}/code/wrong/buggy.py", "w").write(stdin_io.wrap(c["was"][-1]))
        open(f"{q}/code/reference/reference.py", "w").write(stdin_io.wrap(c["refs"][0]))
        for j, r in enumerate(c["refs"][1:], 1):
            open(f"{q}/code/correct/ref_{j:04d}.py", "w").write(stdin_io.wrap(r))
        with open(f"{d}/brafar.log", "w") as log:   # cwd = d: the fault localizer writes its trace to ./log.txt
            subprocess.run([RPY, os.path.join(ROOT, "run.py"), "-d", d, "-q", "q", "-s", "100"], cwd=d, timeout=CAP,
                           stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                           env={**os.environ, "PYTHONHASHSEED": "0", "BRAFAR_TO": str(c["timeout"])})
        log = open(f"{d}/brafar.log", errors="replace").read()
        to = {k: log.count("histra:timeout:" + k) for k in ("test", "fl")}
        res = f"{q}/brafar_result_100.csv"
        rows = list(csv.DictReader(open(res))) if os.path.exists(res) else []
        status = rows[0]["Status"] if rows else "no_result"
        patch = stdin_io.unwrap(rows[0]["Repair"], q, "buggy.py") if status == "True" else None
        if patch and not V.verify(patch, c["tests"], c["timeout"]).passed:
            patch, status = None, status + "+verify_fail"
    except subprocess.TimeoutExpired:
        patch, status = None, "wall_timeout"
    except Exception as e:
        patch, status = None, f"driver_error:{type(e).__name__}"
    finally:
        if KEEP:
            shutil.copytree(d, os.path.join(KEEP, os.path.basename(d)), dirs_exist_ok=True)
        shutil.rmtree(d, ignore_errors=True)
    return patch, time.time() - t0, status, to


if __name__ == "__main__":
    out = sys.argv[1]
    done = {(r["pid"], r["user"]) for r in map(json.loads, open(out))} if os.path.exists(out) else set()
    cs = [c for c in cases() if (c["pid"], c["user"]) not in done]     # rows are appended as they finish: a rerun resumes
    if os.environ.get("RERUN"):                                         # only these rows, appended to OUT
        want = {(r["pid"], r["user"]) for r in map(json.loads, open(os.environ["RERUN"]))}
        cs = [c for c in cs if (c["pid"], c["user"]) in want]
    print(f"POOL={POOL} already done {len(done)}, to do {len(cs)}", flush=True)
    with ThreadPool(POOL) as p, open(out, "a") as f:
        for i, (c, (pt, sec, st, to)) in enumerate(zip(cs, p.imap(run, cs, chunksize=1)), 1):
            f.write(json.dumps(dict(pid=c["pid"], user=c["user"], was=c["was"], oracle=c["oracle"], patch=pt, sec=sec, status=st,
                                    timeouts=to)) + "\n")
            f.flush()
            if i % 50 == 0:
                print(f"{i}/{len(cs)}", flush=True)
    rows = [json.loads(l) for l in open(out)]
    secs = sorted(r["sec"] for r in rows)
    print("brafar", f"passed {sum(r['patch'] is not None for r in rows)}/{len(rows)}"
          f" | mean {sum(secs)/len(secs):.1f}s median {secs[len(secs)//2]:.1f}s max {secs[-1]:.1f}s")
