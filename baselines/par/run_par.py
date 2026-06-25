"""PaR (Peer-aided Repairer) baseline, adapted to the Histra dataset.

Faithful re-implementation of PaR (Zhao et al., "Peer-aided Repairer", 2024) for
our stdin/stdout Python competitive-programming dataset. The upstream release
(github.com/whisperzqh/Peer-aided-Repairer) ships C-only code, an OpenAI/HF
backend, and an example-level PSM script, so we re-implement PaR's METHOD here:

  1. PSM peer selection: psm = 0.25 * (test_pass_match + bm25_norm
       + ast_match + dataflow_match), coefficients 0.25 each (per the paper).
       - test_pass_match: 2*|both pass| / (|buggy pass| + |peer pass|)
       - bm25_norm:       min-max normalized BM25 of buggy(query) vs candidates
       - ast_match:       CodeBLEU syntax_match_score(buggy, peer)
       - dataflow_match:  CodeBLEU dataflow_match_score(buggy, peer)
  2. Prompt: PaR's template (task desc + problem statement + reference/peer code
       + buggy code), with "C" swapped for "Python".
  3. LLM call: local Ollama via its OpenAI-compatible endpoint.
  4. Evaluate: our Validator (all held-out tests must pass).

Deviations from upstream (documented for the paper):
  - Language C -> Python; backend OpenAI/HF -> local Ollama.
  - Candidates are prefiltered to the BM25 top-K before the (expensive) CodeBLEU
    terms are computed, for tractability over ~100 donors/problem.
  - peer/donor pool = other students' ACs (the student's own AC is excluded).

Metrics (RR/TED/IP/ATT) reuse src.utils.metrics so they match the Histra runner.
"""
import os, sys, re, csv, json, time, argparse, urllib.request, urllib.error
from statistics import mean

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

import warnings
warnings.filterwarnings("ignore")

from src.utils import DataLoader
from src.core.validator import Validator
from src.types import Status
from src.utils import metrics as _metrics

from rank_bm25 import BM25Okapi
from codebleu import calc_codebleu

OLLAMA = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")


# ---------------------------------------------------------------- problem text
def problem_text(pid: str) -> str:
    path = os.path.join(ROOT, "data", pid, "problem.html")
    if not os.path.exists(path):
        return ""
    html = open(path, encoding="utf-8").read()
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ------------------------------------------------------------------- tokenize
_TOK = re.compile(r"[A-Za-z_]\w*|\d+|\S")
def tokenize(code: str):
    return _TOK.findall(code or "")


# --------------------------------------------------------------- test vectors
def pass_vector(code: str):
    """Per-test pass booleans for `code` (Validator must be init'd for the pid)."""
    try:
        results = Validator.run(code)
    except Exception:
        return None
    return [tr.result is not None and tr.result.status == Status.PASSED
            for tr in results.ts]


# --------------------------------------------------------------- PSM scoring
def codebleu_terms(buggy: str, peer: str):
    """(ast_match, dataflow_match) from CodeBLEU; robust to parse failures."""
    try:
        r = calc_codebleu([peer], [buggy], lang="python",
                          weights=(0.25, 0.25, 0.25, 0.25))
        return r.get("syntax_match_score", 0.0), r.get("dataflow_match_score", 0.0)
    except Exception:
        return 0.0, 0.0


