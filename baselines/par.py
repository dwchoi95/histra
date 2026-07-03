"""PaR (Peer-aided Repairer) baseline approach, adapted to the HISTRA dataset.

Faithful re-implementation of PaR (Zhao et al., 2024): PSM peer selection
(0.25 * (test_pass_match + bm25_norm + ast_match + dataflow_match)) + the PaR
prompt + an LLM call, evaluated with our Validator. The paper's best model is
gpt-3.5-turbo, so this calls the OpenAI Chat Completions API (set OPENAI_API_KEY).

solve(pid, timeout, tests, trajs, refs) -> {user_id: (patch_or_None, seconds)}
"""
import os, re, time, json
from concurrent.futures import ThreadPoolExecutor, as_completed, CancelledError
from tqdm import tqdm
from src.core.validator import Validator
from src.types import Status
from src.utils import metrics as _metrics  # noqa: F401 (kept for parity)

MODEL = os.environ.get("PAR_MODEL", "gpt-3.5-turbo")
TOPK = int(os.environ.get("PAR_PSM_TOPK", "25"))   # BM25 prefilter before CodeBLEU
SAMPLES = int(os.environ.get("PAR_SAMPLES", "1"))   # LLM samples per buggy (pass@k)
TEMPERATURE = float(os.environ.get("PAR_TEMPERATURE", "0"))
SERVICE_TIER = os.environ.get("PAR_SERVICE_TIER", "").strip()
LLM_RETRIES = int(os.environ.get("PAR_LLM_RETRIES", "5"))
RETRY_SLEEP = float(os.environ.get("PAR_RETRY_SLEEP", "2.0"))
LLM_CONCURRENCY = int(os.environ.get("PAR_CONCURRENCY", "16"))
PREP_CONCURRENCY = int(os.environ.get("PAR_PREP_CONCURRENCY", "1"))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TOK = re.compile(r"[A-Za-z_]\w*|\d+|\S")
_CODEBLOCK = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)
_FATAL_LLM_ERROR_CODES = {
    "insufficient_quota",
    "invalid_api_key",
    "model_not_found",
    "model_not_available",
}


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


def _call_llm(prompt, temperature, max_tokens=None):
    _load_env()
    from openai import OpenAI
    base = os.environ.get("LLM_BASE_URL")  # e.g. http://localhost:11434/v1 for Ollama
    client = OpenAI(base_url=base, api_key="ollama") if base else OpenAI()
    kwargs = {}
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    if SERVICE_TIER:
        kwargs["service_tier"] = SERVICE_TIER
    resp = client.chat.completions.create(
        model=MODEL, temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
        **kwargs)
    return resp.choices[0].message.content


def _call_llm_with_retries(label, pid, prompt):
    started = time.time()
    last_error = None
    for attempt in range(LLM_RETRIES + 1):
        try:
            return _call_llm(prompt, TEMPERATURE), None, time.time() - started
        except Exception as exc:
            last_error = _format_llm_error(exc)
            if _is_fatal_llm_error(exc):
                raise RuntimeError(
                    f"{label} {pid}: fatal LLM API error. {last_error}"
                ) from exc
            if attempt >= LLM_RETRIES or not _is_retryable_llm_error(exc):
                return None, last_error, time.time() - started
            time.sleep(RETRY_SLEEP * (attempt + 1))


def _worker_count(task_count):
    if task_count <= 0:
        return 1
    if LLM_CONCURRENCY <= 0:
        return task_count
    return max(1, min(LLM_CONCURRENCY, task_count))


def _prep_worker_count(task_count):
    if task_count <= 0:
        return 1
    if PREP_CONCURRENCY <= 0:
        return task_count
    return max(1, min(PREP_CONCURRENCY, task_count))


def _build_donors(refs, label, pid):
    items = list(refs.items())
    donors = {}

    def prepare(item):
        uid, ac = item
        return uid, ac, _pass_vector(ac)

    if _prep_worker_count(len(items)) <= 1:
        iterator = tqdm(
            items,
            total=len(items),
            desc=f"{label} {pid} donors",
            leave=False,
            dynamic_ncols=True,
        )
        for item in iterator:
            uid, ac, vec = prepare(item)
            if vec and all(vec):
                donors[uid] = (ac, vec)
        return donors

    with ThreadPoolExecutor(max_workers=_prep_worker_count(len(items))) as executor:
        futures = [executor.submit(prepare, item) for item in items]
        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc=f"{label} {pid} donors",
            leave=False,
            dynamic_ncols=True,
        ):
            uid, ac, vec = future.result()
            if vec and all(vec):
                donors[uid] = (ac, vec)
    return donors


