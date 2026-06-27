"""Trajectory-aware intent-preservation metrics.

The committed IP anchors at the LAST WA only, which favours methods that minimally
edit the last submission (PaR/Refactory). These variants measure preservation
against the WHOLE trajectory (all WA submissions), per the project's premise that
intent is what the student expressed consistently across attempts.

Given the full WA trajectory `traj` (list of code strings, earliest->latest), the
`patch`, and the student's own AC `oracle`:

  ip_mean(traj, patch, oracle):
      D_x = mean_i TED(x, WA_i);  IP = (D_oracle - D_patch)/(D_oracle + D_patch)
      Generalises the current metric (n=1 -> identical). Higher = the patch stays
      closer to the student's whole set of attempts than the oracle does.

  ip_recency(traj, patch, oracle):
      same, but weight w_i = i (later attempts count more — intent converges).

  ip_stable(traj, patch):
      S = statements present in ALL parseable WAs (the consistently-written
      "intent"); returns |S ∩ patch| / |S|. Oracle-free, model-agnostic.
"""
import ast
from functools import lru_cache
from src.utils.metrics import ted as _ted


@lru_cache(maxsize=200000)
def _ted_cached(a, b):
    t = _ted(a, b)
    return t


def _agg_dist(x, traj, weights):
    ds, ws = [], []
    for code, w in zip(traj, weights):
        t = _ted_cached(x, code)
        if t is not None:
            ds.append(t * w); ws.append(w)
    if not ws:
        return None
    return sum(ds) / sum(ws)


def _ip_from_dists(traj, patch, oracle, weights):
    if not traj or not patch or not oracle:
        return None
    dp = _agg_dist(patch, traj, weights)
    do = _agg_dist(oracle, traj, weights)
    if dp is None or do is None:
        return None
    s = dp + do
    return (do - dp) / s if s else 0.0


def ip_mean(traj, patch, oracle):
    return _ip_from_dists(traj, patch, oracle, [1.0] * len(traj))


def ip_recency(traj, patch, oracle):
    return _ip_from_dists(traj, patch, oracle, [i + 1 for i in range(len(traj))])


def _stmt_set(code):
    try:
        tree = ast.parse(code)
    except Exception:
        return None
    out = set()
    for s in ast.walk(tree):
        if isinstance(s, ast.stmt):
            try:
                out.add(ast.unparse(s).strip())
            except Exception:
                pass
    return out


def ip_stable(traj, patch):
    if not traj or not patch:
        return None
    sets = [s for s in (_stmt_set(c) for c in traj) if s]
    if not sets:
        return None
    stable = set.intersection(*sets)
    if not stable:
        return None
    ps = _stmt_set(patch)
    if ps is None:
        return None
    return len(stable & ps) / len(stable)
