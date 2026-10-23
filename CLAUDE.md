# CLAUDE.md (paper)

This folder is the `paper` branch of the histra repository, checked out as a git worktree at `histra/paper/`
(`git worktree add paper paper`): commit here for the paper, in the parent folder for the code (`dev`). The parent's
`.git/info/exclude` hides this folder from `dev` and `main`.

- English; strict `\documentclass[10pt,conference]{IEEEtran}` — no compsoc, no spacing/font/caption changes
  (desk-reject risk), so no `caption` package; 10 pages + 2 pages of references.
- Write each section by following `guidelines/section/<section>.md` (`skeleton.md` = overall structure,
  `floats.md` = figure/table design). Tool name via `\tool{}`.
- `notes/`: mock reviews and the expert-evaluation research behind RQ4.
- Draft layout: each paragraph is written in Korean (commented with `% `) directly above its live English version;
  floats, math, captions, abbreviations, and key terms stay English. Answer the user in Korean.
- Workflow: show a Korean proposal of each change first and apply it after approval; plans list tasks only (no schedule).
- Style: results paragraphs go table/figure -> numbers -> conclusion last; comparisons as relative "% more/less",
  consistent within a metric; do not expose weaknesses unnecessarily; say "technique" and "instructors"; Orvalho et
  al.'s tool is CEGIS; no custom widths; do not expand tool names; keep each section within its guideline's move
  proportions; unknown numbers stay as red `\TODO{...}`.
- Prior work is grouped as alignment-based (CLARA, Sarfgen, Refactory, MENTORED, Verifix), localization-based (Brafar,
  CEGIS, AdaPatcher, infilling), and knowledge-based (AutoGrader, Refazer, LLMs, REFERENT, PyDex, PaR, LSGen); the
  baselines are one per group: Refactory, Brafar, LSGen (GPT-4o).
- Tables and figure data: `python paper/summarize.py` (reads `../output/`, writes `tables.tex` and `numbers.txt` here),
  then `python3 paper/fill_tables.py` (copies the `% rows:<name>` sections of `tables.tex` into `main.tex`).
- Numbers in the text only: `paper/expert_analyze.py` (RQ4 kappa, shares, sign tests), `paper/fixregion.py`
  (Section II-B), `paper/std_effect.py` (RQ3).
- `python3 paper/to_english.py paper/main.tex > main.en.tex` — submission (English-only) source from the Korean draft.
- Build in a scratch copy: `pdflatex → bibtex → pdflatex ×2`, then check `main.log` for `^!|undefined`.
- PDFs (`main.pdf`, `guidelines/*.pdf`) stay local (`.gitignore`).
