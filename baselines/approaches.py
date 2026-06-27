"""Approach dispatcher for run.py -a {histra,refactory,par}.

Every approach exposes the same contract:
    solve(pid, timeout, tests, trajs, refs) -> {user_id: (patch_or_None, seconds)}
where `patch` is a repaired program that PASSES our Validator (None otherwise),
and `seconds` is the per-buggy time. run.py turns this into the unified
results/<pid>/<approach>.csv and results/overall.csv rows.
"""
import time

APPROACHES = ("histra", "histra_llm", "llm_only", "refactory", "par")


def _histra_solve(pid, timeout, tests, trajs, refs):
    from src.core.histra import HISTRA
    h = HISTRA(timeout, tests, refs)
    out = {}
    if hasattr(h, "_pipeline_run") and hasattr(h, "_get_ac_pool"):
        for uid, traj in trajs.items():
            t0 = time.time()
            try:
                patch = h._pipeline_run(traj, h._get_ac_pool(uid))
            except Exception:
                patch = None
            out[uid] = (patch, time.time() - t0)
    else:                                   # fall back to the public API
        t0 = time.time()
        res = h.run(trajs)
        att = (time.time() - t0) / max(len(res), 1)
        out = {uid: (p, att) for uid, p in res.items()}
    return out


def solve(approach, pid, timeout, tests, trajs, refs):
    if approach == "histra":
        return _histra_solve(pid, timeout, tests, trajs, refs)
    if approach == "histra_llm":
        from baselines.histra_llm import solve as hllm_solve
        return hllm_solve(pid, timeout, tests, trajs, refs)
    if approach == "llm_only":
        from baselines.llm_only import solve as llm_only_solve
        return llm_only_solve(pid, timeout, tests, trajs, refs)
    if approach == "par":
        from baselines.par import solve as par_solve
        return par_solve(pid, timeout, tests, trajs, refs)
    if approach == "refactory":
        from baselines.refactory_runner import solve as ref_solve
        return ref_solve(pid, timeout, tests, trajs, refs)
    raise ValueError(f"unknown approach: {approach}")
