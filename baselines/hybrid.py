"""End-to-end HistrA -> PaRTraj cascade.

The composed hybrid results can be obtained post-hoc from existing HistrA and
PaRTraj CSVs. This module runs the same policy end to end: execute HistrA first,
then call PaRTraj only for submissions HistrA did not repair.

solve(pid, timeout, tests, trajs, refs) -> {user_id: (patch_or_None, seconds, source)}
where source is one of {"histra", "partraj", "none"}.
"""

import csv
import os

from src.core.histra import solve as histra_solve
from baselines.par import solve as par_solve


def _load_cached_histra(pid, trajs):
    root = os.environ.get("HYBRID_HISTRA_CACHE_ROOT", "").strip()
    if not root:
        return None
    path = os.path.join(root, pid, "histra.csv")
    if not os.path.exists(path):
        if os.environ.get("HYBRID_REQUIRE_HISTRA_CACHE") == "1":
            raise FileNotFoundError(f"missing cached HistrA result: {path}")
        return None

    by_uid = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            uid = row.get("user_id")
            if not uid:
                continue
            fixed = str(row.get("fixed", "")).strip() in {"1", "1.0", "true", "True"}
            patch = row.get("patch") if fixed else None
            try:
                secs = float(row.get("att", 0.0) or 0.0)
            except ValueError:
                secs = 0.0
            by_uid[uid] = (patch, secs)
    return {uid: by_uid.get(uid, (None, 0.0)) for uid in trajs}


def solve(pid, timeout, tests, trajs, refs):
    histra_results = _load_cached_histra(pid, trajs)
    if histra_results is None:
        histra_results = histra_solve(timeout, tests, trajs, refs)
    failed_trajs = {
        uid: trajs[uid]
        for uid, (patch, _secs) in histra_results.items()
        if not patch and uid in trajs
    }

    partraj_results = {}
    if failed_trajs:
        partraj_results = par_solve(
            pid, timeout, tests, failed_trajs, refs, use_traj=True
        )

    out = {}
    for uid in trajs:
        h_patch, h_secs = histra_results.get(uid, (None, 0.0))
        if h_patch:
            out[uid] = (h_patch, h_secs, "histra")
            continue

        p_patch, p_secs = partraj_results.get(uid, (None, 0.0))
        source = "partraj" if p_patch else "none"
        out[uid] = (p_patch, h_secs + p_secs, source)
    return out
