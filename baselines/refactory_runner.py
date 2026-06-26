"""Refactory baseline approach, wired so run.py can call it like the others.

For one problem it (1) writes the problem into Refactory's folder layout with each
program wrapped into a single `def __main__()` and the buggy targets' own ACs
excluded from the correct pool (no self-oracle leakage), (2) runs the patched
Refactory in its Python-3.8 venv as a subprocess (stdin mode, incremental save),
then (3) reads the per-wrong incremental results, unwraps each patch and
re-validates it with OUR Validator.

solve(pid, timeout, tests, trajs, refs) -> {user_id: (patch_or_None, seconds)}
"""
import os, ast, json, time, shutil, textwrap, subprocess
from src.core.validator import Validator

HERE = os.path.dirname(os.path.abspath(__file__))
CLONE = os.path.join(HERE, "refactory")
VENV = os.path.join(CLONE, ".venv38", "bin", "python")
RUN_ROOT = os.path.join(CLONE, "_run")
TIMEOUT = int(os.environ.get("REFACTORY_TIMEOUT", "7200"))   # wall seconds/problem


# ---- whole-program <-> single-function wrapping (so Refactory doesn't gut it) --
def _strip_main_guard(code):
    try:
        tree = ast.parse(code)
    except Exception:
        return code
    body = []
    for node in tree.body:
        if (isinstance(node, ast.If) and isinstance(node.test, ast.Compare)
                and isinstance(node.test.left, ast.Name)
                and node.test.left.id == "__name__"):
            body.extend(node.body)
        else:
            body.append(node)
    try:
        return ast.unparse(ast.Module(body=body, type_ignores=[]))
    except Exception:
        return code

def _wrap(code):
    body = _strip_main_guard(code).rstrip("\n") or "pass"
    return "def __main__():\n" + textwrap.indent(body, "    ") + "\n"

def _unwrap(code):
    try:
        tree = ast.parse(code)
    except Exception:
        return None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "__main__":
            try:
                return ast.unparse(ast.Module(body=node.body, type_ignores=[]))
            except Exception:
                return None
    return code


def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _build_layout(pid, tests, trajs, refs):
    base = os.path.join(RUN_ROOT, pid)
    if os.path.isdir(base):
        shutil.rmtree(base)
    code_dir = os.path.join(base, "code")
    for i, tc in enumerate(tests, 1):
        _write(os.path.join(base, "ans", f"input_{i:03d}.txt"), tc["input"])
        _write(os.path.join(base, "ans", f"output_{i:03d}.txt"), tc["output"])
    _write(os.path.join(code_dir, "global.py"), "")

    # Correct pool = EVERY student's AC. No-leakage is enforced inside the patched
    # Refactory (it drops correct_<uid>.py when repairing wrong_<uid>.py), which is
    # the only way to exclude self on full data where every student is also a
    # target. The reference dir is left empty so it cannot leak either.
    pool = [(u, c) for u, c in refs.items() if c and c.strip()]
    if not pool:
        return base, {}
    os.makedirs(os.path.join(code_dir, "reference"), exist_ok=True)
    for u, c in pool:
        _write(os.path.join(code_dir, "correct", f"correct_{u}.py"), _wrap(c))

    manifest = {}
    for u in sorted(trajs):
        was = trajs.get(u) or []
        if not was or not was[-1].strip():
            continue
        try:
            ast.parse(was[-1])
        except Exception:
            continue
        _write(os.path.join(code_dir, "wrong", f"wrong_{u}.py"), _wrap(was[-1]))
        manifest[u] = was[-1]
    return base, manifest


def solve(pid, timeout, tests, trajs, refs):
    base, manifest = _build_layout(pid, tests, trajs, refs)
    inc_path = os.path.join(base, "incremental.jsonl")
    if os.path.exists(inc_path):
        os.remove(inc_path)

    if manifest and os.path.exists(VENV):
        cmd = [VENV, "run.py", "-d", "_run", "-q", pid, "-s", "100", "-o", "-m", "-b"]
        env = {**os.environ, "REFACTORY_STDIN": "1"}
        try:
            subprocess.run(cmd, cwd=CLONE, env=env, timeout=TIMEOUT,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            pass   # incremental.jsonl still holds whatever finished

    # collect per-wrong results, unwrap + re-validate with OUR validator
    repaired = {}   # uid -> (rep_code, secs)
    if os.path.exists(inc_path):
        for line in open(inc_path, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            fn = rec.get("file_name", "")
            if not (fn.startswith("wrong_") and fn.endswith(".py")):
                continue
            uid = fn[len("wrong_"):-len(".py")]
            secs = float(rec.get("total_time", 0) or 0)
            code = rec.get("rep_code", "") if str(rec.get("status", "")).startswith("success") else ""
            repaired[uid] = (code, secs)

    Validator.init_globals(tests, timeout)
    out = {}
    for u in trajs:
        rep, secs = repaired.get(u, ("", 0.0))
        patch = None
        if rep:
            cand = _unwrap(rep)
            try:
                if cand and Validator.run(cand).passed():
                    patch = cand
            except Exception:
                patch = None
        out[u] = (patch, secs)
    return out
