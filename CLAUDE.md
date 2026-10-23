# CLAUDE.md (paper)

This folder is the `paper` branch: only the paper's files, checked out as a git worktree at `<repo>/paper/`. Commit paper
edits here; code goes to `dev` in the parent folder. Branch, repository, and artifact rules: [INIT.md](INIT.md).

## Format

- Follow the venue's template strictly. IEEE: `\documentclass[10pt,conference]{IEEEtran}`, no compsoc, no changes to
  spacing, fonts, or captions (desk-reject risk), so no `caption` package and no custom widths (`\IEEEsetlabelwidth`).
- Everything up to Data Availability fits the page limit; references take their own pages.
- Tool name via `\tool{}`; unknown numbers stay as red `\TODO{...}`.

## Writing

- Each section follows `guidelines/section/<section>.md`: `skeleton.md` gives the structure, the word proportions, and
  §7 (common rules); `floats.md` covers figures and tables.
- Final review: give review agents only the PDF and `guidelines/review_prompt.md` (the user's own review prompt, used
  verbatim); the procedure (venue criteria, calibration with accepted papers) is in `guidelines/review.md`.
- Draft layout: each paragraph in Korean (commented out with `%`) directly above its live English version; floats, math,
  captions, abbreviations, and key terms stay English. `python3 paper/src/to_english.py paper/main.tex > main.en.tex`
  drops the Korean for submission.
- Workflow: answer in Korean. Propose each change in Korean first and apply it after approval. Revise paragraph by
  paragraph (Korean, approval, English, proofreading); for a results subsection, review the paragraph flow first.
  Plans list tasks only, never schedules or deadline judgments.
- Style (details in `skeleton.md` §7):
  - Results go float, then numbers per metric, then the conclusion last; no headline sentence.
  - Comparisons are relative "% more/less", one form per metric; no forced statistical tests; no "much/far".
  - Percentages without "N of M" in the Abstract and Introduction.
  - Leave out weaknesses and details the message does not need (the artifact has them); keep the strongest claim the
    data support.
  - One term per concept; abbreviations defined at their first use in each section; tool names cited, not expanded.
  - Baselines are not named in the Abstract or Introduction; comparisons there say "three state-of-the-art techniques"
    with citations and give results as ranges. The Conclusion repeats the Abstract's claims without numbers.
- Figures: mix graphs into the results (tables only for exact per-item values); floats `[h]`, above their first mention.

## Data and build

- All code for the paper's analyses, tables, and figures lives in `src/` here (or in one `paper.ipynb`), never in `dev`.
  `python paper/src/summarize.py` reads `../output/` and writes `tables.tex` and `numbers.txt` next to `main.tex`;
  `python3 paper/src/fill_tables.py` fills the `% rows:<name>` ... `% end rows` blocks of `main.tex`.
- Build in a scratch copy: `pdflatex → bibtex → pdflatex ×2`, then check `main.log` for `^!|undefined`.
- PDFs (`main.pdf`, `guidelines/*.pdf`) stay local (`.gitignore`).

## This project (HISTRA)

- Target: ICSE-SEET 2027 (criteria: Relevance, Significance, Soundness, Verifiability, Presentation; novelty is not one).
- Prior work is grouped as alignment-based (CLARA, Sarfgen, Refactory, MENTORED, Verifix), localization-based (Brafar,
  CEGIS, AdaPatcher, infilling), and knowledge-based (AutoGrader, Refazer, LLMs, REFERENT, PyDex, PaR, LSGen); the
  baselines are one per group: Refactory, Brafar, LSGen (GPT-4o). Orvalho et al.'s tool is CEGIS. Say "technique" and
  "instructors".
- Numbers in the text only: `src/expert_analyze.py` (RQ4 kappa, shares, sign tests), `src/fixregion.py`
  (Section II-B), `src/std_effect.py` (RQ3).
- `notes/`: mock reviews and the expert-evaluation research behind RQ4.
