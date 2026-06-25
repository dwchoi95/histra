# HISTRA improvement methods — results log

Dev set, same 50-sample uids (sorted). Baselines on these problems:
Refactory p02694=60%/p02659=66%, PaR=54%/40%, orig HISTRA=26%/0%.

| method | k | budget | sample | problems | RR | IP | per-problem |
|---|---|---|---|---|---|---|---|
| loop | 4 | 80 | 30 | p02659,p02694 | 0.0% (0/60) | -- | p02659=0% p02694=0% |
| beam | 4 | 80 | 30 | p02659,p02694 | 23.3% (14/60) | -0.03 | p02659=0% p02694=46% |
