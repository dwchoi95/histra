# HISTRA

Artifact of the paper *HISTRA: Guiding Program Repair for Programming Assignments with Students' Own Submission
Histories*. HISTRA repairs a student's latest wrong-answer submission while keeping the code that the student kept across
their earlier submissions (the *intent skeleton*): it holes the code that the student kept revising (Sketch), retrieves
other students' accepted programs (Search), and merges them into the holes first (Repair). It uses no language model.

## Layout

```text
run.py               run HISTRA (or an RQ3 variant) on the benchmark
src/core/            HISTRA: standardizer, sketch, reformat (projection onto the original code), searcher, merge,
                     repair, minimize, validator, histra (Algorithm 2)
src/experiments/     scripts behind every table, figure, and number of the paper (see below)
  baselines/         Refactory, Brafar, LSGen: setup.sh (upstream commit) and our patch to run them on the benchmark
data.tar.xz          benchmark: 14 AtCoder problems, 1,764 submission trajectories (unpacks into data/)
output.tar.xz        outputs of every technique and the instructors' ratings (unpacks into output/)
```

## Setup

Python 3.13 (3.12+ for the fault-localization control) and `pip install -r requirements.txt`. Unpack the benchmark and the outputs:

```sh
tar -xJf data.tar.xz       # data/: one directory per problem (data/README.md)
tar -xJf output.tar.xz     # output/: approaches/, ablation/, expert/ (output/README.md)
```

## Running HISTRA

```sh
python run.py p02742          # one problem: replaces its rows in output/approaches/histra.jsonl
python run.py                 # every problem (run p02686 alone with -j 4: correct programs take ~1.8 s of its 2 s limit)
python run.py -m nohist       # an RQ3 variant -> output/ablation/nohist.jsonl (modes: src/experiments/histra_eval.py)
```

Each row holds the patch and its metrics (skeleton loss; for HISTRA also Kept and Dist), as described in
`output/README.md`. Measuring takes longer than repairing (tree edit distances to every earlier submission).

## Reproducing the paper

`python src/experiments/summarize.py` reads `output/` and writes `output/summary/tables.tex` (the data of every table and
figure) and `output/summary/numbers.txt` (the numbers in the text).

| Paper | Script (in `src/experiments/`) | Output (`output/summary/`) |
| --- | --- | --- |
| Table I (benchmark) | `summarize.py` | `tables.tex` (bench) |
| Fig. 1, Section II-B | `summarize.py`; `fixregion.py` (code inside and outside the skeleton that the students' fixes change) | `tables.tex` (figlimit*), `numbers.txt` |
| Table II (RQ1) | `run.py`, `run_refactory.py`, `run_brafar.py`, `run_lsgen.py run`, then `summarize.py` | `tables.tex` (rq1), `numbers.txt` |
| Fig. 4 (RQ2) | the same runs, then `summarize.py` | `tables.tex` (figclose*), `numbers.txt` |
| Table III (RQ3) | `run.py -m MODE` for each variant and control, then `summarize.py`; `std_effect.py` | `tables.tex` (rq2), `numbers.txt` |
| Fig. 5 (RQ4) | `expert_analyze.py` (shares, sign tests, agreement), `summarize.py` | `tables.tex` (figexp*) |

To rerun every experiment:

```sh
for m in min nostd nohole nokept plain sizemin nohist randfrac fl; do python run.py -m $m; done
for s in 0 1 2; do HSEED=$s python run.py -m randhole; done
sh src/experiments/baselines/refactory/setup.sh && python src/experiments/run_refactory.py
sh src/experiments/baselines/brafar/setup.sh && POOL=4 python src/experiments/run_brafar.py
sh src/experiments/baselines/lsgen/setup.sh && CODENET=<Project_CodeNet> python src/experiments/run_lsgen.py prep \
  && OPENAI_API_KEY=<key> python src/experiments/run_lsgen.py run --batch --submit
python src/experiments/summarize.py
```

Environment variables of the scripts: `ONLY=p02742,...` restricts the problems, `POOL` sets the worker processes
(default 16), and `PER=k` samples k trajectories per problem. Tests that run close to their time limit (p02686) can time
out under load, so run them on an otherwise idle machine; `RERUN=<rows.jsonl> python src/experiments/run_brafar.py`
reruns the given rows.

## License

The code is released under the MIT License. The benchmark is derived from Project CodeNet and the FixEval test cases
(`data/README.md`). The baselines' patches apply to their upstream code under the upstream licenses.