def select_peer(buggy, buggy_vec, candidates, topk):
    """candidates: list[(uid, code, vec)]. Returns (uid, code) maximizing PSM."""
    if not candidates:
        return None
    # BM25 over all candidates (cheap); query = buggy
    corpus = [tokenize(c) for _, c, _ in candidates]
    bm25 = BM25Okapi(corpus)
    bm_scores = bm25.get_scores(tokenize(buggy))
    lo, hi = min(bm_scores), max(bm_scores)
    span = (hi - lo) or 1.0
    bm_norm = [(s - lo) / span for s in bm_scores]

    # prefilter to BM25 top-K before the expensive CodeBLEU terms
    order = sorted(range(len(candidates)), key=lambda i: bm_scores[i], reverse=True)
    keep = order[:topk]

    bpass = sum(1 for v in buggy_vec for v in [v] if v) if buggy_vec else 0
    best, best_psm = None, -1.0
    for i in keep:
        uid, code, vec = candidates[i]
        # test-pass match
        if buggy_vec and vec:
            same = sum(1 for a, b in zip(buggy_vec, vec) if a and b)
            ppass = sum(1 for b in vec if b)
            denom = (bpass + ppass) or 1
            tmatch = (2 * same) / denom
        else:
            tmatch = 0.0
        ast_m, df_m = codebleu_terms(buggy, code)
        psm = 0.25 * (tmatch + bm_norm[i] + ast_m + df_m)
        if psm > best_psm:
            best_psm, best = psm, (uid, code)
    return best


# ------------------------------------------------------------------- prompt
def build_prompt(pdesc, peer_code, buggy_code):
    task = ("There is a Python programming problem. Below is the problem "
            "description, the input/output format and examples, a copy of a "
            "correct reference solution by a peer student, and a copy of a buggy "
            "program containing semantic errors written by a student. The program "
            "reads from standard input and writes to standard output. Please fix "
            "the buggy code and return the corrected program.\n\n")
    desc = "[Problem]\n" + pdesc + "\n[End of Problem]\n\n"
    peer = "[Reference Code]\n" + peer_code + "\n[End of Reference Code]\n\n"
    buggy = "[Buggy Code]\n" + buggy_code + "\n[End of Buggy Code]\n\n"
    tail = ("Return ONLY the corrected Python program inside a single ```python "
            "code block, with no explanation.")
    return task + desc + peer + buggy + tail


# ------------------------------------------------------------------- LLM call
def call_llm(prompt, model, temperature, timeout=180):
    url = OLLAMA.rstrip("/") + "/v1/chat/completions"
    payload = {"model": model,
               "messages": [{"role": "user", "content": prompt}],
               "temperature": temperature}
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode())
    return data["choices"][0]["message"]["content"]


_CODEBLOCK = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)
def extract_code(text):
    m = _CODEBLOCK.findall(text or "")
    if m:
        return max(m, key=len).strip()
    return (text or "").strip()


