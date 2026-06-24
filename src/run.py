import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))      # src/ (import root)
ROOT = os.path.dirname(HERE)                            # repo root
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from core.searcher import Searcher
from core.histra import HISTRA
from verify.types import TestCase
from model.client import ModelClient
from types import Config

DATA = os.path.join(ROOT, "data")
MODEL = "gemma4:e4b"

# ablation presets (one OFAT change each from Full) -- select with --ablation NAME|all
ABLATIONS = {
    "full":           Config(),
    "no-reformat":    Config(reformat=False),
    "no-standardize": Config(standardize=False),
    "ref-random":     Config(ref="random"),
    "ref-oracle":     Config(ref="oracle"),
    "wan-ac":         Config(sketch="wan+ac"),
    "was-only":       Config(sketch="was", ref="none"),
    "plain":          Config(repair="plain"),
}


def load_problem(pid):
    pdir = os.path.join(DATA, pid)
    with open(os.path.join(pdir, "trajectories.jsonl"), encoding="utf-8") as f:
        trajs = [json.loads(ln) for ln in f]
    with open(os.path.join(pdir, "tests.jsonl"), encoding="utf-8") as f:
        tests = [json.loads(ln) for ln in f]                       # ALL tests, no cap
    tcs = [TestCase(input=t["input"], output=t["output"]) for t in tests]
    with open(os.path.join(pdir, "problem.html"), encoding="utf-8") as f:
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", f.read())).strip()[:1200]
    timeout_s = 2.0
    mp = os.path.join(pdir, "meta.json")
    if os.path.exists(mp):
        with open(mp, encoding="utf-8") as f:
            timeout_s = json.load(f).get("time_limit_ms", 2000) / 1000.0
    return trajs, tcs, text, timeout_s


def ac_pool(trajs, exclude_user=None):
    codes, users = [], []
    for t in trajs:
        ac = t["submissions"][-1]
        if ac["verdict"] == "Accepted" and t["user_id"] != exclude_user:
            codes.append(ac["code"]); users.append(t["user_id"])
    return codes, users


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else 0.0


def run_batch(pipe, trajs, n, config, *, verbose=False, log_each=False):
    """Run config over trajs[:n] (paired across ablations). Returns a metrics dict.
    %RR = pass/n; ATT = mean repair time over attempted; TED/intent over passed."""
    m = {"n": 0, "pass": 0, "empty": 0, "skip": 0, "inject": 0, "fails": {},
         "secs": [], "ted": [], "intent": []}
    for i, t in enumerate(trajs[:n], 1):
        r = pipe.run_case(t, config=config, verbose=(verbose and i == 1))
        m["n"] += 1
        if r.skip:
            m["skip"] += 1; tag = f"skip({r.skip})"
        else:
            m["pass"] += r.passed; m["empty"] += r.empty
            m["inject"] += r.injected
            m["secs"].append(r.seconds)                  # attempted (repair time)
            if r.passed:                                  # TED/intent over fixed (passing) patches
                m["ted"].append(r.ted); m["intent"].append(r.intent)
            if r.fail_reason:
                m["fails"][r.fail_reason] = m["fails"].get(r.fail_reason, 0) + 1
            tag = f"pass={r.passed}" + (f" fail({r.fail_reason})" if r.fail_reason else "")
        if log_each:
            print(f"[{i:3d}] {t['user_id']:12s} {tag}", flush=True)
    m["RR"] = m["pass"] / (m["n"] or 1)
    m["ATT"] = _mean(m["secs"])
    m["TED"] = _mean(m["ted"])
    m["IP"] = _mean(m["intent"])
    return m


def main():
    pid = sys.argv[1] if len(sys.argv) > 1 else "p02909"
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else None
    abl = sys.argv[sys.argv.index("--ablation") + 1] if "--ablation" in sys.argv else "full"
    if abl != "all" and abl not in ABLATIONS:
        sys.exit(f"unknown --ablation {abl}; choose from: all, {', '.join(ABLATIONS)}")

    trajs, tests, problem, timeout_s = load_problem(pid)
    n = n or len(trajs)
    codes, users = ac_pool(trajs)
    index = Searcher(codes, users=users)
    client = ModelClient(model=MODEL, mode="preflight", timeout=120.0)  # fail-fast on hang
    pipe = HISTRA(index, problem, tests, client, timeout=timeout_s)
    print(f"problem {pid}: {len(trajs)} traj, {len(tests)} tests, timeout={timeout_s}s, "
          f"AC pool {len(index)} | ablation={abl} n={n}")

    names = list(ABLATIONS) if abl == "all" else [abl]
    rows = []
    for name in names:
        m = run_batch(pipe, trajs, n, ABLATIONS[name],
                      verbose=(abl != "all"), log_each=(abl != "all"))
        d = m["n"] or 1
        fails = " ".join(f"{k}={v}" for k, v in sorted(m["fails"].items()))
        print(f"[{name:14s}] %RR={m['RR']:.0%} ({m['pass']}/{d}) "
              f"TED={m['TED']:.1f} IP={m['IP']:+.2f} ATT={m['ATT']:.1f}s "
              f"skip={m['skip']} empty={m['empty']} | {fails}", flush=True)
        rows.append((name, m))

    if abl == "all":
        print(f"\n=== ABLATION (problem {pid}, n={n}, paired) ===")
        print("%RR=repair rate  TED=TED(WAn,fixed)|passed  IP=intent-preservation|passed  ATT=repair sec")
        print(f"{'variant':15s} {'%RR':>8} {'TED':>6} {'IP':>6} {'ATT':>6} "
              f"{'skip':>5} {'wrong':>6} {'rterr':>6} {'tle':>4}")
        for name, m in rows:
            d = m["n"] or 1
            f = m["fails"]
            print(f"{name:15s} {m['pass']:3d}/{d:<3d} {m['TED']:6.1f} {m['IP']:+6.2f} "
                  f"{m['ATT']:6.1f} {m['skip']:5d} "
                  f"{f.get('wrong_output',0):6d} {f.get('runtime_error',0):6d} {f.get('timeout',0):4d}")


if __name__ == "__main__":
    main()
