# CLAUDE.md (paper)

This folder is the `paper` branch: only the paper's files, checked out as a git worktree at `<repo>/paper/`. Commit paper
edits here; code goes to `dev` in the parent folder. Branch, repository, and artifact rules: [INIT.md](INIT.md).

## Format

- Follow the venue's template strictly. IEEE: `\documentclass[10pt,conference]{IEEEtran}`, no compsoc, no changes to
  spacing, fonts, or captions (desk-reject risk), so no `caption` package and no custom widths (`\IEEEsetlabelwidth`).
- Everything up to Data Availability fits the page limit; references take their own pages.
- No `\usepackage` that the paper does not use. In the final version, clean up every `\newcommand`/`\renewcommand`
  (write the definition out in the text and delete it); while drafting, the tool name may go through `\tool{}`.
- Unknown numbers stay as red `\TODO{...}`.

## Writing

- Each section follows `guidelines/section/<section>.md`: `skeleton.md` gives the structure, the word proportions, and
  §7 (common rules); `floats.md` covers figures and tables.
- Final review: give review agents only the PDF and `guidelines/review_prompt.md` (the user's own review prompt, used
  verbatim); the procedure (venue criteria, calibration with accepted papers) is in `guidelines/review.md`.
- Draft layout: every paragraph is exactly two lines in `main.tex`: the Korean paragraph on one line, commented out
  with `%`, directly above the English paragraph on one line; a blank line between paragraphs, no line breaks inside a
  paragraph. Floats, math, captions, abbreviations, and key terms stay English.
  `python3 paper/src/to_english.py paper/main.tex > main.en.tex` drops the Korean for submission.
- Workflow: answer in Korean. Revise paragraph by paragraph: show the Korean version first, and once it is confirmed,
  show the English version (then proofread). Propose other changes in Korean first and apply them after approval. For a
  results subsection, review the paragraph flow before the paragraphs.
  Plans list tasks only, never schedules or deadline judgments.
- Style (details in `skeleton.md` §7):
  - Results go float, then numbers per metric, then the conclusion last; no headline sentence.
  - Comparisons are relative "% more/less", one form per metric; no forced statistical tests; no "much/far".
  - Percentages without "N of M" in the Abstract and Introduction.
  - Leave out weaknesses and details the message does not need (the artifact has them); keep the strongest claim the
    data support.
  - One term per concept; abbreviations as "Automated Program Repair (APR)" at their first use in each section; tool
    names cited, not expanded.
  - Tool names, ours and prior work's, in `\textsc{}` everywhere, including table headers and figure labels (all-caps
    names capitalized inside: `\textsc{Clara}`). Metrics and newly defined terms in `\emph{}` where they are defined.
  - Baselines are not named in the Abstract or Introduction; comparisons there say "three state-of-the-art techniques"
    with citations and give results as ranges. The Conclusion repeats the Abstract's claims without numbers.
- Figures: mix graphs into the results (tables only for exact per-item values); floats `[h]`, above their first mention.

## Data and build

- All code for the paper's analyses, tables, and figures lives in `src/` here (or in one `paper.ipynb`), never in `dev`,
  and writes its results to `output/` here. `python paper/src/summarize.py` reads `../output/` and writes
  `output/tables.tex` and `output/numbers.txt`; `python3 paper/src/fill_tables.py` copies the `% rows:<name>` sections
  into the `% rows:<name>` ... `% end rows` blocks of `main.tex`.
- `main.tex` never `\input`s a generated `.tex`: table and plot data are written into `main.tex` itself. The only files
  `main.tex` may reference in `output/` are images (`.png` etc., via `\includegraphics`).
- Build in a scratch copy: `pdflatex → bibtex → pdflatex ×2`, then check `main.log` for `^!|undefined`.
- PDFs (`main.pdf`, `guidelines/*.pdf`) stay local (`.gitignore`).

## This project (HISTRA)

- Target: ICSE-SEET 2027 (criteria: Relevance, Significance, Soundness, Verifiability, Presentation; novelty is not one).
- Macros are cleaned up: the tool name is written as `\textsc{Histra}` (also in `src/summarize.py`'s table labels), and
  the algorithms' Input/Output lines use `\item[\textbf{Input:}]` instead of a redefined `\Require`.
- Prior work is grouped as alignment-based (CLARA, Sarfgen, Refactory, MENTORED, Verifix), localization-based (Brafar,
  CEGIS, AdaPatcher, infilling), and knowledge-based (AutoGrader, Refazer, LLMs, REFERENT, PyDex, PaR, LSGen); the
  baselines are one per group: Refactory, Brafar, LSGen (GPT-4o). Orvalho et al.'s tool is CEGIS. Say "technique" and
  "instructors".
- Numbers in the text only: `src/expert_analyze.py` (RQ4 kappa, shares, sign tests), `src/fixregion.py`
  (Section II-B), `src/std_effect.py` (RQ3).
- `notes/`: mock reviews and the expert-evaluation research behind RQ4.
