# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this is

`histra` is **submission-history-aware, intent-preserving program repair** for competitive-programming
submissions. Given a student's trajectory of wrong-answer (WA) submissions, it keeps the "intent skeleton" of the
latest WA (code unchanged across the student's own history), holes the changed parts, and fills the holes with
fragments taken from **other students' accepted (AC) submissions — no LLM**. Novelty axis: intent inferred from the
student's OWN trajectory (vs alignment-, localization-, and knowledge-based techniques, which rely on references,
tests, or models of common mistakes).

## Branches

- `dev`: development, every commit. Tracks `README.md`, `LICENSE`, `requirements.txt`, `run.py`, `src/`, `tests/`,
  this file, `data.tar.xz`, `output.tar.xz` (each folder packed whole, README inside).
- `main`: the anonymous artifact (mirrored through anonymous.4open.science), one orphan commit = `dev` minus `tests/`,
  this file, and our safety devices (LSGen spending caps/billing prints, `wait_idle`, `recheck`).
- Local only (git-ignored): `results/` (every experiment ever run), `baselines/` (forks), `data.zip`, `test.ipynb`, `.env`.
- Unpack before running anything: `tar -xJf data.tar.xz`,
`tar -xJf output.tar.xz` → `output/{approaches,ablation,expert}/` (`output/summary/` = generated
tables/numbers, not shipped). Names: `histra`, `refactory`, `brafar`, `lsgen` (approaches/), ablation by mode (`nohist`,
`randhole0`, ...); `common.path(name)` maps a name to its file. Repack `output/` without `summary/` into `output.tar.xz`.

## Pipeline (`src/core/histra.py`, `HISTRA.sketch` / `HISTRA.repair`)

```text
trajectory WA_1..WA_n (WA_n = buggy anchor); refs = other users' final ACs (own AC never used)
  → Standardizer.run   # canonical AST (range/loops/compare/augassign/empty containers) + `._origin` provenance
  → Sketcher.run       # APTED vs every earlier WA; anchor nodes matched in ALL = preserved, rest → __HOLE_k__
  → Reformatter.run    # project holes onto the original (non-canonical) anchor via provenance
  → Searcher.run       # top-20 refs by IDF-weighted skip-gram weighted Jaccard (core/features.py)
  → Repair.run         # MergeRepair (core/merge.py) of each ref into the pristine anchor:
                       #   phase 1 freezes pure-skeleton nodes (hole-only merge), phase 2 free merge;
                       #   first passing patch → Minimizer (core/minimize.py): revert to the student's
                       #   code while tests pass, skeleton region first, budget 20 validations
```

- The paper groups these as **Sketch · Search · Repair**; Validate/Minimize ⊂ Repair. Tests run through
  `core/validator.passes(src, tests, timeout)`.
- Phase 2 may touch the skeleton → the paper only claims patches "tend to keep" it.
- `ast.Load`/operator nodes are tree-wide shared singletons (`repair.SHARED`): never put them in id-sets (`holed`), or
  every node containing a read looks holed (`tests/test_sketch_holes.py`). Repair's frozen set excludes them too
  (`tests/test_repair_ops.py`). Minimize breaks ties by tree position, not `id()`.
- Skeleton labels (`src/experiments/skel._label`) include operators (`Compare:Lt`, `BinOp:Add`);
  `tests/test_retention_ops.py`.
- APTED on whole modules costs ~5s/call — keep it out of per-candidate loops (use `MergeRepair._match`).

## Commands

```bash
python run.py p02742                 # HISTRA on one problem: replaces its rows in output/approaches/histra.jsonl
python run.py -m MODE                # min | nostd nohole nokept plain sizemin | nohist randhole(HSEED) randfrac fl -> output/ablation/
python src/experiments/measure.py output/approaches/refactory.jsonl ...  # (re)add metrics to rows in place
python src/experiments/summarize.py  # output/summary/tables.tex (every table/figure) + numbers.txt (numbers in the text)
```

- Each result row carries its metrics (`measure.metrics`: skel_share, ret_patch, ret_oracle; approaches also kept, dist),
  added by `run.py` and at the end of each baseline runner. Experiments read `data/`, write `output/<group>/`; env `ONLY=<pid,...>`, `POOL` (default 16), `PER=k` (sample k per problem).
- Baselines: `src/experiments/baselines/<tool>/setup.sh` clones the upstream commit into `upstream/` and applies
  `histra.patch`; runners `run_refactory.py`, `run_brafar.py` (records Brafar's internal timeouts; `RERUN=` reruns
  load-sensitive rows on an idle machine), `run_lsgen.py {prep|run|recheck}` (GPT-4o; `OPENAI_API_KEY`, `CODENET`).
- RQ4: `output/expert/ratings.csv` (both raters + adjudicated); `expert_analyze.py` (kappa, shares, sign tests). The rating
  kit (pages, key, protocol) stays local in `results/expert_eval/`; `expert_kit.py` is on `pre-artifact`.
- Regression checks: `.venv/bin/python tests/test_*.py` (and `tests/standardizer.py`).
- Long runs: `nohup caffeinate -is sh <script> &`; all heavy experiments run on SuperServer (`~/histra-mentored`, which
  still has the pre-cleanup layout). Never run other CPU-heavy work alongside a run that validates tests.

## Gotchas

- Heavy tests (p02686, 2s timeout) flake under CPU load: correct patches take ~1.8 s on the heaviest test, so even
  light concurrent work (pdflatex, summarize.py) flips passes to timeouts. Run p02686 alone (POOL=4) on an idle machine.
- Run scripts from the repo root; `src/experiments/*` import `common` (puts the root on `sys.path`) and `src.core.*`.
- No `from __future__` (Python 3.13; the FL control needs 3.12+ `sys.monitoring`). The benchmark is eval-only.
- Artifact hygiene: no names, paths, or accounts in tracked files; archives are packed with
  `COPYFILE_DISABLE=1 tar --format=ustar --uid 0 --gid 0 --uname root --gname root` and `xz -9e`.
