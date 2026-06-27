# histra

Submission-History-Aware Automated Program Repair

Intent-preserving repair: freeze the stable skeleton of a student's latest buggy
submission, hole only the changed parts, generate patch, return the patch
in the student's own style. 


## Layout

- `src/` — implementation, import root (`PYTHONPATH=src`, prefix-free imports)
  - `run.py` — CLI runner (`env/bin/python run.py`)
  - `src/core/` — pipeline stages
  - `src/utils/` — shared helpers, dataclasses, dataset builder;
- `data/` — evaluation data (`data/README.md` describes the benchmark + schema)
- `paper/` — paper source (`main.tex` + `references.bib`)

See `CLAUDE.md` for the full architecture and conventions.
