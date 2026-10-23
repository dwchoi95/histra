"""Replace one problem's rows in results/eval/<mode>.jsonl with the re-run rows in results/eval/<pid>/<mode>.jsonl
(the originals are kept as <mode>.pool14.jsonl). Usage: python splice.py p02686 merge histra_min ..."""
import json, os, shutil, sys

pid, D = sys.argv[1], "results/eval"
for mode in sys.argv[2:]:
    full, part = f"{D}/{mode}.jsonl", f"{D}/{pid}/{mode}.jsonl"
    shutil.copy(full, f"{D}/{mode}.pool14.jsonl")      # always back up the current run (a stale backup would revert it)
    new = {r["user"]: r for r in map(json.loads, open(part))}
    rows = [json.loads(l) for l in open(f"{D}/{mode}.pool14.jsonl")]
    assert {r["user"] for r in rows if r["pid"] == pid} == set(new), mode
    with open(full, "w") as f:
        for r in rows:
            f.write(json.dumps(new[r["user"]] if r["pid"] == pid else r) + "\n")
    print(mode, "spliced", len(new), "rows of", pid)