# --------------------------------------------------------------------- driver
def run_problem(pid, timeout, tests, trajs, refs, model, samples, topk, out_root):
    out_dir = os.path.join(out_root, pid)
    os.makedirs(out_dir, exist_ok=True)
    per_csv = os.path.join(out_dir, "results.csv")

    Validator.init_globals(tests, timeout)
    pdesc = problem_text(pid)

    # donor pool: every student's AC + its per-test vector (all True if it passes)
    donors = {}
    for uid, ac in refs.items():
        vec = pass_vector(ac)
        if vec and all(vec):
            donors[uid] = (ac, vec)

    rows = [("user_id", "pass", "ted", "ip", "att_seconds", "buggy", "fixed", "oracle")]
    pass_cnt = 0
    ted_vals, ip_vals = [], []
    t0 = time.time()  # wall-clock: LLM compute is offloaded to the Ollama server

    users = list(trajs.keys())
    for uid in users:
        was = trajs.get(uid) or []
        if not was:
            continue
        buggy = was[-1]
        oracle = refs.get(uid)
        buggy_vec = pass_vector(buggy)

        cands = [(u, c, v) for u, (c, v) in donors.items() if u != uid]
        peer = select_peer(buggy, buggy_vec, cands, topk)
        patch = None
        if peer is not None:
            prompt = build_prompt(pdesc, peer[1], buggy)
            for _ in range(samples):
                try:
                    out = call_llm(prompt, model, 0.8 if samples > 1 else 0.2)
                except Exception:
                    continue
                cand = extract_code(out)
                if not cand:
                    continue
                try:
                    if Validator.run(cand).passed():
                        patch = cand
                        break
                except Exception:
                    continue

        passed = patch is not None
        ted = _metrics.ted(buggy, patch) if passed else None
        ip = (_metrics.intent_preservation(buggy, patch, oracle)
              if passed and oracle else None)
        if passed:
            pass_cnt += 1
            if ted is not None: ted_vals.append(ted)
            if ip is not None: ip_vals.append(ip)
        rows.append((uid, int(passed),
                     ted if ted is not None else "",
                     ip if ip is not None else "",
                     "", buggy, patch or "", oracle or ""))
        print(f"[{pid}] {uid} pass={int(passed)} "
              f"({pass_cnt}/{len(rows)-1})", flush=True)

    total_sec = time.time() - t0
    n_users = max(len(trajs), 1)
    att = total_sec / n_users
    rows = [rows[0]] + [(u, p, t, i, f"{att:.6f}", b, f, o)
                        for (u, p, t, i, _a, b, f, o) in rows[1:]]
    with open(per_csv, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

    rr = pass_cnt / n_users
    return {"pid": pid, "rr": rr, "pass": pass_cnt, "n_users": n_users,
            "ted_mean": mean(ted_vals) if ted_vals else 0.0,
            "ip_mean": mean(ip_vals) if ip_vals else 0.0,
            "att_mean": att, "total_seconds": total_sec}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--dataset", default=os.path.join(ROOT, "data"))
    ap.add_argument("-p", "--problems", nargs="+", default=None)
    ap.add_argument("-m", "--model", default="qwen2.5-coder:14b")
    ap.add_argument("-k", "--samples", type=int, default=1,
                    help="LLM samples per buggy (pass@k); 1 = single-shot")
    ap.add_argument("--topk", type=int, default=25,
                    help="BM25 prefilter size before CodeBLEU PSM terms")
    ap.add_argument("--limit", type=int, default=None,
                    help="cap users per problem (debug)")
    ap.add_argument("-n", "--sample", type=int, default=None,
                    help="deterministic buggy sample per problem (sorted uids), "
                         "matching the Refactory adapter's --sample")
    ap.add_argument("-o", "--out", default=os.path.join(HERE, "results_par"))
    ap.add_argument("-r", "--reset", action="store_true")
    args = ap.parse_args()

    problems = DataLoader.run(args.dataset)
    if args.problems:
        problems = [p for p in problems if p[0] in args.problems]
    os.makedirs(args.out, exist_ok=True)
    overall_path = os.path.join(args.out, "overall.csv")

    summaries = []
    for pid, timeout, tests, trajs, refs in problems:
        per_csv = os.path.join(args.out, pid, "results.csv")
        if (not args.reset) and os.path.exists(per_csv):
            print(f"[{pid}] skip (exists)")
            continue
        if args.sample:
            trajs = {u: trajs[u] for u in sorted(trajs)[:args.sample]}
        elif args.limit:
            trajs = {u: trajs[u] for u in list(trajs)[:args.limit]}
        s = run_problem(pid, timeout, tests, trajs, refs, args.model,
                        args.samples, args.topk, args.out)
        summaries.append(s)
        print(f"[{pid}] RR={s['rr']:.3f} pass={s['pass']}/{s['n_users']} "
              f"ted={s['ted_mean']:.2f} ip={s['ip_mean']:+.2f} "
              f"t={s['total_seconds']:.1f}s", flush=True)

    if summaries:
        header = ["pid", "rr", "pass", "n_users", "ted_mean", "ip_mean",
                  "att_mean", "total_seconds"]
        exists = os.path.exists(overall_path)
        with open(overall_path, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if not exists:
                w.writerow(header)
            for s in summaries:
                w.writerow([s["pid"], f"{s['rr']:.6f}", s["pass"], s["n_users"],
                            f"{s['ted_mean']:.6f}", f"{s['ip_mean']:.6f}",
                            f"{s['att_mean']:.6f}", f"{s['total_seconds']:.6f}"])


if __name__ == "__main__":
    main()
