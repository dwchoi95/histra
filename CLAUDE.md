# CLAUDE.md (paper)

This folder is the `paper` branch of the histra repository, checked out as a git worktree at `histra/paper/`
(`git worktree add paper paper`): commit here for the paper, in the parent folder for the code (`dev`). The parent's
`.git/info/exclude` hides this folder from `dev` and `main`.

- English; strict `\documentclass[10pt,conference]{IEEEtran}` — no compsoc, no spacing/font/caption changes
  (desk-reject risk), so no `caption` package; 10 pages + 2 pages of references.
- Write each section by following `guidelines/section/<section>.md` (`skeleton.md` = overall structure,
  `floats.md` = figure/table design). Tool name via `\tool{}`.
- `notes/`: mock reviews and the expert-evaluation research behind RQ4.
- Tables and figure data: `python paper/summarize.py` (reads `../output/`, writes `tables.tex` and `numbers.txt` here),
  then `python3 paper/fill_tables.py` (copies the `% rows:<name>` sections of `tables.tex` into `main.tex`).
- Numbers in the text only: `paper/expert_analyze.py` (RQ4 kappa, shares, sign tests), `paper/fixregion.py`
  (Section II-B), `paper/std_effect.py` (RQ3).
- `python3 paper/to_english.py paper/main.tex > main.en.tex` — submission (English-only) source from the Korean draft.
- Build in a scratch copy: `pdflatex → bibtex → pdflatex ×2`, then check `main.log` for `^!|undefined`.
- PDFs (`main.pdf`, `guidelines/*.pdf`) stay local (`.gitignore`).
