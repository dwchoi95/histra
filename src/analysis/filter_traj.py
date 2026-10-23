"""Filter data/<pid>/trajectories.jsonl: drop any trajectory containing a submission that
(a) fails ast.parse, or (b) whose Validator verdict disagrees with the recorded verdict
(Accepted must pass ALL tests; Wrong Answer must fail at least one).

Dry-run by default (reports only). Pass --apply to overwrite trajectories.jsonl.
Usage: .venv/bin/python src/analysis/filter_traj.py [pid ...] [--apply]
"""
import sys, os, ast, json, time, tempfile
sys.path.insert(0, os.getcwd())                     # project root -> 'src' package importable
from src.core.validator import Validator
from src.types import TestCase, Status
import warnings
warnings.filterwarnings("ignore")

DATA = os.path.join(os.getcwd(), "data")


def _parses(code):
    try:
        ast.parse(code); return True
    except (SyntaxError, ValueError):
        return False


def passes_all(code, testcases, timeout):
    """True iff code passes ALL tests; early-stop at the first non-pass."""
    Validator.timeout = timeout
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as fh:
        fh.write(code); path = fh.name
    try:
        for tc in testcases:
            if Validator.run_case(path, tc).status != Status.PASSED:
                return False
        return True
    finally:
        try: os.unlink(path)
        except OSError: pass


def load_tests(pdir):
    tcs = []
    with open(os.path.join(pdir, "tests.jsonl"), encoding="utf-8") as f:
        for i, ln in enumerate(f):
            d = json.loads(ln)
            tcs.append(TestCase(id=i, input=d["input"], output=d["output"]))
    timeout = 2.0
    mp = os.path.join(pdir, "meta.json")
    if os.path.exists(mp):
        with open(mp, encoding="utf-8") as f:
            timeout = json.load(f).get("time_limit_ms", 2000) / 1000.0
    return tcs, timeout


def good_traj(traj, tcs, timeout):
    for s in traj["submissions"]:
        if not _parses(s["code"]):
            return False, "unparsable"
        expect_pass = (s["verdict"] == "Accepted")
        if passes_all(s["code"], tcs, timeout) != expect_pass:
            return False, "verdict_mismatch"
    return True, None


def main():
    apply = "--apply" in sys.argv
    pids = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not pids:
        pids = sorted(d for d in os.listdir(DATA)
                      if d.startswith("p") and os.path.isdir(os.path.join(DATA, d)))
    tot_keep = tot_drop = 0
    for pid in pids:
        pdir = os.path.join(DATA, pid)
        fp = os.path.join(pdir, "trajectories.jsonl")
        if not os.path.exists(fp):
            continue
        trajs = [json.loads(ln) for ln in open(fp, encoding="utf-8")]
        tcs, timeout = load_tests(pdir)
        t0 = time.time()
        kept, drops = [], {"unparsable": 0, "verdict_mismatch": 0}
        for tr in trajs:
            ok, why = good_traj(tr, tcs, timeout)
            if ok:
                kept.append(tr)
            else:
                drops[why] += 1
        tot_keep += len(kept); tot_drop += (len(trajs) - len(kept))
        print(f"{pid}: {len(trajs)} -> {len(kept)}  "
              f"(drop {len(trajs)-len(kept)}: unparsable={drops['unparsable']} "
              f"verdict_mismatch={drops['verdict_mismatch']})  {time.time()-t0:.0f}s", flush=True)
        if apply and len(kept) != len(trajs):
            with open(fp, "w", encoding="utf-8") as f:
                for r in kept:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\nTOTAL kept={tot_keep} dropped={tot_drop}  ({'APPLIED' if apply else 'DRY-RUN'})")


if __name__ == "__main__":
    main()
