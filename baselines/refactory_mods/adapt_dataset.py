"""Adapt the Histra dataset (stdin/stdout AtCoder programs) into Refactory's
folder layout, wrapping every program into a single `def __main__():` function.

Why wrap: Refactory's `regularize` deletes all module-level statements and its
repair pipeline is keyed on FunctionDef names, so a flat stdin/stdout script
reduces to an empty program. Wrapping the whole body into one named function
(`__main__`) preserves the code, gives every program the same function name for
structural alignment, and lets the patched harness call it via entry_code
"__main__()" with stdin fed from input files. A `def main(): ...; main()`-style
script also works: the inner `main()` call is no longer top-level so it survives.

Output layout (per problem), consumed by `run.py -d data_histra -q <pid> ...`:
  data_histra/<pid>/ans/input_NNN.txt , output_NNN.txt   (raw stdin/stdout)
  data_histra/<pid>/code/global.py                       (empty)
  data_histra/<pid>/code/reference/reference.py          (one AC, wrapped)
  data_histra/<pid>/code/correct/<uid>.py                (donor ACs, wrapped)
  data_histra/<pid>/code/wrong/<uid>.py                  (last-WA buggy, wrapped)

Also writes data_histra/<pid>/manifest.json mapping uid -> original (unwrapped)
buggy and oracle code, for consistent TED/IP scoring after repair.

NOTE on donors: Refactory repairs all wrong programs in one batch against one
correct pool, so per-instance exclusion of a student's own AC is not supported.
The correct pool therefore includes every AC (mild self-leakage that, if
anything, inflates Refactory's results); this is disclosed as a limitation.
"""
import os, sys, json, ast, argparse, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
from src.utils import DataLoader


def strip_main_guard(code: str) -> str:
    """If the program is `if __name__ == '__main__': <body>`, return the dedented
    body so it can be re-wrapped uniformly. Otherwise return code unchanged."""
    try:
        tree = ast.parse(code)
    except Exception:
        return code
    new_body = []
    for node in tree.body:
        if (isinstance(node, ast.If) and isinstance(node.test, ast.Compare)
                and isinstance(node.test.left, ast.Name)
                and node.test.left.id == "__name__"):
            new_body.extend(node.body)
        else:
            new_body.append(node)
    try:
        return ast.unparse(ast.Module(body=new_body, type_ignores=[]))
    except Exception:
        return code


def wrap(code: str) -> str:
    """Wrap a whole-program script into `def __main__():` (4-space indented)."""
    code = strip_main_guard(code)
    body = code.rstrip("\n")
    if not body.strip():
        body = "pass"
    indented = textwrap.indent(body, "    ")
    return "def __main__():\n" + indented + "\n"


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def adapt_problem(pid, tests, trajs, refs, out_root, sample=None):
    base = os.path.join(out_root, pid)
    code_dir = os.path.join(base, "code")

    # tests -> ans/input_NNN.txt, output_NNN.txt (raw)
    for i, tc in enumerate(tests, 1):
        write(os.path.join(base, "ans", f"input_{i:03d}.txt"), tc["input"])
        write(os.path.join(base, "ans", f"output_{i:03d}.txt"), tc["output"])

    write(os.path.join(code_dir, "global.py"), "")

    # correct pool = every student's AC (wrapped); reference = first AC
    ac_items = [(u, c) for u, c in refs.items() if c and c.strip()]
    if not ac_items:
        return 0
    # NO LEAKAGE: the buggy targets are the sampled users; exclude THEIR own ACs
    # (oracles) from the correct pool and from the reference, so no buggy is ever
    # repaired against its own accepted solution. This matches the self-exclusion
    # used by the HISTRA+ and PaR runs.
    wrong_uids = sorted(trajs.keys())          # deterministic order
    if sample:
        wrong_uids = wrong_uids[:sample]
    target_set = set(wrong_uids)
    pool = [(u, c) for u, c in ac_items if u not in target_set]
    if not pool:                                # fallback: tiny problem
        pool = ac_items
    ref_uid, ref_code = pool[0]                 # reference from a non-target AC
    write(os.path.join(code_dir, "reference", "reference.py"), wrap(ref_code))
    for u, c in pool:
        # Refactory keys files by 'correct'/'wrong' prefix conventions
        write(os.path.join(code_dir, "correct", f"correct_{u}.py"), wrap(c))

    # wrong pool = each sampled student's last WA (buggy), wrapped
    manifest = {}
    n_wrong = 0
    for u in wrong_uids:
        was = trajs.get(u) or []
        if not was:
            continue
        buggy = was[-1]
        if not buggy or not buggy.strip():
            continue
        try:
            ast.parse(buggy)
        except Exception:
            continue  # Refactory needs parseable input
        write(os.path.join(code_dir, "wrong", f"wrong_{u}.py"), wrap(buggy))
        manifest[u] = {"buggy": buggy, "oracle": refs.get(u, "")}
        n_wrong += 1

    write(os.path.join(base, "manifest.json"),
          json.dumps(manifest, ensure_ascii=False))
    return n_wrong


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--dataset", default=os.path.join(ROOT, "data"))
    ap.add_argument("-p", "--problems", nargs="+", default=None)
    ap.add_argument("-o", "--out", default=os.path.join(HERE, "data_histra"))
    ap.add_argument("-n", "--sample", type=int, default=None,
                    help="cap buggy programs per problem (deterministic: sorted uids)")
    args = ap.parse_args()

    problems = DataLoader.run(args.dataset)
    if args.problems:
        problems = [p for p in problems if p[0] in args.problems]
    for pid, timeout, tests, trajs, refs in problems:
        n = adapt_problem(pid, tests, trajs, refs, args.out, sample=args.sample)
        print(f"[{pid}] tests={len(tests)} correct={len(refs)} wrong={n}")


if __name__ == "__main__":
    main()
