"""Run Brafar (Xie et al., ISSTA'24) in its paper setting (-s 100); setup: baselines/brafar/setup.sh.
Usage: [POOL=4] [ONLY=pid,..] [CAP=sec] [KEEP=dir] [RERUN=rows.jsonl] python src/experiments/run_brafar.py [OUT.jsonl]
  CAP: wall-clock kill (default 300 s); KEEP: keep each question dir and log; RERUN: run only the listed rows
Rows record `timeouts`: Brafar's internal test/fault-localization timeouts, whose outcome depends on machine load."""
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from multiprocessing.pool import ThreadPool

from common import POOL, cases, passes, path
from measure import measure

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "baselines", "brafar", "upstream")
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
        if patch and not passes(patch, c["tests"], c["timeout"]):
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
    out = sys.argv[1] if len(sys.argv) > 1 else path("brafar")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    done = {(r["pid"], r["user"]) for r in map(json.loads, open(out))} if os.path.exists(out) else set()
    cs = [c for c in cases() if (c["pid"], c["user"]) not in done]     # appended as they finish: a rerun resumes
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
    measure(out)
    rows = [json.loads(l) for l in open(out)]
    secs = sorted(r["sec"] for r in rows)
    print("brafar", f"passed {sum(r['patch'] is not None for r in rows)}/{len(rows)}"
          f" | mean {sum(secs)/len(secs):.1f}s median {secs[len(secs)//2]:.1f}s max {secs[-1]:.1f}s")
