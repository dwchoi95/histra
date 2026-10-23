import os, re, sys
from collections import Counter

SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # src/ (import root)
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from run import load_problem, ac_pool
from core.searcher import Searcher
from core.sketch import Sketcher
from core.standardizer import Standardizer
from core.align import Aligner
from utils.ast_utils import AstUtils


def parse_run(path):
    res = {}
    if path and os.path.exists(path):
        for line in open(path, encoding="utf-8", errors="replace"):
            m = re.search(r"(u\d+)\s+pass=(True|False)", line)
            if m:
                res[m.group(1)] = (m.group(2) == "True")
            elif re.search(r"(u\d+)\s+skip", line):
                res[re.search(r"(u\d+)", line).group(1)] = "skip"
    return res


def main():
    pid = sys.argv[1] if len(sys.argv) > 1 else "p02909"
    run = parse_run(sys.argv[2] if len(sys.argv) > 2 else "")
    trajs, tests, problem, _timeout = load_problem(pid)
    codes, users = ac_pool(trajs)
    index = Searcher(codes, users=users)

    leak = 0
    agg = Counter()
    need = Counter()        # total ops needed by type
    uncov = Counter()       # uncovered ops by type
    per_outcome = Counter()  # (has_uncovered_repl_del, has_insert, outcome)

    for t in trajs:
        uid = t["user_id"]
        wa = [s["code"] for s in t["submissions"][:-1]]   # WA1..WAn only
        ac_std = Standardizer.standardize(t["submissions"][-1]["code"])  # held-out oracle
        sk0 = Sketcher.build(wa)
        std_sn = Standardizer.standardize(wa[-1])
        if sk0 is None or ac_std is None or std_sn is None:
            continue
        cands = index.search(std_sn, exclude_user=uid)
        if any(c == ac_std for c in cands):                # setting check: own AC leaked?
            leak += 1
        # frozen skeleton of the final (with-ref) sketch
        ref = cands[0] if cands else None
        prep = Sketcher.standardize_wa(wa)
        skf = Sketcher.final(prep[0], prep[1], wa[-1], ref_ac=ref) if prep else None
        frozen = skf.frozen_sigs if skf else sk0.frozen_sigs
        ops = Aligner.edit_ops(std_sn, ac_std)
        if ops is None:
            continue
        r = d = i = u_rd = 0
        for kind, an, bn in ops:
            if kind == "insert":
                i += 1
            else:                                          # replace / delete on buggy node
                (r := r + 1) if kind == "replace" else (d := d + 1)
                au = AstUtils.safe_unparse(an)
                if au is not None and au in frozen:        # buggy-wrong subtree stayed frozen
                    u_rd += 1
        need["replace"] += r; need["delete"] += d; need["insert"] += i
        uncov["replace_delete_frozen"] += u_rd
        outcome = run.get(uid, "?")
        per_outcome[(u_rd > 0, i > 0, outcome)] += 1
        agg[outcome] += 1

    print(f"\n=== {pid}: setting check ===")
    print(f"  sketch input = WA1..WAn (subs[:-1]); target AC excluded from search.")
    print(f"  own-AC leaked into candidates: {leak} (should be 0)")

    print(f"\n=== edit ops needed (buggy -> student's own AC), summed ===")
    for k in ("replace", "delete", "insert"):
        print(f"  {k:8s}: {need[k]}")
    print(f"  replace/delete on FROZEN buggy subtree (uncoverable): "
          f"{uncov['replace_delete_frozen']}")

    print(f"\n=== per-trajectory: (uncovered_repl/del?, needs_insert?) x outcome ===")
    print(f"{'uncov_rd':>9} {'insert':>7} {'pass':>5} {'fail':>5} {'skip':>5} {'?':>3}")
    for urd in (False, True):
        for ins in (False, True):
            row = [per_outcome[(urd, ins, o)] for o in (True, False, "skip", "?")]
            if sum(row):
                print(f"{str(urd):>9} {str(ins):>7} {row[0]:5d} {row[1]:5d} {row[2]:5d} {row[3]:3d}")
    print("\ninterpretation:")
    print("  uncov_rd=True  -> a replace/delete bug sits in the FROZEN skeleton "
          "(Align must inject a hole there)")
    print("  insert=True    -> fix needs INSERTING code with no buggy anchor "
          "(replacement-holes can't host it)")


if __name__ == "__main__":
    main()
