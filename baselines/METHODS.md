# HISTRA improvement methods — results log

Dev set, same 50-sample uids (sorted). Baselines on these problems:
Refactory p02694=60%/p02659=66%, PaR=54%/40%, orig HISTRA=26%/0%.

| method | k | budget | sample | problems | RR | IP | per-problem |
|---|---|---|---|---|---|---|---|
| loop | 4 | 80 | 30 | p02659,p02694 | 0.0% (0/60) | -- | p02659=0% p02694=0% |
| beam | 4 | 80 | 30 | p02659,p02694 | 23.3% (14/60) | -0.03 | p02659=0% p02694=46% |
| beam | 4 | 80 | 30 | p02659,p03324,p02823,p02694 | 15.0% (18/120) | +0.01 | p02659=0% p03324=3% p02823=10% p02694=46% |
| coherent | 4 | 80 | 30 | p02659,p03324,p02823,p02694 | 41.7% (50/120) | -0.32 | p02659=3% p03324=50% p02823=56% p02694=56% |
| cascade | 4 | 80 | 30 | p02659,p03324,p02823,p02694 | 41.7% (50/120) | -0.31 | p02659=3% p03324=50% p02823=56% p02694=56% |
