"""Baseline dispatcher for run.py -a {refactory,par,partraj,hybrid_e2e}.

Every approach exposes the same contract:
    solve(pid, timeout, tests, trajs, refs) -> {user_id: (patch_or_None, seconds)}
where `patch` is a repaired program that PASSES our Validator (None otherwise),
and `seconds` is the per-buggy time. run.py turns this into the unified
results/<pid>/<approach>.csv and results/overall.csv rows.
"""

APPROACHES = ("partraj", "refactory", "par", "hybrid_e2e")


def solve(approach, pid, timeout, tests, trajs, refs):
    if approach == "partraj":   # PaR + Trajectory (same model/peer/validation as par)
        from baselines.par import solve as par_solve
        return par_solve(pid, timeout, tests, trajs, refs, use_traj=True)
    if approach == "par":
        from baselines.par import solve as par_solve
        return par_solve(pid, timeout, tests, trajs, refs)
    if approach == "refactory":
        from baselines.refactory_runner import solve as ref_solve
        return ref_solve(pid, timeout, tests, trajs, refs)
    if approach == "hybrid_e2e":
        from baselines.hybrid import solve as hybrid_solve
        return hybrid_solve(pid, timeout, tests, trajs, refs)
    raise ValueError(f"unknown approach: {approach}")
