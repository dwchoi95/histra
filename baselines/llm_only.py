"""All-to-LLM baseline: hand the model everything (problem + the student's FULL
submission trajectory) and ask it to repair the last attempt while preserving the
student's intent. No peer/donor, no HISTRA pipeline — this measures whether an LLM
can do the whole job by itself. If it can, a complex method like HISTRA isn't
needed; if it can't, that motivates HISTRA.

Model: gemma3n:e4b via the local Ollama OpenAI-compatible endpoint. Only the
problem statement (with its example I/O) is given — NOT the hidden test cases.
Patches are checked with our Validator.

solve(pid, timeout, tests, trajs, refs) -> {user_id: (patch_or_None, seconds)}
"""
import os, time
from src.core.validator import Validator
from baselines.par import _problem_text, _extract_code, _load_env

MODEL = os.environ.get("LLM_ONLY_MODEL", "gemma3n:e4b")
BASE = os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1")
SAMPLES = int(os.environ.get("LLM_ONLY_SAMPLES", "1"))


def _call(prompt, temperature):
    _load_env()
    from openai import OpenAI
    client = OpenAI(base_url=BASE, api_key="ollama")
    resp = client.chat.completions.create(
        model=MODEL, temperature=temperature,
        messages=[{"role": "user", "content": prompt}])
    return resp.choices[0].message.content


def _build_prompt(pdesc, traj):
    parts = [
        "You are an expert program-repair system for an introductory programming "
        "course. A student has repeatedly submitted Wrong-Answer solutions to a "
        "problem. You are given the problem and the student's FULL submission "
        "history in chronological order. Repair the student's LAST attempt so it "
        "becomes CORRECT, while PRESERVING the student's own intent and coding "
        "style.\n",
        "[Problem]\n" + pdesc + "\n",
        "[Student submission history — chronological, all Wrong Answer]",
    ]
    for i, code in enumerate(traj, 1):
        tag = " (most recent — repair THIS one)" if i == len(traj) else ""
        parts.append(f"### Attempt {i}{tag}\n```python\n{code}```")
    parts.append(
        "\n[Instructions]\n"
        "- Use the submission history to infer the student's intent: what they were "
        "trying to do and where they kept struggling. The parts that stayed "
        "consistent across attempts are their confirmed intent.\n"
        "- Produce a corrected version of the MOST RECENT attempt that passes all "
        "tests.\n"
        "- PRESERVE the student's intent: keep their overall approach/algorithm, "
        "their variable names, and their style. Make the SMALLEST change needed to "
        "make it correct — do NOT rewrite it into a different solution.\n"
        "- The program reads from standard input and writes to standard output.\n"
        "- Return ONLY the corrected Python program inside a single ```python code "
        "block, with no explanation.")
    return "\n".join(parts)


def solve(pid, timeout, tests, trajs, refs):
    Validator.init_globals(tests, timeout)
    pdesc = _problem_text(pid)
    out = {}
    for uid in trajs:
        was = trajs.get(uid) or []
        t0 = time.time()
        if not was:
            out[uid] = (None, 0.0)
            continue
        prompt = _build_prompt(pdesc, was)
        patch = None
        for _ in range(SAMPLES):
            try:
                text = _call(prompt, 0.8 if SAMPLES > 1 else 0.2)
            except Exception:
                continue
            cand = _extract_code(text)
            if cand and Validator.run(cand).passed():
                patch = cand
                break
        out[uid] = (patch, time.time() - t0)
    return out
