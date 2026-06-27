"""HISTRA-LLM: trajectory-aware, intent-preserving LLM repair.

The project's core claim is that prior methods use ONLY the last submission, so
they don't preserve the student's intent. HISTRA-LLM keeps that contribution when
introducing an LLM: it feeds the model the student's ENTIRE submission trajectory
(every WA, in order) plus a trajectory-derived intent model — which regions stayed
STABLE across all attempts (the student's confirmed intent, to preserve) and which
the student KEPT CHANGING (where they struggled — the likely bug) — and asks for a
minimal, intent-preserving fix to the last submission. Optionally a peer AC is
added as reference. The patch is validated with our Validator.

This differs from PaR (last submission + one peer only) precisely by USING THE
WHOLE TRAJECTORY. solve(pid, timeout, tests, trajs, refs) ->
{user_id: (patch_or_None, seconds)}.
"""
import os, ast, time, difflib
from src.core.validator import Validator
from src.core.standardizer import Standardizer
from src.core.sketch import Sketcher
from src.core.reformat import Reformatter
# reuse PaR's LLM plumbing (gpt-3.5-turbo, .env, code extraction, peer PSM)
from baselines.par import (_problem_text, _call_llm, _extract_code, _load_env,
                           _pass_vector, _select_peer, MODEL, SAMPLES)

USE_PEER = os.environ.get("HISTRA_LLM_PEER", "1") == "1"


# --------------------------- trajectory intent model ---------------------------
def _changed_line_idxs(traj):
    """Indices (in the LAST submission) of lines the student edited across the
    trajectory — the union of diffs between each consecutive pair, projected onto
    the final submission. This is the 'where they struggled' signal."""
    last = traj[-1].splitlines()
    changed = set()
    for a_code, b_code in zip(traj[:-1], traj[1:]):
        sm = difflib.SequenceMatcher(a=a_code.splitlines(), b=b_code.splitlines())
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != "equal" and b_code is traj[-1]:
                for j in range(j1, j2):
                    changed.add(j)
    # also mark anything that differs between the last two attempts
    if len(traj) >= 2:
        sm = difflib.SequenceMatcher(a=traj[-2].splitlines(), b=last)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != "equal":
                for j in range(j1, j2):
                    changed.add(j)
    return changed


def _annotated_last(traj):
    """Last submission with the kept-changing lines flagged for the LLM."""
    lines = traj[-1].splitlines()
    changed = _changed_line_idxs(traj)
    out = []
    for i, ln in enumerate(lines):
        out.append(ln + ("    # <-- student kept changing this" if i in changed else ""))
    return "\n".join(out)


def _stable_changed_summary(traj):
    """Short natural-language summary of stable vs changing structure from the
    HISTRA sketch (best-effort; falls back silently)."""
    try:
        std = Standardizer.run(traj)
        skt = Sketcher.run(std)
        anchor = std[-1]
        skt_org = Reformatter.run(anchor, skt)
        holes = sum(1 for n in ast.walk(skt_org) if getattr(n, "_hole", False))
        total = sum(1 for n in ast.walk(skt_org) if isinstance(n, ast.expr))
        return holes, total
    except Exception:
        return None, None


# ------------------------------------- prompt ----------------------------------
def _build_prompt(pdesc, traj, peer_code):
    parts = []
    parts.append(
        "You are repairing a student's buggy program for a competitive-programming "
        "problem. Unlike a one-shot fixer, you are given the student's ENTIRE "
        "submission history — their sequence of failed attempts — which reveals "
        "their INTENT and exactly where they kept struggling. Use it.\n")
    parts.append("[Problem]\n" + pdesc + "\n")
    parts.append("[Student submission trajectory — earliest to latest, all Wrong Answer]")
    for i, code in enumerate(traj, 1):
        tag = " (LATEST — fix THIS one)" if i == len(traj) else ""
        parts.append(f"--- Attempt {i}{tag} ---\n{code}")
    parts.append(
        "\n[Intent signal from the trajectory]\n"
        "Across the attempts above, the parts that stayed the SAME are the "
        "student's confirmed intent — preserve them and their variable names/style. "
        "The lines the student KEPT CHANGING are flagged below with "
        "'# <-- student kept changing this'; the bug is most likely there (but if a "
        "stable line is genuinely the bug, you may fix it too).\n")
    parts.append("[Latest attempt, annotated]\n" + _annotated_last(traj) + "\n")
    if peer_code:
        parts.append("[Reference: a peer student's accepted solution]\n" + peer_code + "\n")
    parts.append(
        "Task: produce the SMALLEST change to the latest attempt that passes all "
        "tests while PRESERVING the student's intent (keep the stable skeleton, "
        "their variable names and overall approach; prefer editing the flagged "
        "regions). Return ONLY the corrected Python program in a single ```python "
        "code block, no explanation.")
    return "\n".join(parts)


# ------------------------------------- solve -----------------------------------
def solve(pid, timeout, tests, trajs, refs):
    _load_env()
    Validator.init_globals(tests, timeout)
    pdesc = _problem_text(pid)

    donors = {}
    if USE_PEER:
        for uid, ac in refs.items():
            vec = _pass_vector(ac)
            if vec and all(vec):
                donors[uid] = (ac, vec)

    out = {}
    for uid in trajs:
        was = trajs.get(uid) or []
        t0 = time.time()
        if not was:
            out[uid] = (None, 0.0)
            continue
        buggy = was[-1]
        peer_code = None
        if USE_PEER and donors:
            buggy_vec = _pass_vector(buggy)
            cands = [(u, c, v) for u, (c, v) in donors.items() if u != uid]
            peer = _select_peer(buggy, buggy_vec, cands)
            peer_code = peer[1] if peer else None

        prompt = _build_prompt(pdesc, was, peer_code)
        patch = None
        for _ in range(SAMPLES):
            try:
                text = _call_llm(prompt, 0.8 if SAMPLES > 1 else 0.2)
            except Exception:
                continue
            cand = _extract_code(text)
            if cand and Validator.run(cand).passed():
                patch = cand
                break
        out[uid] = (patch, time.time() - t0)
    return out
