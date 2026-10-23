# HISTRA

Artifact of *HISTRA: Guiding Program Repair for Programming Assignments with Students' Own Submission Histories*.
HISTRA repairs a student's latest wrong-answer submission while keeping the code that the student kept across their
earlier submissions, using other students' accepted programs and no language model.

## Dataset

data.tar.xz : The benchmark of 14 AtCoder problems (1,764 submission trajectories) from Project CodeNet, with the test
cases from FixEval.

```text
|-data
    |-pxxxxx
    |    |-trajectories.jsonl
    |    |-tests.jsonl
    |    |-problem.html
    |    |-meta.json
    |-...
```

> pxxxxx : Folder of an AtCoder problem.  
> trajectories.jsonl : One trajectory per line: a student's wrong-answer submissions, then their first accepted one.  
> tests.jsonl : Test cases (input and expected output).  
> problem.html : Problem statement.  
> meta.json : Time and memory limits.  

output.tar.xz : The results of HISTRA, the baselines, the ablation, and the expert evaluation.

```text
|-output
    |-approaches
    |    |-histra.jsonl
    |    |-refactory.jsonl
    |    |-brafar.jsonl
    |    |-lsgen.jsonl
    |-ablation
    |    |-{mode}.jsonl
    |    |-...
    |-expert
         |-ratings.csv
```

> approaches : Patches and metrics of HISTRA and the baselines, one line per trajectory.  
> {mode}.jsonl : Patches and metrics of an ablation mode (see Command Line Arguments).  
> ratings.csv : The instructors' choices between the patches of HISTRA and of HISTRA without the history.  

## Setup

1. Environment
   `python >= 3.12`
2. Install library

   ```sh
   pip install -r requirements.txt
   ```
3. Set the OpenAI API key for the LSGen baseline (option)

   ```sh
   export OPENAI_API_KEY=<your openai api key>
   ```
4. Unzip Dataset

   ```sh
   tar -xJf data.tar.xz
   tar -xJf output.tar.xz
   ```

## How to Run

+ Run single problem
  ```sh
  python run.py p02742
  ```
+ Run all problems (run p02686 alone with `-j 4`: its tests are close to the time limit)
  ```sh
  python run.py
  ```
+ Run an ablation mode
  ```sh
  python run.py -m nohist
  ```
+ Run the baselines
  ```sh
  sh src/experiments/baselines/refactory/setup.sh && python src/experiments/run_refactory.py
  sh src/experiments/baselines/brafar/setup.sh && POOL=4 python src/experiments/run_brafar.py
  sh src/experiments/baselines/lsgen/setup.sh && CODENET=<Project_CodeNet> python src/experiments/run_lsgen.py prep
  python src/experiments/run_lsgen.py run --batch --submit
  ```

## Command Line Arguments

`python run.py [PROBLEM ...] [-m MODE] [-j WORKERS]`

| Argument | Description |
| --- | --- |
| `PROBLEM ...` | problem ids under `data/` (default: all) |
| `-m`, `--mode` | `min` (HISTRA, default) or an ablation mode below |
| `-j`, `--workers` | worker processes (default: 16) |

| Mode | Ablation |
| --- | --- |
| `nostd` | without normalization (HISTRA-Norm) |
| `nohole` | without the hole-only phase (HISTRA-Hole) |
| `nokept` | without the Kept order (HISTRA-Kept) |
| `plain` | without minimization (HISTRA-Min) |
| `sizemin` | minimization ordered by subtree size only |
| `nohist` | without the history (H = {}) |
| `randhole` | random holes matched to the history's in number, kind, and size (`HSEED=0,1,2`) |
| `randfrac` | random holes covering 48.5% of the nodes |
| `fl` | holes from spectrum-based fault localization |

## Project Structure

```text
histra/
├── data.tar.xz           # Benchmark (see Dataset)
├── output.tar.xz         # Results (see Dataset)
├── src/
│   ├── core/             # HISTRA: Sketch, Search, Repair
│   └── experiments/      # Ablation modes, metrics, baseline runners
│       └── baselines/    # Baseline setup scripts and our patches
├── run.py                # Main entry point
└── requirements.txt      # Python dependencies
```
