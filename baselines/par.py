"""PaR (Peer-aided Repairer) baseline approach, adapted to the HISTRA dataset.

Faithful re-implementation of PaR (Zhao et al., 2024): PSM peer selection
(0.25 * (test_pass_match + bm25_norm + ast_match + dataflow_match)) + the PaR
prompt + an LLM call, evaluated with our Validator. The paper's best model is
gpt-3.5-turbo, so this calls the OpenAI Chat Completions API (set OPENAI_API_KEY).

solve(pid, timeout, tests, trajs, refs) -> {user_id: (patch_or_None, seconds)}
"""
import os, re, time, json
from src.core.validator import Validator
from src.types import Status
from src.utils import metrics as _metrics  # noqa: F401 (kept for parity)

MODEL = os.environ.get("PAR_MODEL", "gpt-3.5-turbo")
TOPK = int(os.environ.get("PAR_PSM_TOPK", "25"))   # BM25 prefilter before CodeBLEU
SAMPLES = int(os.environ.get("PAR_SAMPLES", "1"))   # LLM samples per buggy (pass@k)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TOK = re.compile(r"[A-Za-z_]\w*|\d+|\S")
_CODEBLOCK = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)


def _problem_text(pid):
    path = os.path.join(ROOT, "data", pid, "problem.html")
    if not os.path.exists(path):
        return ""
    html = open(path, encoding="utf-8").read()
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _pass_vector(code):
    try:
        results = Validator.run(code)
    except Exception:
        return None
    return [tr.result is not None and tr.result.status == Status.PASSED
            for tr in results.ts]


def _codebleu_terms(buggy, peer):
    from codebleu import calc_codebleu
    try:
        r = calc_codebleu([peer], [buggy], lang="python",
                          weights=(0.25, 0.25, 0.25, 0.25))
        return r.get("syntax_match_score", 0.0), r.get("dataflow_match_score", 0.0)
    except Exception:
        return 0.0, 0.0


def _select_peer(buggy, buggy_vec, candidates):
    """candidates: list[(uid, code, vec)] -> (uid, code) maximizing PSM score."""
    if not candidates:
        return None
    from rank_bm25 import BM25Okapi
    corpus = [_TOK.findall(c) for _, c, _ in candidates]
    bm25 = BM25Okapi(corpus)
    bm = bm25.get_scores(_TOK.findall(buggy))
    lo, hi = min(bm), max(bm)
    span = (hi - lo) or 1.0
    bm_norm = [(s - lo) / span for s in bm]
    order = sorted(range(len(candidates)), key=lambda i: bm[i], reverse=True)[:TOPK]
    bpass = sum(1 for v in (buggy_vec or []) if v)
    best, best_psm = None, -1.0
    for i in order:
        uid, code, vec = candidates[i]
        if buggy_vec and vec:
            same = sum(1 for a, b in zip(buggy_vec, vec) if a and b)
            ppass = sum(1 for b in vec if b)
            tmatch = (2 * same) / ((bpass + ppass) or 1)
        else:
            tmatch = 0.0
        ast_m, df_m = _codebleu_terms(buggy, code)
        psm = 0.25 * (tmatch + bm_norm[i] + ast_m + df_m)
        if psm > best_psm:
            best_psm, best = psm, (uid, code)
    return best


def _build_prompt(pdesc, peer_code, buggy_code):
    return (
        "There is a Python programming problem. Below is the problem description, "
        "the input/output format and examples, a correct reference solution by a "
        "peer student, and a buggy program with semantic errors written by a "
        "student. The program reads from standard input and writes to standard "
        "output. Please fix the buggy code and return the corrected program.\n\n"
        "[Problem]\n" + pdesc + "\n[End of Problem]\n\n"
        "[Reference Code]\n" + peer_code + "\n[End of Reference Code]\n\n"
        "[Buggy Code]\n" + buggy_code + "\n[End of Buggy Code]\n\n"
        "Return ONLY the corrected Python program inside a single ```python code "
        "block, with no explanation.")


def _build_prompt_traj(pdesc, peer_code, traj):
    """PaR+Trajectory: the PaR prompt unchanged, plus the student's full submission
    history and one instruction to use it to preserve the student's intent. The
    last attempt IS the buggy code shown above."""
    history = "\n".join(
        f"--- Attempt {i} (Wrong Answer)"
        f"{' (= the Buggy Code above)' if i == len(traj) else ''} ---\n{c}"
        for i, c in enumerate(traj, 1))
    return (
        "There is a Python programming problem. Below is the problem description, "
        "the input/output format and examples, a correct reference solution by a "
        "peer student, and a buggy program with semantic errors written by a "
        "student. The program reads from standard input and writes to standard "
        "output. Please fix the buggy code and return the corrected program.\n\n"
        "[Problem]\n" + pdesc + "\n[End of Problem]\n\n"
        "[Reference Code]\n" + peer_code + "\n[End of Reference Code]\n\n"
        "[Buggy Code]\n" + traj[-1] + "\n[End of Buggy Code]\n\n"
        "[Student Submission History — earliest to latest]\n" + history +
        "\n[End of Submission History]\n\n"
        "Additionally, use the student's submission history above to understand and "
        "PRESERVE the student's intent: fix the buggy code with the smallest change "
        "that keeps the student's own approach and coding style.\n\n"
        "Return ONLY the corrected Python program inside a single ```python code "
        "block, with no explanation.")


def _load_env():
    """Load baselines/.env (KEY=VALUE lines) into os.environ if not already set.
    The OPENAI_API_KEY lives there and the file is gitignored."""
    path = os.path.join(HERE, ".env")
    if not os.path.exists(path):
        return
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


HERE = os.path.dirname(os.path.abspath(__file__))


def _call_llm(prompt, temperature):
    _load_env()
    from openai import OpenAI
    base = os.environ.get("LLM_BASE_URL")  # e.g. http://localhost:11434/v1 for Ollama
    client = OpenAI(base_url=base, api_key="ollama") if base else OpenAI()
    resp = client.chat.completions.create(
        model=MODEL, temperature=temperature,
        messages=[{"role": "user", "content": prompt}])
    return resp.choices[0].message.content


def _extract_code(text):
    m = _CODEBLOCK.findall(text or "")
    return (max(m, key=len).strip() if m else (text or "").strip())


def solve(pid, timeout, tests, trajs, refs, use_traj=False):
    """PaR baseline. use_traj=True is the PaR+Trajectory variant: identical
    everything (model, PSM peer selection, validation), but the prompt also
    carries the student's full submission history (_build_prompt_traj)."""
    Validator.init_globals(tests, timeout)
    pdesc = _problem_text(pid)

    donors = {}
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
        buggy_vec = _pass_vector(buggy)
        cands = [(u, c, v) for u, (c, v) in donors.items() if u != uid]
        peer = _select_peer(buggy, buggy_vec, cands)
        patch = None
        if peer is not None:
            prompt = (_build_prompt_traj(pdesc, peer[1], was) if use_traj
                      else _build_prompt(pdesc, peer[1], buggy))
            for _ in range(SAMPLES):
                try:
                    out_text = _call_llm(prompt, 0.8 if SAMPLES > 1 else 0.2)
                except Exception:
                    continue
                cand = _extract_code(out_text)
                if cand and Validator.run(cand).passed():
                    patch = cand
                    break
        out[uid] = (patch, time.time() - t0)
    return out
