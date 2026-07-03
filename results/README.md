# Results layout

Outputs are organized by problem and approach.

```text
results/<pid>/<approach>.csv
results/overall.csv
results/summary.csv
```

`histra.csv` and `refactory.csv` include a `seed` column.
`par.csv`, `partraj.csv`, `hybrid_composed.csv`, and `hybrid_e2e.csv` include
`temperature`, `model`, and `trials` columns, so multiple LLM models and trials
stay in one approach-level CSV.
`hybrid_composed.csv` is the post-hoc HistrA -> PaRTraj cascade built from
already validated `histra.csv` and `partraj.csv` rows.
`hybrid_e2e.csv` is the actual end-to-end cascade produced by running HistrA
first and calling PaRTraj only for HistrA failures.
Both hybrid files include a `source` column (`histra`, `partraj`, or `none`).
The aggregate `overall.csv` and `summary.csv` files include only one extra
`model` column to separate LLM model results.

Patch preservation is split into two columns:

- `ip_last`: the previous `ip` metric, computed against the last wrong answer.
- `ip_traj`: the same metric averaged over every wrong answer in the student's
  trajectory.
