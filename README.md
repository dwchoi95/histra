# HISTRA

## Installation

Requires **Python 3.13**.

```bash
python -m venv env
source env/bin/activate            # Windows: env\Scripts\activate
pip install -r requirements.txt    # apted, numpy, tqdm, prettytable
```

Baselines need extra setup (not required for HISTRA):

- **PaR / partraj** (LLM baselines) read an OpenAI key from `baselines/.env`:
  `OPENAI_API_KEY=<your key>`.
- **Refactory** runs in its own Python 3.8 environment under
  `baselines/refactory/`; local modifications are mirrored in
  `baselines/refactory_mods/`.

## Usage

Run from the repository root (imports use the `src.` prefix, so the repo root
must be the working directory):

```bash
python run.py -d data                    # HISTRA (default) on every problem
python run.py -d data -a histra          # our approach, explicitly
python run.py -d data -a refactory       # Refactory baseline
python run.py -d data -a par             # PaR baseline (needs OPENAI_API_KEY)
python run.py -d data/p02686             # a single problem
python run.py -d data -a histra -r       # recompute even if results exist
```

Flags:

| flag | meaning |
|------|---------|
| `-d, --dataset` | dataset directory of `data/<pid>/` problems (**required**) |
| `-a, --approach` | `histra` (default) `\| refactory \| par \| partraj \| hybrid_e2e` |
| `-r, --reset` | recompute even if the output CSV already exists |
| `-j, --jobs` | number of problem processes to run at once |
| `-o, --out-root` | output directory (default `results`) |
| `--model` | LLM model for `par` / `partraj` |
| `--seed` | seed for reproducible non-LLM sampling (default `0`) |

**Output.** Each problem writes `results/<pid>/<approach>.csv`
(`user_id,buggy,patch,oracle,fixed,ted,ip,att`); all processes update the shared
`results/overall.csv` and `results/summary.csv`.

## Layout

- `run.py` — CLI entry point (one process per problem)
- `src/core/` — pipeline stages: `standardizer` → `sketch` → `reformat` →
  `searcher` → `repair` / `mutator` → `validator`, orchestrated by `histra.py`
- `src/utils/` — data loader, tree-edit-distance metrics, AST helpers
- `baselines/` — baseline approaches (`par`, `refactory_runner`, `hybrid`) and
  the `approaches.py` dispatcher
- `data/` — evaluation dataset, one `data/<pid>/` per problem
  (see `data/README.md` for the benchmark and schema)
- `results/` — precomputed results (`overall.csv`, `summary.csv`, and
  per-problem patch CSVs)
