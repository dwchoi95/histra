"""Run LSGen (Dai et al., "Learner-Tailored Program Repair", AAAI 2026; github.com/PandaAB/LSGen) on the baselines.py
sample and store its patches. LSGen's own code runs in its venv (baselines/lsgen/.venv) through lsgen_bridge.py.
Usage:
  python run_lsgen.py prep                     # once: LSGen's retrieval DB from CodeNet (get_pairs.py, filter_submission_pairs.py,
                                               #   execution filter with V.verify) + Qwen3-Embedding vectors
  [PER=0] [ONLY=pid,..] [POOL=n] python run_lsgen.py {gpt4o|qwen|vllm} OUT.jsonl [--batch [--submit]]
     qwen: Qwen2.5-Coder-7B-Instruct fp16 via local Ollama; vllm: the same model in BF16 behind `vllm serve` on a CUDA
     server (LSGEN_VLLM_URL), with Qwen3-Embedding-0.6B run by vLLM as LSGen does
LSGen_iter3: round 0 = edit-driven retrieval (top-5) -> one bug description per retrieved pair -> solution-guided repair
(LSGen_base); rounds 1-3 = iterative retrieval enhancement with the failed repair, for the programs still failing.
Each repair is validated with V.verify. OUT gets dict(pid, user, was, oracle, patch, sec, round); OUT.raw.jsonl gets per
program LSGen's retrieved pairs, descriptions, raw repair responses, and every LLM call with its tokens.
--batch (gpt4o): every LLM stage of all programs becomes one OpenAI Batch; --submit submits it, polls until it finishes,
and goes on with the next stage (without --submit the batch input is only written); a stage is split into batches of at
most LSGEN_BATCH_TOKENS input tokens (default 1.3M, the account's batch queue limit), one in flight at a time. Stage outputs and responses are
cached under baselines/lsgen/work/runs/<OUT name>, so a rerun resumes. LSGEN_BUDGET=<usd> stops live GPT-4o calls once
their standard-price cost reaches it.
  [POOL=n] python run_lsgen.py revalidate OUT.jsonl   # re-run V.verify on every final patch here (e.g. results produced on
     another machine): rows get server_pass, mac_pass, server_patch; patch keeps only the patches that pass here
  [PER=0] [POOL=n] python run_lsgen.py recheck OUT.jsonl  # unrepaired rows: re-run V.verify on each round's repair (from
     OUT.raw.jsonl) on an idle machine; the first that passes becomes the patch, as LSGen would have stopped there
     (validation under load can time out on heavy tests); flipped rows get recheck=True"""
import functools, hashlib, importlib.util, json, os, subprocess, sys, time
from collections import defaultdict
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(__file__))
from baselines import cases, V, POOL, DATA

HERE = os.path.dirname(os.path.abspath(__file__))
LSG = os.path.abspath(os.path.join(HERE, "..", "..", "..", "baselines", "lsgen"))
WORK, LPY, BRIDGE = os.path.join(LSG, "work"), os.path.join(LSG, ".venv", "bin", "python"), os.path.join(HERE, "lsgen_bridge.py")
FP = os.path.join(WORK, "dataset", "Filtered_pair")
DB = os.path.join(FP, "code1_Added_testScode_pairs", "Exec_test_processed_pair.json")
PQ = os.path.join(WORK, "dataset", "repairDataset", "Program_Question_Data", "English_Program_Question_StringVersion.json")
CODENET = "/Users/cdw/VSCode/aria/data/Project_CodeNet"
ROUNDS = 4                                   # LSGen_base + 3 iterations of iterative retrieval enhancement (NUM_REFINE=3)


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)


