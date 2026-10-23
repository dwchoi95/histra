"""Paths and benchmark loading shared by the experiment scripts (run them from the repository root)."""
import glob
import json
import os
import random
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from src.core.validator import passes  # noqa: E402

DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "output")
APPROACHES = ("histra", "refactory", "brafar", "lsgen")
PER = int(os.environ.get("PER", 0))       # trajectories per problem (0: all)
POOL = int(os.environ.get("POOL", 16))    # worker processes; use 4 for p02686, whose heavy tests time out under load
ONLY = os.environ.get("ONLY", "")          # comma-separated problem ids (empty: all)


def normalize(code):
    """fractions.gcd was removed in Python 3.9 (it was valid when the programs were submitted)."""
    code = code.replace("from fractions import gcd", "from math import gcd")
    return re.sub(r"\bfractions\.gcd\b", "math.gcd", code)


def problem(pid):
    """(tests, time limit in seconds, problem statement as plain text) of a benchmark problem."""
    d = os.path.join(DATA, pid)
    tests = [json.loads(l) for l in open(os.path.join(d, "tests.jsonl"), encoding="utf-8")]
    meta = json.load(open(os.path.join(d, "meta.json")))
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", open(os.path.join(d, "problem.html"), encoding="utf-8").read()))
    return tests, min(meta.get("time_limit_ms", 2000) / 1000.0, 4.0), text.strip()[:2000]


def cases():
    """One case per trajectory: its WAs (was[-1] = b), own AC (oracle, evaluation only), other students' ACs (refs)."""
    out = []
    for d in sorted(glob.glob(os.path.join(DATA, "p*", ""))):
        pid = os.path.basename(d.rstrip("/"))
        if ONLY and pid not in ONLY.split(","):
            continue
        trajs = [json.loads(l) for l in open(d + "trajectories.jsonl", encoding="utf-8")]
        tests, timeout, text = problem(pid)
        acs = [(t["user_id"], normalize(t["submissions"][-1]["code"])) for t in trajs]
        for t in random.Random(0).sample(trajs, min(PER, len(trajs))) if PER > 0 else trajs:
            was = [normalize(s["code"]) for s in t["submissions"] if s["verdict"] != "Accepted"]
            out.append(dict(pid=pid, user=t["user_id"], was=was, oracle=normalize(t["submissions"][-1]["code"]),
                            refs=[c for u, c in acs if u != t["user_id"]], tests=tests, timeout=timeout, problem=text))
    return out


def path(name):
    """output/approaches/ (HISTRA and the baselines) or output/ablation/ (RQ3) <name>.jsonl."""
    return os.path.join(OUT, "approaches" if name in APPROACHES else "ablation", name + ".jsonl")


def rows(name):
    """{(pid, user): row} of path(name), or None if the file does not exist."""
    p = path(name)
    return {(r["pid"], r["user"]): r for r in map(json.loads, open(p)) if r} if os.path.exists(p) else None
