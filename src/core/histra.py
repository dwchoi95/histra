from __future__ import annotations

import ast
import copy
import os
import signal
import time
from contextlib import contextmanager
from multiprocessing import Process, Queue
from typing import Dict
from tqdm import tqdm

from .validator import Validator
from src.types import Status
from .standardizer import Standardizer
from .sketch import Sketcher
from .reformat import Reformatter
from .searcher import Searcher
from .repair import Repair
from .mutator import LocalMutator
from src.utils import metrics as _metrics

class HISTRA:
    DEFAULT_LOCAL_TIME_BUDGET = 8.0
    DEFAULT_FALLBACK_TIME_BUDGET = 12.0
    DEFAULT_FALLBACK_RANKS = 8
    DEFAULT_FALLBACK_PREFILTER = 60
    DEFAULT_FALLBACK_MAX_HOLE_STMTS = 10
    DEFAULT_LOCAL_CANDIDATES = 180
    DEFAULT_LOCAL_LOOKAHEAD = 16
    DEFAULT_LOCAL_GENERAL_ONLY = True
    DEFAULT_LOCAL_USE_REFS = True
    DEFAULT_LOCAL_USE_HISTORY_SOURCES = True

    def __init__(
        self,
        timeout,
        tests,
        refs,
        local_time_budget: float | None = None,
        fallback_time_budget: float | None = None,
        fallback_rank_budget: int | None = None,
        fallback_prefilter: int | None = None,
        fallback_max_ted: float | None = None,
        fallback_cluster_mode: str | None = None,
        fallback_cluster_threshold: float | None = None,
        fallback_max_hole_stmts: int | None = None,
        diffuse_local_time_budget: float | None = None,
        local_candidate_budget: int | None = None,
        local_lookahead: int | None = None,
        local_general_only: bool | None = None,
        local_use_refs: bool | None = None,
        local_use_history_sources: bool | None = None,
    ):
        self.refs = refs
        self._test_order = None
        self.local_time_budget = self._float_opt(
            local_time_budget,
            "HISTRA_LOCAL_TIME_BUDGET",
            self.DEFAULT_LOCAL_TIME_BUDGET,
        )
        self.fallback_time_budget = self._float_opt(
            fallback_time_budget,
            "HISTRA_FALLBACK_TIME_BUDGET",
            self.DEFAULT_FALLBACK_TIME_BUDGET,
        )
        self.fallback_rank_budget = self._int_opt(
            fallback_rank_budget,
            "HISTRA_FALLBACK_RANKS",
            self.DEFAULT_FALLBACK_RANKS,
        )
        self.fallback_prefilter = self._int_opt(
            fallback_prefilter,
            "HISTRA_FALLBACK_PREFILTER",
            self.DEFAULT_FALLBACK_PREFILTER,
        )
        self.fallback_max_ted = self._float_opt(
            fallback_max_ted, "HISTRA_FALLBACK_MAX_TED")
        self.fallback_cluster_mode = self._str_opt(
            fallback_cluster_mode, "HISTRA_FALLBACK_CLUSTER")
        self.fallback_cluster_threshold = self._float_opt(
            fallback_cluster_threshold, "HISTRA_FALLBACK_CLUSTER_THRESHOLD") or 0.45
        self.fallback_max_hole_stmts = self._int_opt(
            fallback_max_hole_stmts,
            "HISTRA_FALLBACK_MAX_HOLE_STMTS",
            self.DEFAULT_FALLBACK_MAX_HOLE_STMTS,
        )
        self.diffuse_local_time_budget = self._float_opt(
            diffuse_local_time_budget, "HISTRA_DIFFUSE_LOCAL_TIME_BUDGET")
        self.local_candidate_budget = self._int_opt(
            local_candidate_budget,
            "HISTRA_LOCAL_CANDIDATES",
            self.DEFAULT_LOCAL_CANDIDATES,
        )
        self.local_lookahead = self._int_opt(
            local_lookahead,
            "HISTRA_LOCAL_LOOKAHEAD",
            self.DEFAULT_LOCAL_LOOKAHEAD,
        )
        self.local_general_only = self._bool_opt(
            local_general_only,
            "HISTRA_LOCAL_GENERAL_ONLY",
            self.DEFAULT_LOCAL_GENERAL_ONLY,
        )
        self.local_use_refs = self._bool_opt(
            local_use_refs,
            "HISTRA_LOCAL_USE_REFS",
            self.DEFAULT_LOCAL_USE_REFS,
        )
        self.local_use_history_sources = self._bool_opt(
            local_use_history_sources,
            "HISTRA_LOCAL_USE_HISTORY_SOURCES",
            self.DEFAULT_LOCAL_USE_HISTORY_SOURCES,
        )
        self.last_trace = self._new_trace()
        Validator.init_globals(tests, timeout)
    
    def _get_ac_pool(self, user_id):
        # 간단/안전: 사본에서 해당 사용자만 제거하고 남은 코드 리스트 반환
        d = self.refs.copy()
        d.pop(user_id, None)
        return list(d.values())
    
    def _has_hole(self, node: ast.AST) -> bool:
        return any(getattr(n, "_hole", False) for n in ast.walk(node))

    # ---- Static helpers for multiprocessing-safe execution ----
    def _pipeline_run(self, traj: list[str], refs: list[str]) -> str | None:
        self.last_trace = self._new_trace()
        total_start = time.time()
        try:
            buggy = traj[-1] if traj else ""
            order_start = time.time()
            self._test_order = self._failing_first_order(traj[-1]) if traj else None
            self.last_trace["test_order_time"] = time.time() - order_start

            # 1. Standardize: 모든 WA를 동일 규칙으로 정규화 (문자열) + WAn(AST, provenance)
            phase_start = time.time()
            std_traj = Standardizer.run(traj)
            anchor = std_traj[-1]
            self.last_trace["standardize_time"] = time.time() - phase_start

            # 2. Sketch: 변형된 부분만 __HOLE_k__ 처리 (canonical space)
            phase_start = time.time()
            skt_std = Sketcher.run(std_traj)
            self.last_trace["sketch_time"] = time.time() - phase_start

            # 3. Reformat: Sketch 결과(holes/insert_entries)를 원래 표면으로 투영
            phase_start = time.time()
            skt_org = Reformatter.run(anchor, skt_std)
            self.last_trace["reformat_time"] = time.time() - phase_start
            self.last_trace["holes"] = sum(
                1 for node in ast.walk(skt_org) if getattr(node, "_hole", False))
            self.last_trace["hole_stmts"] = self._hole_stmt_count(skt_org)

            # 4. First try localized, history-aware edits around changed regions.
            local_start = time.time()
            mutator_kwargs = {}
            if self.local_candidate_budget is not None:
                mutator_kwargs["max_candidates"] = self.local_candidate_budget
            if self.local_general_only:
                mutator_kwargs["general_only"] = True
            mutator_kwargs["use_refs"] = self.local_use_refs
            mutator_kwargs["use_history_sources"] = self.local_use_history_sources
            mutator = LocalMutator(traj, refs, skt_org, **mutator_kwargs)
            self.last_trace["local_build_time"] = time.time() - local_start
            local_budget = self._local_budget_for_case()
            self.last_trace["local_budget"] = local_budget if local_budget is not None else ""
            patch = self._local_best_passing(
                buggy,
                mutator.generate(),
                lookahead=self.local_lookahead,
                start_time=local_start,
                budget=local_budget,
            )
            self.last_trace["local_time"] = time.time() - local_start
            if patch:
                self.last_trace["result_source"] = "local"
                return patch

            # 5-7. Fallback: Search top-k refs, repair, validate, then choose the
            # first passing patch. Local candidates above are ordered by edit size,
            # so they are the main intent-preserving path.
            if self.fallback_rank_budget == 0:
                self.last_trace["fallback_skipped"] = 1
                self.last_trace["fallback_skip_reason"] = "rank_budget"
                return None
            if self._diffuse_sketch():
                self.last_trace["fallback_skipped"] = 1
                self.last_trace["fallback_skip_reason"] = "diffuse_sketch"
                return None
            fallback_start = time.time()
            self.last_trace["fallback_prefilter"] = self.fallback_prefilter or ""
            self.last_trace["fallback_max_ted"] = self.fallback_max_ted or ""
            self.last_trace["fallback_cluster"] = self.fallback_cluster_mode or ""
            searcher = Searcher(
                refs,
                anchor,
                top_k=self.fallback_rank_budget or 10,
                prefilter_k=self.fallback_prefilter,
                hole_only=True,
                cluster_mode=self.fallback_cluster_mode,
                cluster_threshold=self.fallback_cluster_threshold,
            )
            rank_limit = len(searcher)
            if self.fallback_rank_budget is not None:
                rank_limit = min(rank_limit, self.fallback_rank_budget)
            for rank in range(rank_limit):
                if self._budget_exceeded(fallback_start, self.fallback_time_budget):
                    self.last_trace["fallback_timed_out"] = 1
                    break
                self.last_trace["fallback_ranks"] += 1
                candidate = copy.deepcopy(skt_org)
                node_map, var_map = searcher.run(candidate, rank)
                self.last_trace["fallback_clusters"] = searcher.cluster_count
                self.last_trace["fallback_cluster_size"] = searcher.selected_cluster_size
                if not node_map:
                    continue

                mod = Repair(node_map, var_map)
                repaired = mod.run(candidate)
                patch = ast.unparse(repaired)
                if self._passes(patch, phase="fallback"):
                    patch_ted = _metrics.ted(buggy, patch)
                    if (
                        self.fallback_max_ted is not None
                        and patch_ted is not None
                        and patch_ted > self.fallback_max_ted
                    ):
                        self.last_trace["fallback_rejected"] += 1
                        continue
                    self.last_trace["fallback_best_ted"] = patch_ted
                    self.last_trace["fallback_time"] = time.time() - fallback_start
                    self.last_trace["result_source"] = "fallback"
                    return patch

            self.last_trace["fallback_time"] = time.time() - fallback_start
            return None
        finally:
            self.last_trace["total_time"] = time.time() - total_start

    def _local_best_passing(
        self,
        buggy: str,
        candidates,
        lookahead: int,
        start_time: float,
        budget: float | None,
    ) -> str | None:
        seen = set()
        best_patch = None
        best_score = None
        after_first = 0
        for patch in candidates:
            if self._budget_exceeded(start_time, budget):
                self.last_trace["local_timed_out"] = 1
                break
            if not patch or patch in seen:
                continue
            seen.add(patch)
            self.last_trace["local_candidates"] += 1
            if not self._passes(patch, phase="local"):
                if best_patch is not None:
                    after_first += 1
                if best_patch is not None and after_first >= lookahead:
                    break
                continue
            score = _metrics.ted(buggy, patch)
            score = score if score is not None else float("inf")
            if best_score is None or score < best_score:
                best_score = score
                best_patch = patch
                self.last_trace["local_best_ted"] = score
            self.last_trace["local_passes"] += 1
            if self.last_trace["local_first_pass_at"] == 0:
                self.last_trace["local_first_pass_at"] = self.last_trace["local_candidates"]
            after_first += 1
            if after_first >= lookahead:
                break
        return best_patch

    def _passes(self, patch: str, phase: str | None = None) -> bool:
        if phase:
            key = f"{phase}_validations"
            self.last_trace[key] = self.last_trace.get(key, 0) + 1
        try:
            if self._test_order:
                return Validator.run_failfast_ordered(patch, self._test_order).passed()
            return Validator.run_failfast(patch).passed()
        except Exception:
            return False

    def _failing_first_order(self, code: str) -> tuple[int, ...] | None:
        try:
            n_tests = len(Validator.tests)
            for idx, testcase in enumerate(Validator.tests):
                tr = Validator._validation((code, testcase))
                if tr.result is None or tr.result.status != Status.PASSED:
                    rest = tuple(i for i in range(n_tests) if i != idx)
                    return (idx,) + rest
        except Exception:
            return None
        order = tuple(range(len(Validator.tests)))
        return order or None

    @staticmethod
    def _hole_stmt_count(tree: ast.AST) -> int:
        return sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.stmt)
            and any(getattr(child, "_hole", False) for child in ast.walk(node))
        )

    def _local_budget_for_case(self) -> float | None:
        budget = self.local_time_budget
        if (
            self.diffuse_local_time_budget is not None
            and self._diffuse_sketch()
            and (budget is None or budget > self.diffuse_local_time_budget)
        ):
            return self.diffuse_local_time_budget
        return budget

    def _diffuse_sketch(self) -> bool:
        limit = self.fallback_max_hole_stmts
        return limit is not None and self.last_trace["hole_stmts"] > limit

    @staticmethod
    def _float_opt(value, env_name: str, default: float | None = None) -> float | None:
        if value is not None:
            return float(value)
        raw = os.environ.get(env_name)
        return float(raw) if raw else default

    @staticmethod
    def _int_opt(value, env_name: str, default: int | None = None) -> int | None:
        if value is not None:
            return int(value)
        raw = os.environ.get(env_name)
        return int(raw) if raw else default

    @staticmethod
    def _str_opt(value, env_name: str) -> str | None:
        if value is not None:
            return str(value) or None
        raw = os.environ.get(env_name)
        return raw or None

    @staticmethod
    def _bool_opt(value, env_name: str, default: bool = False) -> bool:
        if value is not None:
            return bool(value)
        raw = os.environ.get(env_name, "").lower()
        if raw:
            return raw in {"1", "true", "yes", "on"}
        return default

    @staticmethod
    def _budget_exceeded(start_time: float, budget: float | None) -> bool:
        return budget is not None and (time.time() - start_time) >= budget

    @staticmethod
    def _new_trace() -> dict:
        return {
            "result_source": "none",
            "holes": 0,
            "hole_stmts": 0,
            "test_order_time": 0.0,
            "standardize_time": 0.0,
            "sketch_time": 0.0,
            "reformat_time": 0.0,
            "local_build_time": 0.0,
            "local_budget": "",
            "local_time": 0.0,
            "local_candidates": 0,
            "local_validations": 0,
            "local_passes": 0,
            "local_first_pass_at": 0,
            "local_best_ted": "",
            "local_timed_out": 0,
            "fallback_time": 0.0,
            "fallback_prefilter": "",
            "fallback_max_ted": "",
            "fallback_cluster": "",
            "fallback_clusters": 0,
            "fallback_cluster_size": 0,
            "fallback_ranks": 0,
            "fallback_validations": 0,
            "fallback_rejected": 0,
            "fallback_best_ted": "",
            "fallback_skipped": 0,
            "fallback_skip_reason": "",
            "fallback_timed_out": 0,
            "total_time": 0.0,
        }

    def run(self, trajectories:dict) -> dict:
        out = {}
        for user_id, traj in tqdm(trajectories.items(), total=len(trajectories), desc="Buggys", leave=False):
            refs = self._get_ac_pool(user_id)
            out[user_id] = self._pipeline_run(traj, refs)
        return dict(out)


