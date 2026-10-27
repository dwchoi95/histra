"""Run LSGen (Dai et al., AAAI'26) with GPT-4o on the benchmark via lsgen_bridge.py (setup: baselines/lsgen/setup.sh).
Usage: python src/experiments/run_lsgen.py prep | run [OUT.jsonl] [--batch [--submit]]
  prep     LSGen's retrieval database from CodeNet (CODENET=<Project_CodeNet dir>) and its embeddings
  run      LSGen_iter3 (OPENAI_API_KEY); --batch writes each LLM stage as an OpenAI Batch, which --submit sends"""
import functools
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from collections import defaultdict
from multiprocessing import Pool

from common import POOL, cases, passes, path, problem
from measure import measure

HERE = os.path.dirname(os.path.abspath(__file__))
LSG = os.path.join(HERE, "baselines", "lsgen", "upstream")
WORK, LPY, BRIDGE = os.path.join(LSG, "work"), os.path.join(LSG, ".venv", "bin", "python"), os.path.join(HERE, "lsgen_bridge.py")
FP = os.path.join(WORK, "dataset", "Filtered_pair")
DB = os.path.join(FP, "code1_Added_testScode_pairs", "Exec_test_processed_pair.json")
PQ = os.path.join(WORK, "dataset", "repairDataset", "Program_Question_Data", "English_Program_Question_StringVersion.json")
CODENET = os.environ.get("CODENET", "")       # Project CodeNet (metadata/ and data/), for prep only
ROUNDS = 4                                   # LSGen_base + 3 rounds of retrieval enhancement (NUM_REFINE=3)


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
    """The program as LSGen's get_pairs.py stores it: comments removed by its remove_comments.py, plus a newline."""
    return _remove_comments()(src) + "\n"


def _passes(args):
    t0 = time.time()
    return passes(*args), time.time() - t0


def get_pairs(pid):
    """LSGen's get_pairs.py for one problem, in its own cwd (it writes fixed temp files under ./ProcessData/...)."""
    out = os.path.join(FP, "ALL_pairs", f"{pid}_pair.json")
    if not os.path.exists(out):
        cwd = os.path.join(WORK, "getpairs", pid)
        os.makedirs(os.path.join(cwd, "ProcessData", "Get_Filtered_Data", "temp"), exist_ok=True)
        dump(os.path.join(cwd, "pids.json"), [pid])
        subprocess.run([LPY, "-m", "ProcessData.Get_Filtered_Data.get_pairs", "--csv_folder", f"{CODENET}/metadata",
                        "--data_folder", f"{CODENET}/data", "--json_file", "pids.json", "--output_file", out, "--language", "Python",
                        "--threshold", "0.5", "--lines_threshold", "20"],      # LSGen's get_pairs.sh values
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
    # LSGen's get_filtered_pairs.sh values
    subprocess.run([LPY, "-m", "ProcessData.Get_Filtered_Data.filter_submission_pairs", "--json_file", allp, "--output_file", proc,
                    "--mode", "test", "--threshold", "0.65", "--lines_threshold", "0", "--IS_SAVE"], cwd=LSG, check=True)
    kept = json.load(open(proc, encoding="utf-8"))
    # LSGen's EXEC_EVAL with our validator instead of go-judge: code2 must pass every test, code1 must fail
    tests = {p: problem(p)[:2] for p in pids}
    for key, want in (("code2", True), ("code1", False)):
        with Pool(min(POOL, 8)) as p:
            ok = p.map(_passes, [(r[key], *tests[r["problem_id"]]) for r in kept], chunksize=4)
        kept = [r for r, (o, _) in zip(kept, ok) if o == want]
    dump(DB, kept)
    n = defaultdict(int)
    for r in kept:
        n[r["problem_id"]] += 1
    print("DB pairs per problem:", dict(sorted(n.items())), "total", len(kept))
    subprocess.run([LPY, BRIDGE, "embed", os.path.join(WORK, "runs", "_embed"), "0", "-", "-"], check=True)


def bridge(run, stage, rnd, items, flags):
    """One LSGen stage over all items; a finished stage with the same input is reused."""
    inp, out = os.path.join(run, f"r{rnd}_{stage}.in.json"), os.path.join(run, f"r{rnd}_{stage}.json")
    if os.path.exists(out) and os.path.exists(inp) and json.load(open(inp, encoding="utf-8")) == items:
        return json.load(open(out, encoding="utf-8"))
    dump(inp, items)
    if os.path.exists(out):
        os.remove(out)
    while (rc := subprocess.run([LPY, BRIDGE, stage, run, str(rnd), inp, out] + flags).returncode) == 3:
        if "--submit" not in flags:
            sys.exit(f"round {rnd} {stage}: batch input written; rerun with --submit to send it")
        wait_batches(run)
    if rc:
        sys.exit(f"bridge {stage} failed ({rc})")
    return json.load(open(out, encoding="utf-8"))


def wait_batches(run):
    """Ingest finished OpenAI batches into the response cache, polling while one is still running."""
    while (rc := subprocess.run([LPY, BRIDGE, "batch-sync", run]).returncode) == 4:
        time.sleep(60)
    if rc:
        sys.exit(f"batch-sync failed ({rc})")


def main(out, flags):
    cs = cases()
    run = os.path.join(WORK, "runs", os.path.basename(out).removesuffix(".jsonl"))
    if "--submit" in flags:
        wait_batches(run)
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
            q = bridge(run, stage, rnd, q, flags)
            for it in q:
                secs[it["submission1_id"]] += it.pop("_sec", 0.0)
        keys = [hashlib.sha256((it["problem_id"] + "\0" + it["code_content"]).encode()).hexdigest() for it in q]
        new = [(k, it) for k, it in zip(keys, q) if k not in vcache]
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
    calls = defaultdict(dict)                  # reruns replay cached responses: keep the first record of each
    if os.path.exists(os.path.join(run, "calls.jsonl")):
        for line in open(os.path.join(run, "calls.jsonl"), encoding="utf-8"):
            r = json.loads(line)
            calls[r["sid"]].setdefault(r["key"], r)
    with open(out, "w") as f, open(os.path.join(run, "raw.jsonl"), "w") as g:
        for s, c in case.items():
            pt, rnd = patch.get(s, (None, None))
            f.write(json.dumps(dict(pid=c["pid"], user=c["user"], was=c["was"], oracle=c["oracle"], patch=pt,
                                    sec=secs[s], round=rnd)) + "\n")
            g.write(json.dumps(dict(pid=c["pid"], user=c["user"], rounds=hist[s], calls=list(calls[s].values()))) + "\n")
    measure(out)


if __name__ == "__main__":
    out = next((a for a in sys.argv[2:] if a.endswith(".jsonl")), path("lsgen"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if sys.argv[1] == "prep":
        prep()
    else:
        assert sys.argv[1] == "run", sys.argv[1]
        main(out, [a for a in sys.argv[2:] if a in ("--batch", "--submit")])
