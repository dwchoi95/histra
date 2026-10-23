"""Run Refactory (Hu et al., ASE'19; stdin/stdout fork in baselines/refactory) on the baselines.py sample.
Usage: [PER=0] [POOL=n] [ONLY=pid,..] [CAP=sec] [KEEP=dir] python run_refactory.py OUT.jsonl     (PER=0: full benchmark)
Each trajectory is one Refactory question of raw programs: was[-1] in code/wrong, the other students' ACs (refs, never
the oracle) in code/correct, the tests in ans/ (input_i = stdin, output_i = expected stdout). The fork wraps programs into
a function, runs them on stdin, and writes the repaired program back as a stdin/stdout program (basic_framework/stdin_io.py).
Refactory runs in its paper setting (-o online refactoring, -m structure mutation, -b block repair, -s 100) with its
own 60 s repair budget; CAP (default 300 s) is a wall-clock kill. Its patch is re-validated with V.verify.
KEEP=dir keeps each question directory and Refactory's log there."""
import csv, json, os, shutil, subprocess, sys, tempfile, time
from multiprocessing.pool import ThreadPool
sys.path.insert(0, os.path.dirname(__file__))
from baselines import cases, V, POOL

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "baselines", "refactory"))
RPY = os.path.join(ROOT, ".venv", "bin", "python")
CAP, KEEP = float(os.environ.get("CAP", 300)), os.environ.get("KEEP")


def run(c):
    t0, d = time.time(), tempfile.mkdtemp(prefix=f"rfty_{c['pid']}_{c['user']}_")
    q = os.path.join(d, "q")
    try:
        for sub in ("ans", "code/reference", "code/correct", "code/wrong"):
            os.makedirs(os.path.join(q, sub))
        for i, t in enumerate(c["tests"]):
            open(f"{q}/ans/input_{i}.txt", "w").write(t["input"])
            open(f"{q}/ans/output_{i}.txt", "w").write(t["output"])
        open(f"{q}/code/wrong/buggy.py", "w").write(c["was"][-1])
        for j, r in enumerate(c["refs"]):
            open(f"{q}/code/correct/ref_{j:04d}.py", "w").write(r)
        with open(f"{d}/refactory.log", "w") as log:
            subprocess.run([RPY, "run.py", "-d", d, "-q", "q", "-s", "100", "-o", "-m", "-b"], cwd=ROOT, timeout=CAP,
                           stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, env={**os.environ, "PYTHONHASHSEED": "0"})
        rows = list(csv.DictReader(open(f"{q}/refactory_online.csv"))) if os.path.exists(f"{q}/refactory_online.csv") else []
        status = rows[0]["Status"] if rows else "no_result"
        patch = rows[0]["Repair"] if status.startswith("success") else None
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
    return patch, time.time() - t0, status


if __name__ == "__main__":
    out = sys.argv[1]
    done = {(r["pid"], r["user"]) for r in map(json.loads, open(out))} if os.path.exists(out) else set()
    cs = [c for c in cases() if (c["pid"], c["user"]) not in done]     # rows are appended as they finish: a rerun resumes
    print(f"POOL={POOL} already done {len(done)}, to do {len(cs)}", flush=True)
    with ThreadPool(POOL) as p, open(out, "a") as f:
        for i, (c, (pt, sec, st)) in enumerate(zip(cs, p.imap(run, cs, chunksize=1)), 1):
            f.write(json.dumps(dict(pid=c["pid"], user=c["user"], was=c["was"], oracle=c["oracle"], patch=pt, sec=sec, status=st)) + "\n")
            f.flush()
            if i % 50 == 0:
                print(f"{i}/{len(cs)}", flush=True)
    rows = [json.loads(l) for l in open(out)]
    secs = sorted(r["sec"] for r in rows)
    print("refactory", f"passed {sum(r['patch'] is not None for r in rows)}/{len(rows)}"
          f" | mean {sum(secs)/len(secs):.1f}s median {secs[len(secs)//2]:.1f}s max {secs[-1]:.1f}s")
