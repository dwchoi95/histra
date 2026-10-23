"""Run representative repairers on a fixed per-problem sample and store their passing patches.
  merge: Sarfgen-style AC merge (src/core/merge.py), top-20 ACs of OTHER students by weighted Jaccard
  llm:   direct LLM repair (local gemma4:e4b, one sample, temperature 0)
Usage: [PER=0] [POOL=n] [ONLY=pid,..] python baselines.py {merge|merge-min|llm} OUT.jsonl [MODEL]   (PER=0: full benchmark)"""
import json, os, re, sys, glob, random, subprocess
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from src.core.merge import MergeRepair
from src.utils.features import Featurizer
from src.model.client import ModelClient

DATA, SEED = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")), 0
PER = int(os.environ.get("PER", 30))      # trajectories per problem; PER=0 runs the full benchmark
POOL = int(os.environ.get("POOL", 16))    # worker processes (heavy tests time out under more load)
ONLY = os.environ.get("ONLY", "")          # comma-separated problem ids to run (empty: all)
PY = sys.executable


def normalize(code):  # fractions.gcd was removed in Python 3.9 (valid at submission time)
    code = code.replace("from fractions import gcd", "from math import gcd")
    return re.sub(r"\bfractions\.gcd\b", "math.gcd", code)


class _R:
    def __init__(self, ok): self.passed = ok


class V:
    @staticmethod
    def verify(src, tests, timeout=3.0):
        for t in tests:
            try:
                p = subprocess.run([PY, "-c", src], input=t["input"], capture_output=True, text=True, timeout=timeout)
            except subprocess.TimeoutExpired:
                return _R(False)
            if p.returncode != 0 or " ".join(p.stdout.split()) != " ".join(t["output"].split()):
                return _R(False)
        return _R(True)


def cases():
    out = []
    for d in sorted(glob.glob(f"{DATA}/p*/")):
        pid = os.path.basename(d.rstrip("/"))
        if ONLY and pid not in ONLY.split(","):
            continue
        trajs = [json.loads(l) for l in open(d + "trajectories.jsonl", encoding="utf-8")]
        tests = [json.loads(l) for l in open(d + "tests.jsonl", encoding="utf-8")]
        meta = json.load(open(d + "meta.json")) if os.path.exists(d + "meta.json") else {}
        tout = min(meta.get("time_limit_ms", 2000) / 1000.0, 4.0)
        prob = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", open(d + "problem.html", encoding="utf-8").read())).strip()[:2000]
        acs = [(t["user_id"], normalize(t["submissions"][-1]["code"])) for t in trajs]
        for t in (random.Random(SEED).sample(trajs, min(PER, len(trajs))) if PER > 0 else trajs):
            was = [normalize(s["code"]) for s in t["submissions"] if s["verdict"] != "Accepted"]
            out.append(dict(pid=pid, user=t["user_id"], was=was, oracle=normalize(t["submissions"][-1]["code"]),
                            refs=[c for u, c in acs if u != t["user_id"]], tests=tests, timeout=tout, problem=prob))
    return out


def run_merge(c, sarfgen=False):
    """sarfgen=True: keep the smallest-edit passing merge among all candidates (Sarfgen's minimal repair) and give
    its minimization the same budget as HISTRA (20); otherwise the first passing merge with 10 reverts."""
    bf = Featurizer.features(c["was"][-1])
    feats = [Featurizer.features(r) for r in c["refs"]]
    idf = Featurizer.idf(feats)
    order = sorted(range(len(feats)), key=lambda i: -Featurizer.wjaccard(bf, feats[i], idf))
    r = MergeRepair().repair(c["was"][-1], [c["refs"][i] for i in order[:20]], c["tests"], V,
                             timeout=c["timeout"], fast=not sarfgen, minimize=True, min_budget=20 if sarfgen else 10)
    return r["patch"]


PROMPT = ("You are given a programming problem and a student's Python 3 program that gives wrong answers on some tests. "
          "Fix the program so that it solves the problem. Output ONLY the complete corrected program in one ```python code block, "
          "with no explanation.\n\nProblem:\n{problem}\n\nStudent program:\n```python\n{buggy}\n```")


MODELS = {"gemma4:e4b": (False, 2048), "gpt-oss:20b": ("low", 4096)}   # model -> (think, max tokens); gpt-oss cannot disable reasoning


def run_llm(c, model="gemma4:e4b", prompt=None, with_raw=False):
    """Passing program or None; with_raw=True also returns the raw model response."""
    client = ModelClient(model, timeout=900)
    try:
        txt = client.generate(prompt or PROMPT.format(problem=c["problem"], buggy=c["was"][-1]),
                              temperature=0.0, think=MODELS[model][0], max_tokens=MODELS[model][1]).text
    except RuntimeError:
        return (None, None) if with_raw else None
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", txt, re.S)
    src = blocks[-1] if blocks and V.verify(blocks[-1], c["tests"], c["timeout"]).passed else None
    return (src, txt) if with_raw else src


if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    cs = cases()
    raws = [None] * len(cs)
    if mode in ("merge", "merge-min"):
        with Pool(POOL) as p:
            patches = p.starmap(run_merge, [(c, mode == "merge-min") for c in cs], chunksize=2)
    else:
        model = sys.argv[3] if len(sys.argv) > 3 else "gemma4:e4b"
        with ThreadPool(4) as p:
            patches, raws = zip(*p.map(lambda c: run_llm(c, model, with_raw=True), cs))
    with open(out, "w") as f:
        for c, pt, raw in zip(cs, patches, raws):
            row = dict(pid=c["pid"], user=c["user"], was=c["was"], oracle=c["oracle"], patch=pt)
            if raw is not None:
                row["raw"] = raw
            f.write(json.dumps(row) + "\n")
    print(mode, f"passed {sum(p is not None for p in patches)}/{len(cs)}")
