# histra

Submission-History-Aware Automated Program Repair

Intent-preserving repair: freeze the stable skeleton of a student's latest buggy
submission, hole only the buggy parts, let an LLM fill the holes, return the patch
in the student's own style. Pipeline: **Standardize → Sketch → Search → Align →
Reformatting → Repair → Validation**.

## Layout

- `src/` — implementation, import root (`PYTHONPATH=src`, prefix-free imports)
  - `src/run.py` — CLI runner (`.venv/bin/python src/run.py p02909`)
  - `src/core/` — pipeline stages (standardize, sketch, search, align, reformat, repair, histra)
  - `src/verify/` — held-out test execution; `src/model/` — Ollama client
  - `src/utils/` — shared helpers, dataclasses, dataset builder; `src/analysis/` — diagnostics
- `data/` — evaluation data (`data/README.md` describes the benchmark + schema)
- `paper/` — paper source (`main.tex` + `references.bib`)

See `CLAUDE.md` for the full architecture and conventions.
