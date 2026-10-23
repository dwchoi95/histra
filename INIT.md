# INIT.md — repository, branch, and artifact rules

Rules for a research repository that holds the code, the public artifact, and the paper. To start a new project, copy
this file, `CLAUDE.md`, and `guidelines/` into the new project's `paper` branch (the analyzed PDFs in `guidelines/` are
not committed; copy them by hand).

## Branches

| Branch | Holds | Notes |
| --- | --- | --- |
| `main` | the public artifact, one orphan commit | mirrored by anonymous.4open.science for double-blind review |
| `dev` | development, every commit | no trace of `paper/`: no file, no `.gitignore` line, no mention |
| `paper` | the paper's files only, at the branch root | checked out as a worktree at `<repo>/paper/` |

- One working folder: `<repo>/` is on `dev`, `<repo>/paper/` is the `paper` worktree. No second clone or sibling folder.
- Commit code in `<repo>/` and the paper inside `<repo>/paper/`. All code for the paper's analyses, tables, and figures
  (table and figure data, numbers in the text) lives in the paper branch, in `paper/src/` or in one `paper.ipynb`, and
  reads `../output/`; `dev` and `main` keep none of it.
- Paper branch layout:

  ```text
  paper/
  ├── main.tex, references.bib   # Manuscript
  ├── src/                       # Analyses, tables, figures (or one paper.ipynb); results go to output/
  ├── output/                    # tables.tex, numbers.txt, figure images; main.tex includes only the images
  ├── guidelines/                # Section guidelines, review.md, review_prompt.md (the final review prompt)
  ├── notes/                     # Mock reviews, research notes
  ├── CLAUDE.md
  ├── INIT.md
  └── .gitignore                 # *.pdf and LaTeX build files
  ```
- Set up the paper branch once (git ≥ 2.23):

  ```sh
  git worktree add --detach paper
  cd paper && git switch --orphan paper     # empty worktree on a new orphan branch
  # add the paper files at the root (layout below)
  git add -A && git commit -m "Paper" && cd ..
  echo /paper/ >> .git/info/exclude         # hides paper/ from dev and main without a .gitignore line
  ```

- `main` = `dev` minus dev-only files (`tests/`, `CLAUDE.md`) and internal safety devices (spending caps, idle waits,
  rechecks). Never check it out; rebuild it after committing to dev:
  `GIT_INDEX_FILE=<tmp> git read-tree dev`, `git rm -r --cached tests CLAUDE.md`, take main's versions of the files that
  differ (`git update-index --cacheinfo 100644,$(git rev-parse main:<f>),<f>`), `git write-tree`,
  `git commit-tree <tree>` without a parent, `git update-ref refs/heads/main <commit>`.
- Pushing is always confirmed with the user first; `main` is force-pushed. Delete a stale branch only after its commits are
  in `dev`. Keep `main`, `dev`, and `paper` only.

## Repository layout (`dev`; `main` without the dev-only entries)

```text
<repo>/
├── data.tar.xz           # Dataset; unpacks into data/ (README.md inside)
├── output.tar.xz         # Results reported in the paper; unpacks into output/ (README.md inside)
├── src/
│   ├── core/             # The technique
│   └── experiments/      # Run modes, metrics, baseline runners
│       └── baselines/    # <tool>/setup.sh (pinned upstream commit) and our patch
├── tests/                # Regression checks (dev only)
├── run.py                # Main entry point
├── requirements.txt      # Only the packages the code imports
├── README.md
├── LICENSE
└── CLAUDE.md             # Guidance for Claude Code (dev only)
```

- Local only (git-ignored, never deleted without asking): `results/` (every experiment ever run, old datasets, raw logs,
  rating kits), `baselines/` (forks), notebooks, `.env`.
- `output/` holds only what the paper reports, by role: `approaches/` (our technique and the baselines), `ablation/`,
  `expert/` (human ratings). One `<name>.jsonl` per technique, one row per item; each row carries its metrics, written by
  `run.py` and the baseline runners. Paper-only summaries (tables, numbers) are generated in the paper branch, not here.
- Pack whole folders, README inside, as `<folder>.tar.xz` at the root (the anonymous mirror takes at most 60 MB per
  repository and 100 MB per file):
  `COPYFILE_DISABLE=1 tar --format=ustar --uid 0 --gid 0 --uname root --gname root -n -cf - <sorted file list> | xz -9e`.
  Check that the archive round-trips before committing it.

## Artifact hygiene

- No names, accounts, local paths, dates, machine names, or process notes (reruns, budgets, idle waits) in `main`.
- Comments only for a non-obvious why; docstrings one line where the name does not say it.
- Secrets only in `.env` (git-ignored); never print, log, commit, or copy keys to another machine.
- Baselines run from their upstream code at a pinned commit plus our patch, which adapts input and output only; the
  adaptation is not described in the paper or the README.

## README (`main`)

Title and one sentence, then:

1. **Dataset:** one line per archive (`data.tar.xz : ...`), a `|-` tree of its contents, and a `>` legend of the entries.
2. **Setup:** numbered steps — environment (`python >= 3.x`), `pip install -r requirements.txt`, API keys (option),
   unpacking the archives.
3. **How to Run:** `+` bullets, each with a command block (one problem, all problems, a mode, the baselines).
4. **Command Line Arguments:** tables of `run.py` arguments and modes.
5. **Project Structure:** a `├──` tree with `#` comments.

## Experiments

- Heavy runs go to the server. Never run other CPU-heavy work beside a run that validates tests (timeouts flip results).
- Use the full benchmark rather than samples and the baselines' public implementations rather than reimplementations.
- Long runs survive a closed session: `nohup caffeinate -is sh <script> &` (macOS).