class CaseTimeout(Exception):
    pass


def _handle_timeout(signum, frame):
    raise CaseTimeout()


@contextmanager
def _case_timeout(seconds: float | None):
    if not seconds:
        yield
        return
    old_handler = signal.signal(signal.SIGALRM, _handle_timeout)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)


def _solve_case(h: HISTRA, trajs, uid: str, case_timeout: float | None):
    start = time.time()
    patch = None
    try:
        with _case_timeout(case_timeout):
            patch = h._pipeline_run(trajs[uid], h._get_ac_pool(uid))
    except Exception:
        patch = None
    return uid, (patch, time.time() - start)


def _solve_worker(timeout, tests, refs, trajs, uids, case_timeout, queue):
    try:
        h = HISTRA(timeout, tests, refs)
        out = [_solve_case(h, trajs, uid, case_timeout) for uid in uids]
        queue.put(("ok", out))
    except Exception as exc:
        queue.put(("error", type(exc).__name__, str(exc)))


def _solve_parallel(timeout, tests, trajs, refs, case_timeout, case_jobs):
    uids = list(trajs)
    jobs = min(max(case_jobs, 1), len(uids))
    if jobs <= 1:
        h = HISTRA(timeout, tests, refs)
        return dict(_solve_case(h, trajs, uid, case_timeout) for uid in uids)

    queue = Queue()
    chunks = [uids[i::jobs] for i in range(jobs)]
    procs = []
    for chunk in chunks:
        if not chunk:
            continue
        proc = Process(
            target=_solve_worker,
            args=(timeout, tests, refs, trajs, chunk, case_timeout, queue),
        )
        proc.start()
        procs.append(proc)

    out = {}
    errors = []
    active = list(procs)
    while active:
        try:
            msg = queue.get(timeout=1.0)
        except Exception:
            msg = None
        if msg:
            if msg[0] == "ok":
                out.update(dict(msg[1]))
            else:
                errors.append(msg[1:])

        still_active = []
        for proc in active:
            if proc.is_alive():
                still_active.append(proc)
                continue
            proc.join()
            if proc.exitcode not in (0, None):
                errors.append(("ExitCode", str(proc.exitcode)))
        active = still_active

    if errors:
        raise RuntimeError(f"HISTRA worker errors: {errors}")
    return {uid: out.get(uid, (None, 0.0)) for uid in uids}


def solve(timeout, tests, trajs, refs) -> Dict[str, tuple[str | None, float]]:
    """Run the finalized HISTRA pipeline.

    This is the public runner used by run.py for the histra approach. Baseline
    dispatch stays in baselines/, while HISTRA's method and execution wrapper
    live in src/.
    """
    case_timeout = float(os.environ.get("HISTRA_CASE_TIMEOUT", "22"))
    case_jobs = int(os.environ.get("HISTRA_CASE_JOBS", "4"))
    return _solve_parallel(timeout, tests, trajs, refs, case_timeout, case_jobs)
