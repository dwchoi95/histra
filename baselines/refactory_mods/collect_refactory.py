"""Collect Refactory results into the shared metric schema.

Refactory writes data_histra/<pid>/refactory_online.csv with a "Repair" column
holding the repaired program (wrapped in def __main__(), regularized). For each
buggy program we: extract the patch, UNWRAP it (strip the __main__ wrapper, take
its body), then re-validate with OUR Validator and score TED/IP with OUR metrics
so Refactory is measured identically to Histra and PaR.

Output: results_refactory/<pid>/results.csv and results_refactory/overall.csv
(same columns as the Histra runner).
"""
import os, sys, csv, json, ast, argparse, time
from statistics import mean

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
import warnings
warnings.filterwarnings("ignore")

from src.utils import DataLoader
from src.core.validator import Validator
from src.utils import metrics as _metrics


def unwrap(code: str):
    """Take def __main__(): body and return it dedented as a standalone module."""
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
    # not wrapped (shouldn't happen) -> return as-is
    return code


def collect_problem(pid, timeout, tests, trajs, refs, data_root, out_root):
    base = os.path.join(data_root, pid)
    csv_path = os.path.join(base, "refactory_online.csv")
    inc_path = os.path.join(base, "incremental.jsonl")
    manifest_path = os.path.join(base, "manifest.json")
    if not os.path.exists(manifest_path):
        print(f"[{pid}] missing manifest, skip")
        return None
    if not os.path.exists(csv_path) and not os.path.exists(inc_path):
        print(f"[{pid}] no csv and no incremental.jsonl, skip")
        return None
    manifest = json.loads(open(manifest_path, encoding="utf-8").read())

    Validator.init_globals(tests, timeout)

    # map uid -> repaired (raw, wrapped) code. Prefer the incremental JSONL (one
    # line per finished wrong -> survives a timeout); fall back to the final CSV.
    repaired = {}
    if os.path.exists(inc_path):
        with open(inc_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                fn = rec.get("file_name", "")
                if not fn.startswith("wrong_") or not fn.endswith(".py"):
                    continue
                uid = fn[len("wrong_"):-len(".py")]
                if str(rec.get("status", "")).startswith("success"):
                    repaired[uid] = rec.get("rep_code", "")
    elif os.path.exists(csv_path):
        with open(csv_path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                fn = row.get("File Name", "")
                if not fn.startswith("wrong_") or not fn.endswith(".py"):
                    continue
                uid = fn[len("wrong_"):-len(".py")]
                if str(row.get("Status", "")).startswith("success"):
                    repaired[uid] = row.get("Repair", "")

    rows = [("user_id", "pass", "ted", "ip", "att_seconds", "buggy", "fixed", "oracle")]
    pass_cnt = 0
    ted_vals, ip_vals = [], []
    sampled = sorted(manifest.keys())          # the buggy programs given to Refactory
    n_users = max(len(sampled), 1)

    for uid in sampled:
        info = manifest.get(uid, {})
        buggy = info.get("buggy", "")
        oracle = info.get("oracle", refs.get(uid, ""))
        patch = None
        raw = repaired.get(uid)
        if raw:
            cand = unwrap(raw)
            if cand:
                try:
                    if Validator.run(cand).passed():
                        patch = cand
                except Exception:
                    patch = None
        passed = patch is not None
        ted = _metrics.ted(buggy, patch) if passed and buggy else None
        ip = (_metrics.intent_preservation(buggy, patch, oracle)
              if passed and buggy and oracle else None)
        if passed:
            pass_cnt += 1
            if ted is not None: ted_vals.append(ted)
            if ip is not None: ip_vals.append(ip)
        rows.append((uid, int(passed),
                     ted if ted is not None else "",
                     ip if ip is not None else "",
                     "", buggy, patch or "", oracle or ""))

    out_dir = os.path.join(out_root, pid)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "results.csv"), "w", newline="",
              encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

    rr = pass_cnt / n_users
    s = {"pid": pid, "rr": rr, "pass": pass_cnt, "n_users": n_users,
         "ted_mean": mean(ted_vals) if ted_vals else 0.0,
         "ip_mean": mean(ip_vals) if ip_vals else 0.0}
    print(f"[{pid}] RR={rr:.3f} pass={pass_cnt}/{n_users} "
          f"ted={s['ted_mean']:.2f} ip={s['ip_mean']:+.2f} "
          f"(repaired-by-tool={len(repaired)})")
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--dataset", default=os.path.join(ROOT, "data"))
    ap.add_argument("-p", "--problems", nargs="+", default=None)
    ap.add_argument("--data_root", default=os.path.join(HERE, "data_histra"))
    ap.add_argument("-o", "--out", default=os.path.join(HERE, "results_refactory"))
    args = ap.parse_args()

    problems = DataLoader.run(args.dataset)
    if args.problems:
        problems = [p for p in problems if p[0] in args.problems]
    os.makedirs(args.out, exist_ok=True)
    summaries = []
    for pid, timeout, tests, trajs, refs in problems:
        s = collect_problem(pid, timeout, tests, trajs, refs,
                            args.data_root, args.out)
        if s: summaries.append(s)

    if summaries:
        header = ["pid", "rr", "pass", "n_users", "ted_mean", "ip_mean"]
        with open(os.path.join(args.out, "overall.csv"), "w", newline="",
                  encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(header)
            for s in summaries:
                w.writerow([s["pid"], f"{s['rr']:.6f}", s["pass"], s["n_users"],
                            f"{s['ted_mean']:.6f}", f"{s['ip_mean']:.6f}"])


if __name__ == "__main__":
    main()
