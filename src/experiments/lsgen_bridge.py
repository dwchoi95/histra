"""LSGen side of run_lsgen.py: runs LSGen's own code (github.com/PandaAB/LSGen) in its venv, cwd = upstream/work.
Usage: lsgen_bridge.py STAGE RUN_DIR ROUND IN.json OUT.json [--batch] [--submit]; STAGE: embed, retrieve, desc, repair,
or batch-sync. LLM responses are cached in RUN_DIR; --batch writes the uncached ones as an OpenAI Batch (exit 3)."""
import ast, hashlib, json, os, sys, threading, time, types
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import requests

LSG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "baselines", "lsgen", "upstream")
WORK = os.path.join(LSG, "work")
DB = "dataset/Filtered_pair/code1_Added_testScode_pairs/Exec_test_processed_pair.json"   # relative to WORK
PQ = "dataset/repairDataset/Program_Question_Data/English_Program_Question_StringVersion.json"
EMB = "Qwen/Qwen3-Embedding-0.6B"            # LSGen paper's model (VectorRetrieval_vllm.py hard-codes the 8B one)
MODEL = os.environ.get("LSGEN_GPT_MODEL", "gpt-4o-2024-08-06")
OPENAI = os.environ.get("LSGEN_OPENAI_BASE", "https://api.openai.com/v1")
BATCH_TOKENS = int(os.environ.get("LSGEN_BATCH_TOKENS", 1_300_000))   # input tokens per OpenAI batch
BATCH_PRICE = (1.25, 5.00)
BATCH_CAP = float(os.environ.get("LSGEN_BATCH_CAP", "inf"))
OUT_PRIOR = {"desc": 400, "repair": 800}
PRICE = (2.50, 10.00)
PLACEHOLDER = json.dumps({"choices": [{"message": {"content": "```python\npass\n```"}}]})
_request, _http = requests.request, requests.Session()


def default_arg(path, flag):
    """An argparse default of LSGen's own script: its prompt templates live in the scripts' __main__ blocks."""
    for n in ast.walk(ast.parse(open(os.path.join(LSG, path), encoding="utf-8").read())):
        if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "add_argument" and n.args \
                and getattr(n.args[0], "value", None) == flag:
            return next(ast.literal_eval(k.value) for k in n.keywords if k.arg == "default")


def auth():
    """Authorization header for the real OpenAI API only (the key never goes to a local stand-in server)."""
    return {"Authorization": "Bearer " + openai_key()} if OPENAI.startswith("https://api.openai.com/") else {}


def openai_key():
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("set OPENAI_API_KEY")
    return os.environ["OPENAI_API_KEY"]


class _Resp:
    def __init__(self, text, code=200):
        self.text, self.status_code = text, code


