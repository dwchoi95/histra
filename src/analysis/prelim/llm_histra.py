"""Generality (paper §4): HISTRA's history guidance on top of an LLM-based repairer.
  full     ask the model to change only the hole lines; if that patch fails, fall back to the plain LLM
           patch (baselines.py llm output); minimize the passing patch with HISTRA's Minimizer
  minonly  plain LLM patch + HISTRA's Minimizer (no hole-only prompt)
  keep     controls for "full" (final review K2), same fallback and Minimizer:
           keep: no line list, only "change as few lines as possible"; randlines: the "full" prompt with as many
           randomly chosen lines as the history marks (seeded per trajectory)
Usage: [PER=0] python llm_histra.py {full|minonly|keep|randlines} LLM_BASELINE.jsonl OUT.jsonl [MODEL]"""
import os, json, sys, ast, random
from multiprocessing.pool import ThreadPool
sys.path.insert(0, os.path.dirname(__file__))
from baselines import cases, V, run_llm
from src.core.histra import HISTRA
from src.core.standardizer import Standardizer
from src.core.minimize import Minimizer

PROMPT = ("You are given a programming problem and a student's Python 3 program that gives wrong answers on some tests. "
          "Across the student's earlier attempts, only the following lines kept changing; every other line stayed the same:\n"
          "{lines}\n\nFix the program so that it solves the problem. Change only the lines listed above if possible, and keep "
          "every other line exactly as written. Output ONLY the complete corrected program in one ```python code block, "
          "with no explanation.\n\nProblem:\n{problem}\n\nStudent program:\n```python\n{buggy}\n```")
KEEP = ("You are given a programming problem and a student's Python 3 program that gives wrong answers on some tests. "
        "Fix the program so that it solves the problem. Change as few lines as possible and keep every other line exactly "
        "as written. Output ONLY the complete corrected program in one ```python code block, with no explanation.\n\n"
        "Problem:\n{problem}\n\nStudent program:\n```python\n{buggy}\n```")


def hole_lines(pristine, holed):
    """Source lines covered by the holes of the student's latest submission."""
    out = set()
    for parent in ast.walk(pristine):
        for n in ast.iter_child_nodes(parent):
            if id(n) in holed and id(parent) not in holed and hasattr(n, "lineno"):
                out.update(range(n.lineno, (n.end_lineno or n.lineno) + 1))
    return sorted(out)


def run(args):
    c, mode, base, model = args
    validate = lambda s: V.verify(s, c["tests"], c["timeout"]).passed
    try:
        _, _, (pristine, holed) = HISTRA._sketch(Standardizer.run(c["was"]))
    except Exception:
        return None, None, None
    patch, phase, raw = None, None, None
    lines = hole_lines(pristine, holed) if mode in ("full", "randlines", "keep") else []   # same trajectories get a 2nd try
    if mode == "randlines" and lines:
        n = len(c["was"][-1].splitlines())
        lines = sorted(random.Random(c["user"]).sample(range(1, n + 1), min(len(lines), n)))
    if mode == "keep" and lines:
        patch, raw = run_llm(c, model, KEEP.format(problem=c["problem"], buggy=c["was"][-1]), with_raw=True)
        phase = "hole" if patch else None
    elif lines:
        src_lines = c["was"][-1].splitlines()
        listing = "\n".join(f"Line {i}: {src_lines[i - 1]}" for i in lines if i <= len(src_lines))
        patch, raw = run_llm(c, model, PROMPT.format(lines=listing, problem=c["problem"], buggy=c["was"][-1]), with_raw=True)
        phase = "hole" if patch else None
    if patch is None and base is not None:
        patch, phase = base, "free"
    if patch is not None:
        try:
            patch = Minimizer(pristine, holed).run(patch, validate)
        except Exception:
            pass
    return patch, phase, raw


if __name__ == "__main__":
    mode, base_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
    model = sys.argv[4] if len(sys.argv) > 4 else "gemma4:e4b"
    base = {(r["pid"], r["user"]): r["patch"] for r in map(json.loads, open(base_path))}
    cs = cases()
    with ThreadPool(4) as p:
        res = p.map(run, [(c, mode, base.get((c["pid"], c["user"])), model) for c in cs])
    with open(out, "w") as f:
        for c, (pt, ph, raw) in zip(cs, res):
            f.write(json.dumps(dict(pid=c["pid"], user=c["user"], was=c["was"], oracle=c["oracle"], patch=pt, phase=ph, raw=raw)) + "\n")
    print(mode, f"passed {sum(p is not None for p, _, _ in res)}/{len(cs)} | hole-only {sum(ph == 'hole' for _, ph, _ in res)}")