@functools.cache
def _remove_comments():
    spec = importlib.util.spec_from_file_location("lsgen_remove_comments", os.path.join(LSG, "utils", "remove_comments.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.remove_comments


def lsgen_code(src):
    """The student's program as LSGen's data processing stores it (get_pairs.py -> save_temp_file): comments removed
    with LSGen's utils/remove_comments.py, plus the newline save_temp_file appends."""
    return _remove_comments()(src) + "\n"


def problem_tests(pid):
    d = os.path.join(DATA, pid)
    meta = json.load(open(os.path.join(d, "meta.json"))) if os.path.exists(os.path.join(d, "meta.json")) else {}
    return [json.loads(l) for l in open(os.path.join(d, "tests.jsonl"), encoding="utf-8")], \
        min(meta.get("time_limit_ms", 2000) / 1000.0, 4.0)          # same timeout as baselines.cases()


def _passes(args):
    t0 = time.time()
    return V.verify(*args).passed, time.time() - t0


def get_pairs(pid):
    """LSGen's get_pairs.py for one problem, in its own cwd (it writes fixed temp files under ./ProcessData/...)."""
    out = os.path.join(FP, "ALL_pairs", f"{pid}_pair.json")
    if not os.path.exists(out):
        cwd = os.path.join(WORK, "getpairs", pid)
        os.makedirs(os.path.join(cwd, "ProcessData", "Get_Filtered_Data", "temp"), exist_ok=True)
        dump(os.path.join(cwd, "pids.json"), [pid])
        subprocess.run([LPY, "-m", "ProcessData.Get_Filtered_Data.get_pairs", "--csv_folder", f"{CODENET}/metadata",
                        "--data_folder", f"{CODENET}/data", "--json_file", "pids.json", "--output_file", out, "--language", "Python",
                        "--threshold", "0.5", "--lines_threshold", "20"],      # scripts/pipline/init_data/get_pairs.sh values
                       cwd=cwd, env={**os.environ, "PYTHONPATH": LSG}, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return json.load(open(out, encoding="utf-8"))


def prep():
    cs = cases()
    dump(PQ, [{"Pid": p, "ProblemText": t} for p, t in sorted({c["pid"]: c["problem"] for c in cs}.items())])
    pids = sorted({c["pid"] for c in cs})
    with Pool(4) as p:
        pairs = [x for ps in p.map(get_pairs, pids) for x in ps]
    allp, proc = os.path.join(FP, "ALL_pairs", "test_pair.json"), os.path.join(FP, "Processed_pair", "test_processed_pair.json")
    dump(allp, pairs)
    os.makedirs(os.path.dirname(proc), exist_ok=True)
    # scripts/pipline/init_data/get_filtered_pairs.sh: MODE=test THRESHOLD=0.65 LINES_THRESHOLD=0
    subprocess.run([LPY, "-m", "ProcessData.Get_Filtered_Data.filter_submission_pairs", "--json_file", allp, "--output_file", proc,
                    "--mode", "test", "--threshold", "0.65", "--lines_threshold", "0", "--IS_SAVE"], cwd=LSG, check=True)
    kept = json.load(open(proc, encoding="utf-8"))
    # EXEC_EVAL (go-judge in LSGen, V.verify on our tests here): keep pairs whose code2 passes every test, then whose code1 fails
    tests = {p: problem_tests(p) for p in pids}
    for key, want in (("code2", True), ("code1", False)):
        with Pool(min(POOL, 8)) as p:
            ok = p.map(_passes, [(r[key], *tests[r["problem_id"]]) for r in kept], chunksize=4)
        kept = [r for r, (o, _) in zip(kept, ok) if o == want]
    dump(DB, kept)
    n = defaultdict(int)
    for r in kept:
        n[r["problem_id"]] += 1
    print("DB pairs per problem:", dict(sorted(n.items())), "total", len(kept))
    subprocess.run([LPY, BRIDGE, "embed", os.path.join(WORK, "runs", "_embed"), "-", "0", "-", "-"], check=True)


def bridge(run, backend, stage, rnd, items, flags):
    """One LSGen stage over all items; a finished stage with the same input is reused (batch resumes replay nothing)."""
    inp, out = os.path.join(run, f"r{rnd}_{stage}.in.json"), os.path.join(run, f"r{rnd}_{stage}.json")
    if os.path.exists(out) and os.path.exists(inp) and json.load(open(inp, encoding="utf-8")) == items:
        return json.load(open(out, encoding="utf-8"))
    dump(inp, items)
    if os.path.exists(out):
        os.remove(out)
    while (rc := subprocess.run([LPY, BRIDGE, stage, run, backend, str(rnd), inp, out] + flags).returncode) == 3:
        if "--submit" not in flags:
            sys.exit(f"round {rnd} {stage}: batch input written; rerun with --submit to send it")
        wait_batches(run, backend)
    if rc == 6:
        sys.exit(f"round {rnd} {stage}: stopped at the spending cap (LSGEN_BATCH_CAP); see {run}/batches/state.json")
    if rc:
        sys.exit(f"bridge {stage} failed ({rc})")
    return json.load(open(out, encoding="utf-8"))


def wait_idle():
    """LSGEN_IDLE=1: validate only while the 1-minute load average is below LSGEN_MAX_LOAD (default 10), so that the
    test runs share the machine with other jobs without timeouts flipping verdicts."""
    while os.environ.get("LSGEN_IDLE") and os.getloadavg()[0] >= float(os.environ.get("LSGEN_MAX_LOAD", 10)):
        print(f"{time.strftime('%H:%M')} waiting to validate: load {os.getloadavg()[0]:.1f}", flush=True)
        time.sleep(300)


def wait_batches(run, backend):
    """Ingest finished OpenAI batches into the response cache, polling while one is still running."""
    while (rc := subprocess.run([LPY, BRIDGE, "batch-sync", run, backend]).returncode) == 4:
        time.sleep(60)
    if rc:
        sys.exit(f"batch-sync failed ({rc})")


def main(backend, out, flags):
    cs = cases()
    run = os.path.join(WORK, "runs", os.path.basename(out).removesuffix(".jsonl"))
    if "--submit" in flags:
        wait_batches(run, backend)
    sid = lambda c: f"q_{c['pid']}_{c['user']}"
    item = {sid(c): dict(submission1_id=sid(c), problem_id=c["pid"], user_id=c["user"], code1=code1,
                         code1_lines=len(code1.splitlines())) for c in cs for code1 in [lsgen_code(c["was"][-1])]}
    case = {sid(c): c for c in cs}
    patch, last, secs, hist = {}, {}, defaultdict(float), defaultdict(list)
    vcache_path = os.path.join(run, "verify.json")
    vcache = json.load(open(vcache_path)) if os.path.exists(vcache_path) else {}
    for rnd in range(ROUNDS):
        todo = [s for s in item if s not in patch]
        if not todo:
            break
        q = [dict(item[s], code_content=last[s]) if rnd else item[s] for s in todo]
        for stage in ("retrieve", "desc", "repair"):
            q = bridge(run, backend, stage, rnd, q, flags)
            for it in q:
                secs[it["submission1_id"]] += it.pop("_sec", 0.0)
        keys = [hashlib.sha256((it["problem_id"] + "\0" + it["code_content"]).encode()).hexdigest() for it in q]
        new = [(k, it) for k, it in zip(keys, q) if k not in vcache]
        if new:
            wait_idle()
        with Pool(POOL) as p:
            res = p.map(_passes, [(it["code_content"], case[it["submission1_id"]]["tests"], case[it["submission1_id"]]["timeout"])
                                  for _, it in new], chunksize=1)
        for (k, it), (ok, sec) in zip(new, res):
            vcache[k] = ok
            secs[it["submission1_id"]] += sec
        dump(vcache_path, vcache)
        for k, it in zip(keys, q):
            s = it["submission1_id"]
            hist[s].append(dict(round=rnd, passed=vcache[k], code_content=it["code_content"],
                                top_k=[(r["RetrievalSubmission1_id"], r["MATCH_SCORE"]) for r in it.get("top_k_results", [])],
                                ref_descs=it.get("retrieval_code_bug_desc"), response=it.get("ori_content"),
                                gen_bug_descriptions=it.get("gen_code1_bug_descriptions")))
            if vcache[k]:
                patch[s] = (it["code_content"], rnd)
            last[s] = it["code_content"]
        print(f"round {rnd}: {sum(vcache[k] for k in keys)}/{len(q)} repaired, total {len(patch)}/{len(item)}", flush=True)
    calls = defaultdict(dict)                  # one record per response (reruns replay cached ones; keep the first)
    if os.path.exists(os.path.join(run, "calls.jsonl")):
        for line in open(os.path.join(run, "calls.jsonl"), encoding="utf-8"):
            r = json.loads(line)
            calls[r["sid"]].setdefault(r["key"], r)
    with open(out, "w") as f, open(out.removesuffix(".jsonl") + ".raw.jsonl", "w") as g:
        for s, c in case.items():
            pt, rnd = patch.get(s, (None, None))
            f.write(json.dumps(dict(pid=c["pid"], user=c["user"], was=c["was"], oracle=c["oracle"], patch=pt,
                                    sec=secs[s], round=rnd)) + "\n")
            g.write(json.dumps(dict(pid=c["pid"], user=c["user"], rounds=hist[s], calls=list(calls[s].values()))) + "\n")
    print(backend, f"passed {len(patch)}/{len(item)}")


def revalidate(out):
    rows = [json.loads(l) for l in open(out, encoding="utf-8")]
    case = {(c["pid"], c["user"]): c for c in cases()}
    for r in rows:
        r.setdefault("server_patch", r["patch"])
        r["server_pass"] = r["server_patch"] is not None
    todo = [r for r in rows if r["server_pass"]]
    wait_idle()
    with Pool(POOL) as p:
        res = p.map(_passes, [(r["server_patch"], case[r["pid"], r["user"]]["tests"], case[r["pid"], r["user"]]["timeout"])
                              for r in todo], chunksize=1)
    for r, (ok, _) in zip(todo, res):
        r["mac_pass"] = ok
    for r in rows:
        r.setdefault("mac_pass", None)
        r["patch"] = r["server_patch"] if r["mac_pass"] else None
    with open(out, "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)
    print(f"server {len(todo)}/{len(rows)}, here {sum(bool(r['mac_pass']) for r in rows)}/{len(rows)}; "
          f"lost here: {[(r['pid'], r['user']) for r in todo if not r['mac_pass']]}")


def recheck(out):
    rows = [json.loads(l) for l in open(out, encoding="utf-8")]
    raw = {(r["pid"], r["user"]): r["rounds"] for r in map(json.loads, open(out.removesuffix(".jsonl") + ".raw.jsonl", encoding="utf-8"))}
    case = {(c["pid"], c["user"]): c for c in cases()}
    jobs = [(r, rd) for r in rows if r["patch"] is None and (r["pid"], r["user"]) in case    # ONLY restricts the problems
            for rd in raw[r["pid"], r["user"]] if rd.get("code_content")]
    wait_idle()
    with Pool(POOL) as p:
        res = p.map(_passes, [(rd["code_content"], case[r["pid"], r["user"]]["tests"], case[r["pid"], r["user"]]["timeout"])
                              for r, rd in jobs], chunksize=1)
    for (r, rd), (ok, _) in zip(jobs, res):     # jobs are in round order per row: the first passing round wins
        if ok and r["patch"] is None:
            r["patch"], r["round"], r["recheck"] = rd["code_content"], rd["round"], True
    with open(out, "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)
    print(f"rechecked {len(jobs)} repairs of {len({(r['pid'], r['user']) for r, _ in jobs})} unrepaired rows; now passing "
          f"{sum(r['patch'] is not None for r in rows)}/{len(rows)}; flipped: {[(r['pid'], r['user'], r['round']) for r in rows if r.get('recheck')]}")


if __name__ == "__main__":
    if sys.argv[1] == "prep":
        prep()
    elif sys.argv[1] == "revalidate":
        revalidate(sys.argv[2])
    elif sys.argv[1] == "recheck":
        recheck(sys.argv[2])
    else:
        assert sys.argv[1] in ("gpt4o", "qwen", "vllm"), sys.argv[1]
        main(sys.argv[1], sys.argv[2], [a for a in sys.argv[3:] if a in ("--batch", "--submit")])