class Transport:
    """Stands in for requests.request in LSGen's post functions."""

    def __init__(self, run, stage, rnd, batch):
        self.run, self.stage, self.rnd, self.batch = run, stage, rnd, batch
        self.cache_path, self.log_path = os.path.join(run, "llm_cache.jsonl"), os.path.join(run, "calls.jsonl")
        self.cache = {}
        if os.path.exists(self.cache_path):
            for line in open(self.cache_path, encoding="utf-8"):
                r = json.loads(line)
                self.cache[r["key"]] = r["text"]
        self.spent = 0.0
        if os.path.exists(self.log_path):
            self.spent = sum(r["cost"] for r in map(json.loads, open(self.log_path, encoding="utf-8")) if not r["cached"])
        self.budget = float(os.environ.get("LSGEN_BUDGET", "inf"))
        self.seen, self.pending, self.lock, self.local = Counter(), {}, threading.Lock(), threading.local()

    def __call__(self, method, url, headers=None, data=None, **kw):
        body = json.loads(data)
        body["model"] = MODEL                        # LSGen sends "gpt-4o-ca", its API proxy's name for GPT-4o
        text = self.call("chat", body)
        return _Resp(text) if text is not None else _Resp("", 500)

    def call(self, kind, body):
        h = hashlib.sha256(json.dumps([kind, body], sort_keys=True).encode()).hexdigest()[:40]
        with self.lock:              # the n-th identical request of a round (an LSGen retry) is a new sample, and so
            self.seen[h] += 1        # is the same prompt in a later round (re-retrieval may return the same pairs)
            key = f"r{self.rnd}-{h}-{self.seen[h]}"
        if key in self.cache:
            self.log(key, self.cache[key], 0.0, True)
            return self.cache[key]
        if self.batch:
            with self.lock:
                self.pending[key] = body
            return PLACEHOLDER
        if self.spent >= self.budget:
            raise SystemExit(f"LSGEN_BUDGET ${self.budget} reached")
        t0 = time.time()
        text = self.live(kind, body)
        if text is not None:
            with self.lock:
                with open(self.cache_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps({"key": key, "text": text}) + "\n")
                self.cache[key] = text
            self.log(key, text, time.time() - t0, False)
        return text

    def live(self, kind, body):
        """One HTTP call with backoff on rate limits/server errors; None if it keeps failing (LSGen then retries)."""
        url, hdr, payload = OPENAI + "/chat/completions", auth(), body
        for attempt in range(8):
            try:
                r = _http.post(url, headers=hdr, json=payload, timeout=1800)
                if r.status_code == 200:
                    return r.text
                print(f"HTTP {r.status_code}: {r.text[:300]}", file=sys.stderr)
                if r.status_code == 429 and any(c in r.text for c in ("insufficient_quota", "billing_not_active")):
                    raise SystemExit("OpenAI account cannot be billed; nothing more is sent")
                if r.status_code not in (408, 409, 429, 500, 502, 503, 504):
                    return None
            except requests.RequestException as e:
                print(f"request failed: {e}", file=sys.stderr)
            time.sleep(min(60, 2 ** attempt))
        return None

    def log(self, key, text, sec, cached):
        j = json.loads(text)
        u = j.get("usage") or {}
        pin, pout = u.get("prompt_tokens", 0), u.get("completion_tokens", 0)
        cost = (pin * PRICE[0] + pout * PRICE[1]) / 1e6
        rec = dict(sid=getattr(self.local, "sid", None), stage=self.stage, round=self.rnd, key=key, cached=cached,
                   model=j.get("model"), prompt_tokens=pin, completion_tokens=pout, sec=round(sec, 2), cost=cost)
        with self.lock:
            if not cached:
                self.spent += cost
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec) + "\n")

    def flush_batch(self, submit):
        """Write up to BATCH_TOKENS of uncached requests as an OpenAI Batch input file (and submit it); exit 3."""
        import tiktoken
        enc, chunk, total = tiktoken.encoding_for_model("gpt-4o"), {}, 0
        for key, body in self.pending.items():
            n = sum(len(enc.encode(m["content"])) + 4 for m in body["messages"]) + 3
            if chunk and total + n > BATCH_TOKENS:
                break
            chunk[key], total = body, total + n
        os.makedirs(os.path.join(self.run, "batches"), exist_ok=True)
        path = os.path.join(self.run, "batches", f"r{self.rnd}_{self.stage}_{int(time.time())}.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            for key, body in chunk.items():
                f.write(json.dumps({"custom_id": key, "method": "POST", "url": "/v1/chat/completions", "body": body}) + "\n")
        state_path = os.path.join(self.run, "batches", "state.json")
        state = load(state_path, {})
        spent = sum(s.get("cost", 0.0) for s in state.values())
        est = (total * BATCH_PRICE[0] + len(chunk) * out_per_request(state, self.stage) * BATCH_PRICE[1]) / 1e6
        print(f"batch input: {path} ({len(chunk)} of {len(self.pending)} pending requests, {total} input tokens, "
              f"estimated ${est:.2f}; billed so far ${spent:.2f})", flush=True)
        if submit and spent + est > BATCH_CAP:
            print(f"STOP: this batch could take the run to ${spent + est:.2f}, above LSGEN_BATCH_CAP ${BATCH_CAP:.2f}", flush=True)
            sys.exit(6)
        if submit:
            hdr = auth()
            fid = _http.post(OPENAI + "/files", headers=hdr, data={"purpose": "batch"},
                             files={"file": open(path, "rb")}).json()["id"]
            b = _http.post(OPENAI + "/batches", headers=hdr, json={"input_file_id": fid, "endpoint": "/v1/chat/completions",
                                                                   "completion_window": "24h"}).json()
            state[b["id"]] = {"input": path, "status": b["status"], "stage": self.stage, "round": self.rnd,
                              "requests": len(chunk), "est_in": total, "est_cost": round(est, 4),
                              "submitted": time.strftime("%Y-%m-%d %H:%M:%S")}
            dump(state_path, state)
            print(f"submitted batch {b['id']} (round {self.rnd} {self.stage})", flush=True)
        sys.exit(3)


def out_per_request(state, stage):
    done = [s for s in state.values() if s.get("stage") == stage and s.get("requests_ok")]
    return 1.25 * sum(s["out"] for s in done) / sum(s["requests_ok"] for s in done) if done else OUT_PRIOR[stage]


def ingest(run, lines):
    """Append a Batch output file's 200-responses to the response cache; (responses, input tokens, output tokens)."""
    n = pin = pout = 0
    with open(os.path.join(run, "llm_cache.jsonl"), "a", encoding="utf-8") as f:
        for line in lines:
            r = json.loads(line)
            if r.get("response") and r["response"]["status_code"] == 200:
                f.write(json.dumps({"key": r["custom_id"], "text": json.dumps(r["response"]["body"])}) + "\n")
                u = r["response"]["body"].get("usage") or {}
                n, pin, pout = n + 1, pin + u.get("prompt_tokens", 0), pout + u.get("completion_tokens", 0)
    return n, pin, pout


def batch_sync(run):
    path = os.path.join(run, "batches", "state.json")
    state, running = load(path, {}), False
    if not state:
        sys.exit(0)
    hdr = auth()
    for bid, s in state.items():
        if s["status"] in ("ingested", "failed", "cancelled"):
            continue
        b = _http.get(f"{OPENAI}/batches/{bid}", headers=hdr).json()
        if b["status"] in ("completed", "expired", "failed", "cancelled"):   # expired batches keep their finished part
            got, pin, pout = 0, 0, 0
            if b.get("output_file_id"):
                got, pin, pout = ingest(run, _http.get(f"{OPENAI}/files/{b['output_file_id']}/content", headers=hdr).text.splitlines())
            s.update(status="ingested" if b["status"] in ("completed", "expired") else b["status"], requests_ok=got,
                     cost=(pin * BATCH_PRICE[0] + pout * BATCH_PRICE[1]) / 1e6, finished=time.strftime("%Y-%m-%d %H:%M:%S"),
                     **{"in": pin, "out": pout})
            print(f"batch {bid} (round {s.get('round')} {s.get('stage')}): {b['status']}, {got}/{s.get('requests')} responses, "
                  f"{pin} in + {pout} out tokens = ${s['cost']:.2f}; billed so far "
                  f"${sum(x.get('cost', 0.0) for x in state.values()):.2f} {b.get('errors') or ''}", flush=True)
            if b["status"] == "failed":                    # e.g. over the token limit: stop instead of resubmitting
                dump(path, state)
                sys.exit(5)
        else:
            running = True
            if b["status"] != s["status"]:
                print(f"{time.strftime('%H:%M')} batch {bid}: {b['status']} {b.get('request_counts')}", flush=True)
                s["status"] = b["status"]
    dump(path, state)
    sys.exit(4 if running else 0)


def load(path, default):
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else default


def dump(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)


def encoder():
    import torch
    import torch.nn.functional as F
    sys.modules.setdefault("vllm", types.SimpleNamespace(LLM=None))    # LSGen imports vLLM (CUDA-only) at module level
    from transformers import AutoTokenizer, AutoModel
    from VectorRetrieval.VectorRetrievalSecondStage import encode_qwen  # LSGen's Qwen3 encoder (last-token pooling)
    dev = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(EMB, padding_side="left")
    model = AutoModel.from_pretrained(EMB).to(dev).eval()
    # as LSGen's vLLM path (encode_qwen_vllm): L2-normalized embeddings read into float32, so retrieval runs in float32
    return lambda codes: F.normalize(encode_qwen(tok, model, dev, codes).float(), p=2, dim=1).cpu() if codes \
        else torch.zeros(0, 1024)


def db_embeddings(enc, pids, db_path=DB, emb_dir="emb"):
    """Per problem: ids, users, and code1/code2 vectors of its DB pairs; vectors cached per pair in emb/<pid>.pt."""
    import torch
    db, out = load(db_path, []), {}
    os.makedirs(emb_dir, exist_ok=True)
    for pid in pids:
        path, rows = f"{emb_dir}/{pid}.pt", [r for r in db if r["problem_id"] == pid]
        vec = torch.load(path) if os.path.exists(path) else {}
        miss = [r for r in rows if r["submission1_id"] not in vec]
        if miss:
            t0 = time.time()
            c1, c2 = enc([r["code1"] for r in miss]), enc([r["code2"] for r in miss])
            vec.update({r["submission1_id"]: (c1[i], c2[i]) for i, r in enumerate(miss)})
            torch.save(vec, path)
            print(f"{pid}: {len(miss)} pairs embedded in {time.time() - t0:.0f}s", flush=True)
        ids = [r["submission1_id"] for r in rows]
        out[pid] = dict(ids=ids, users=[r["user_id"] for r in rows], c1=torch.stack([vec[i][0] for i in ids]),
                        c2=torch.stack([vec[i][1] for i in ids]))
    return {r["submission1_id"]: r for r in db}, out


def retrieve(items, rnd, k=5):
    """LSGen's edit-driven top-k retrieval among the problem's pairs, excluding every pair of the same student."""
    import torch
    import torch.nn.functional as F
    enc = encoder()
    db, emb = db_embeddings(enc, sorted({it["problem_id"] for it in items}))
    cos = lambda a, b: (F.normalize(a, p=2, dim=1) * F.normalize(b, p=2, dim=1)).sum(1)   # diag of calculate_similarity
    t0 = time.time()
    q = enc([it["code1"] for it in items])
    y = enc([it["code_content"] for it in items]) if rnd > 0 else None
    share = (time.time() - t0) / max(1, len(items))           # batched query encoding, split evenly
    for i, it in enumerate(items):
        t0, e = time.time() - share, emb[it["problem_id"]]
        score = cos(q[i] + (e["c2"] - e["c1"]), e["c2"])
        if rnd > 0:
            score = score + (1.0 - cos((y[i] - q[i]) + e["c1"], e["c2"]))
        own = torch.tensor([u == it["user_id"] for u in e["users"]], dtype=torch.bool)
        score[own] = -float("inf")
        top = torch.topk(score, min(k, int((~own).sum())))
        it["top_k_results"] = [{"MATCH_SCORE": float(s), "RetrievalCode": db[e["ids"][j]]["code1"],
                                "RetrievalSubmission1_id": e["ids"][j]} for s, j in zip(top.values.tolist(), top.indices.tolist())]
        it["_sec"] = time.time() - t0
    return items


def run_items(T, sids, fn, workers):
    def one(sid):
        T.local.sid, t0 = sid, time.time()
        r = fn(sid)
        r["_sec"] = time.time() - t0
        return r
    if workers == 1:
        return [one(s) for s in sids]
    with ThreadPoolExecutor(workers) as ex:
        return list(ex.map(one, sids))


def desc(T, items, in_path, workers):
    from ProcessData.Get_Bug_Description.GetBugDescription import DescManager, Description
    cache = os.path.join(T.run, "desc_cache.json")       # LSGen's retrieval_desc_dataset: one description per DB pair
    if not os.path.exists(cache):
        dump(cache, {})
    dm = DescManager(default_arg("ProcessData/Get_Bug_Description/GetBugDescription.py", "--prompt_template"), "python",
                     in_path, PQ, os.path.join(T.run, "tmp"), "unused.json", cache, model=MODEL, retrieval_data_file=DB)
    client = Description(dm.language, "", OPENAI + "/chat/completions", temperature=dm.temperature, model_type=dm.model)
    out = run_items(T, [it["submission1_id"] for it in items], lambda s: dm.process_single(s, client), workers)
    if not T.pending:
        dump(cache, dm.retrieval_desc_data)
    return out


def repair(T, items, in_path, workers):
    import Eval.RepairCodeAndExplainRetryDiff as R
    R.API_URL = OPENAI + "/chat/completions"
    rm = R.RepairManager(default_arg("Eval/RepairCodeAndExplainRetryDiff.py", "--prompt_template"), "python", in_path, PQ,
                         os.path.join(T.run, "tmp"), "unused.json", model=MODEL, topk=5, Retrieval_database=DB)
    return run_items(T, [it["submission1_id"] for it in items], rm._process_submission, workers)


if __name__ == "__main__":
    stage, run = sys.argv[1], os.path.abspath(sys.argv[2])
    paths = [None if a == "-" else os.path.abspath(a) for a in sys.argv[4:6]]        # IN.json, OUT.json (before chdir)
    os.makedirs(run, exist_ok=True)
    sys.path.insert(0, LSG)
    os.chdir(WORK)
    if stage == "batch-sync":
        batch_sync(run)
    (in_path, out_path), rnd, batch = paths, int(sys.argv[3]), "--batch" in sys.argv
    items = load(in_path, []) if in_path else []
    if stage == "embed":                                       # IN.json: pairs to embed ("-": the database)
        db = in_path or DB
        db_embeddings(encoder(), sorted({r["problem_id"] for r in load(db, [])}), db)
        sys.exit(0)
    if stage == "retrieve":
        out = retrieve(items, rnd)
    else:
        T = Transport(run, stage, rnd, batch)
        requests.request = T
        out = (desc if stage == "desc" else repair)(T, items, in_path, 1 if batch else 10)   # LSGen's num_workers = 10
        if T.pending:
            T.flush_batch("--submit" in sys.argv)
    dump(out_path, out)
