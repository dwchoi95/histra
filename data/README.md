# Dataset

Sources:
- Submissions & problems: https://github.com/IBM/Project_CodeNet
- Test cases (AtCoder_testcases.zip): https://github.com/mahimanzum/FixEval#download-test-cases

## Selection criteria
- Language: Python3
- Benchmark: Project_CodeNet_Python800
- Verdicts: AC (Accepted) / WA (Wrong Answer);
- Trajectory: {AC, WA} submissions up to the first AC, with >=2 WA before it (length >=3); last = AC (oracle), last WA = buggy
- Benchmark AC: the trajectory's final AC (oracle) must be one of the Python800 sampled submissions for that problem
- Problems kept: >= 100 trajectories

## Layout
```
data/<problem_id>/
  trajectories.jsonl   {problem_id, user_id, submissions:[{sid, ts, verdict, code}]}
  tests.jsonl          {input, output}
  problem.html         original problem statement
```

## Statistics (final: verdict-reproducible, >= 100 trajectories)
| metric | value |
|---|---|
| problems | 14 |
| trajectories | 1764 |
| submissions | 8696 |
| trajectories per problem (min/median/max) | 101 / 113.0 / 174 |
