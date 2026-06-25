# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

HISTRA — Submission-History-Aware Automated Program Repair. Given a student's
trajectory of submissions to a competitive-programming problem (several Wrong
Answers ending in an Accepted), it repairs the student's **last buggy** submission
while preserving their intent: freeze the parts of the program that stayed stable
across the trajectory, hole only the parts that kept changing, and fill the holes
with minimal subtrees borrowed from *other students'* accepted solutions. The fix
is returned in the student's own style rather than by adopting someone else's AC.

## Environment & commands

Python 3.13 in a checked-out venv at `env/` (gitignored but present on disk). Run
everything through it, from the **repo root** (modules import with the `src.`
prefix, so the repo root must be the working directory / on `sys.path`):

```bash
env/bin/python run.py -d data            # run the full benchmark, write results/
env/bin/python run.py -d data -r         # reset: recompute even if results/ exists
env/bin/pip install -r requirements.txt  # deps: apted, sympy, tqdm, prettytable
```

`run.py` flags: `-d/--dataset` (required, a directory of `data/<pid>/` problems),
`-r/--reset`, `-s/--sampling`, `-ab/--ablation` (the ablation choices are declared
in the argparser but **not yet wired into the pipeline** — `HISTRA` ignores them).

Output: one process per problem writes `results/<pid>/results.csv` (per-user:
pass/ted/ip/att + buggy/fixed/oracle source), and all processes update the shared
`results/overall.csv` under a multiprocessing `Lock`. A `results/<pid>/results.csv`
that already exists is skipped unless `-r`.

### Running a single problem / no test framework

There is no pytest suite. To exercise the pipeline on one problem, point `-d` at a
single problem directory: `env/bin/python run.py -d data/p02686`.

`test.py` is a **stale** manual smoke script — it calls `DataLoader.parse(...)`,
which no longer exists (see Data loading below). Don't trust it as-is; `run.py` is
the real entry point. `tests.ipynb` is a scratch notebook.

## Pipeline architecture

`run.py` → `src/core/histra.py::HISTRA`. For each user, `HISTRA._pipeline_run`
runs six stages in order (`src/core/`), each a small class with a `run(...)`
classmethod/method. The non-obvious through-line is a chain of **AST provenance**:
every transformed node carries an `_origin` attribute pointing back to the node in
the user's original source, so the final patch can be projected back onto the
student's actual surface syntax.

1. **`standardizer.py::Standardizer`** (`ast.NodeTransformer`) — canonicalizes
   *every* submission in the trajectory so that superficial differences don't look
   like real changes: `x += y` → `x = x + y`, `for`/`while` → desugared
   `while True:` + `iter`/`next`/`break`, descending comparisons flipped to
   ascending, `list()/dict()/tuple()` → literals, `range(...)` → 3-arg form.
   Returns `(std_ast, org_ast)` pairs and tags created nodes with `_origin` via
   `_carry`/`_org`. Fresh loop temporaries are named `_itN` (collision-checked).

2. **`sketch.py::Sketcher`** — over the *standardized* trajectory, uses APTED tree
   edit-mapping to find which **expression** nodes of the anchor (the last buggy
   submission = `std_traj[-1]`) stayed label-stable across *all* earlier
   submissions. Stable nodes are "preserved"; the rest are replaced with a
   `Name(id="__HOLE__")` marker. This is the intent-preservation core.

3. **`reformat.py::Reformatter`** — walks the standardized anchor and the sketched
   anchor in parallel to learn which anchor nodes became holes, then projects those
   holes back onto the **original (un-standardized)** anchor AST via `_origin`, so
   the skeleton is in the student's own surface form.

4. **`searcher.py::Searcher`** — for each statement of the sketched program, finds
   the best-matching statement among *other users'* accepted solutions (`refs`).
   Variable names in refs are first remapped to the anchor's names using def-use
   profiles + cosine similarity + a hand-rolled **Hungarian** assignment
   (`_varmap_defuse`/`_hungarian`). Matching is APTED edit distance with a custom
   `NConfig` where **holes cost 0** to insert/delete/rename. Ties broken randomly
   (`random.choice`) — runs are nondeterministic. Returns `{id(stmt): ref_node}`.

5. **`repair.py::Repair`** (`ast.NodeTransformer`) — splices the matched ref
   subtrees in at the mapped statement ids. If any `__HOLE__` survives, the patch
   failed → returns `None`; otherwise `ast.unparse`s the patched tree to source.

6. **`validator.py::Validator`** — runs the candidate patch as a subprocess
   (`python -c <code>`) against every test case in a `fork` multiprocessing pool,
   normalizing whitespace before comparison. Patch is accepted only if **all**
   cases pass, else the user's result is `None`.

Node identity (`id(node)`) is used as the key throughout (node_map, covered sets,
matched sets) — these dicts/sets are only valid within a single process and AST
object graph; don't serialize them.

### APTED wrapper

APTED needs nodes exposing `.name`/`.children`. `src/utils/node.py::Node` is that
adapter (`__slots__` = name, children, node). Each stage builds its own `Node`
labeling scheme — e.g. `metrics._label` is value-aware (`Name:x`, `Const:1`) so
`x=1` and `x=2` differ, while `searcher._label_for` deliberately drops `ctx` and
child-bearing fields. When changing what counts as "the same node," edit the
relevant `_label*`/`_node` builder, not `Node`.

## Data

`data/<pid>/` holds `trajectories.jsonl`, `tests.jsonl`, `meta.json`,
`problem.html`. See `data/README.md` for selection criteria and full schema. Each
trajectory is `{user_id, submissions:[{sid, ts, verdict, code}]}`; the benchmark is
Project_CodeNet Python800 / AtCoder, Python3, AC/WA verdicts only.

**Data loading** (`src/utils/data_loader.py::DataLoader`): `run(path)` →
`get_problem` splits each user's submissions into `trajs[user_id]` = list of WA
codes (the buggy trajectory) and `refs[user_id]` = that user's own AC code (the
oracle). `HISTRA._get_ac_pool` builds the search pool by taking *all other* users'
ACs (the current user's own AC is excluded — no self-leakage). Note the timeout:
`meta.json` actually stores `time_limit_ms`, but `get_problem` reads a `"timeout"`
key, so it currently always falls back to the 2000 ms / 2 s default.

`src/utils/build_dataset.py::DatasetBuilder` regenerates `data/` from a local
Project_CodeNet checkout; its `CN = /Users/cdw/...` paths are machine-specific and
won't run here.

## Metrics

`src/utils/metrics.py`: `ted` = value-aware AST tree edit distance (APTED);
`intent_preservation(buggy, fixed, oracle)` = `(TED_s − TED_f)/(TED_s + TED_f)`
where `TED_s` = buggy↔oracle and `TED_f` = buggy↔fixed. Positive means the fix
stays closer to the student's buggy program than the oracle AC would — the central
claim the project measures.

## Conventions

- Several stages carry Korean inline comments alongside English ones; match the
  existing bilingual style of the file you're editing.
- Stages are stateless façades: a `run(...)` classmethod that constructs the
  transformer and returns plain data (AST or source string). Keep new stages in
  that shape so `HISTRA._pipeline_run` stays a flat sequence.