def _build_prompt_jobs(pid, label, pdesc, donors, trajs, use_traj):
    jobs = []
    out = {}
    items = list(trajs.items())

    def prepare(item):
        uid, was = item
        was = was or []
        t0 = time.time()
        if not was:
            return uid, None, (None, 0.0)
        buggy = was[-1]
        buggy_vec = _pass_vector(buggy)
        cands = [(u, c, v) for u, (c, v) in donors.items() if u != uid]
        peer = _select_peer(buggy, buggy_vec, cands)
        if peer is None:
            return uid, None, (None, time.time() - t0)
        prompt = (_build_prompt_traj(pdesc, peer[1], was) if use_traj
                  else _build_prompt(pdesc, peer[1], buggy))
        return uid, {
            "uid": uid,
            "prompt": prompt,
            "prep_elapsed": time.time() - t0,
        }, None

    if _prep_worker_count(len(items)) <= 1:
        iterator = tqdm(
            items,
            total=len(items),
            desc=f"{label} {pid} prompts",
            leave=False,
            dynamic_ncols=True,
        )
        for item in iterator:
            uid, job, result = prepare(item)
            if job is not None:
                jobs.append(job)
            else:
                out[uid] = result
        return jobs, out

    with ThreadPoolExecutor(max_workers=_prep_worker_count(len(items))) as executor:
        futures = [executor.submit(prepare, item) for item in items]
        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc=f"{label} {pid} prompts",
            leave=False,
            dynamic_ncols=True,
        ):
            uid, job, result = future.result()
            if job is not None:
                jobs.append(job)
            else:
                out[uid] = result
    return jobs, out


def _extract_code(text):
    m = _CODEBLOCK.findall(text or "")
    return (max(m, key=len).strip() if m else (text or "").strip())


def _format_llm_error(exc):
    status = getattr(exc, "status_code", None)
    code = getattr(exc, "code", None)
    parts = [type(exc).__name__]
    if status is not None:
        parts.append(f"status={status}")
    if code:
        parts.append(f"code={code}")
    return f"{' '.join(parts)}: {exc}"


def _is_fatal_llm_error(exc):
    status = getattr(exc, "status_code", None)
    code = getattr(exc, "code", None)
    return status in {401, 403, 404} or code in _FATAL_LLM_ERROR_CODES


def _is_retryable_llm_error(exc):
    status = getattr(exc, "status_code", None)
    return status in {408, 409, 429, 500, 502, 503, 504}


def check_api_ready(label="PaR"):
    """Fail before sending dataset/code prompts when the LLM endpoint is unusable."""
    if os.environ.get("PAR_SKIP_PREFLIGHT") == "1":
        return
    try:
        _call_llm("Return OK.", temperature=0)
    except Exception as exc:
        raise RuntimeError(
            f"{label} API preflight failed before running the dataset. "
            f"{_format_llm_error(exc)}"
        ) from exc


def solve(pid, timeout, tests, trajs, refs, use_traj=False):
    """PaR baseline. use_traj=True is the PaR+Trajectory variant: identical
    everything (model, PSM peer selection, validation), but the prompt also
    carries the student's full submission history (_build_prompt_traj)."""
    Validator.init_globals(tests, timeout)
    pdesc = _problem_text(pid)
    label = "PaRTraj" if use_traj else "PaR"
    llm_attempts = 0
    llm_successes = 0
    last_llm_error = None

    donors = _build_donors(refs, label, pid)
    jobs, out = _build_prompt_jobs(pid, label, pdesc, donors, trajs, use_traj)

    if jobs:
        futures = {}
        futures_by_uid = {}
        done_counts = {job["uid"]: 0 for job in jobs}
        submitted = max(1, SAMPLES)
        max_workers = _worker_count(len(jobs) * submitted)
        executor = ThreadPoolExecutor(max_workers=max_workers)
        try:
            for job in jobs:
                uid = job["uid"]
                futures_by_uid[uid] = []
                for _ in range(submitted):
                    future = executor.submit(
                        _call_llm_with_retries, label, pid, job["prompt"]
                    )
                    futures[future] = job
                    futures_by_uid[uid].append(future)
            llm_attempts += len(futures)
            elapsed_by_uid = {job["uid"]: job["prep_elapsed"] for job in jobs}

            for future in tqdm(
                as_completed(futures),
                total=len(futures),
                desc=f"{label} {pid} LLM",
                leave=False,
                dynamic_ncols=True,
            ):
                job = futures[future]
                uid = job["uid"]
                if uid in out:
                    continue
                try:
                    out_text, err, call_elapsed = future.result()
                except CancelledError:
                    continue
                if err:
                    last_llm_error = err
                done_counts[uid] += 1
                elapsed_by_uid[uid] = max(
                    elapsed_by_uid.get(uid, job["prep_elapsed"]),
                    job["prep_elapsed"] + call_elapsed,
                )
                if out_text is None:
                    if done_counts[uid] >= submitted:
                        out[uid] = (None, elapsed_by_uid[uid])
                    continue

                llm_successes += 1
                cand = _extract_code(out_text)
                validation_started = time.time()
                passed = cand and Validator.run_failfast(cand).passed()
                elapsed = job["prep_elapsed"] + call_elapsed + (
                    time.time() - validation_started
                )
                elapsed_by_uid[uid] = max(elapsed_by_uid[uid], elapsed)
                if passed:
                    out[uid] = (cand, elapsed)
                    for other in futures_by_uid.get(uid, []):
                        if other is not future:
                            other.cancel()
                elif done_counts[uid] >= submitted:
                    out[uid] = (None, elapsed_by_uid[uid])
        except Exception:
            executor.shutdown(wait=False, cancel_futures=True)
            raise
        finally:
            executor.shutdown(wait=True, cancel_futures=True)

    for job in jobs:
        out.setdefault(job["uid"], (None, job["prep_elapsed"]))
    if llm_attempts and llm_successes == 0:
        raise RuntimeError(
            f"{label} {pid}: all {llm_attempts} LLM calls failed; "
            f"refusing to write an all-zero result. Last error: {last_llm_error}"
        )
    return out
