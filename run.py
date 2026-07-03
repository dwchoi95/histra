import os
import argparse
import csv
import random
import time
from collections import defaultdict
from statistics import mean
from tqdm import tqdm
from prettytable import PrettyTable
from multiprocessing import Process, Lock
import warnings
warnings.filterwarnings('ignore')

from src.utils import DataLoader
from src.utils import metrics as _metrics
from src.core.histra import solve as histra_solve
from baselines.approaches import solve as baseline_solve, APPROACHES as BASELINE_APPROACHES

RUNNABLE_APPROACHES = ("histra",) + tuple(BASELINE_APPROACHES)
SUMMARY_ONLY_APPROACHES = ("hybrid_composed",)
APPROACHES = RUNNABLE_APPROACHES + SUMMARY_ONLY_APPROACHES

PER_HEADER = ["user_id", "buggy", "patch", "oracle", "fixed", "ted",
              "ip_last", "ip_traj", "att"]
SEED_PER_HEADER = PER_HEADER + ["seed"]
LLM_PER_HEADER = PER_HEADER + ["temperature", "model", "trials"]
HYBRID_PER_HEADER = LLM_PER_HEADER + ["source"]
OVERALL_HEADER = ["pid", "approach", "model", "corrects", "buggys", "fixed",
                  "rr", "ted", "ip_last", "ip_traj", "att"]
SUMMARY_HEADER = ["approach", "model", "corrects", "buggys", "fixed",
                  "rr", "ted", "ip_last", "ip_traj", "att"]
SUMMARY_ORDER = ("histra", "hybrid_composed", "hybrid_e2e",
                 "par", "partraj", "refactory")
LLM_APPROACHES = {"par", "partraj", "hybrid_e2e", "hybrid_composed"}
HYBRID_APPROACHES = {"hybrid_e2e", "hybrid_composed"}


def configure_seed(seed):
    if seed is None or str(seed).strip() == "":
        return ""
    seed_text = str(seed).strip()
    try:
        seed_int = int(seed_text)
    except ValueError:
        seed_int = sum(ord(ch) for ch in seed_text)
    random.seed(seed_int)
    os.environ["EXPERIMENT_SEED"] = seed_text
    os.environ["REFACTORY_SEED"] = seed_text
    os.environ.setdefault("PYTHONHASHSEED", seed_text)
    try:
        import numpy as np
        np.random.seed(seed_int)
    except Exception:
        pass
    return seed_text


def model_label(approach, model=None):
    if approach in LLM_APPROACHES:
        return model or os.environ.get("PAR_MODEL") or "gpt-3.5-turbo"
    return ""


def temperature_label():
    return os.environ.get("PAR_TEMPERATURE", "0")


def per_csv_path(out_root, pid, approach, trial=None, model=None):
    return os.path.join(out_root, pid, f"{approach}.csv")


def _float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _format_count(value):
    value = float(value)
    if value.is_integer():
        return str(int(value))
    return f"{value:.6f}"


def _format_metric(value):
    return f"{float(value):.6f}"


def _read_dict_rows(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return []
    with open(path, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _completed_trial_numbers(path, model):
    trials = set()
    for row in _read_dict_rows(path):
        if row.get("model", "") == model:
            trial = _int(row.get("trials"), 0)
            if trial > 0:
                trials.add(trial)
    return trials


def _has_columns(path, columns):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return False
    with open(path, "r", newline="", encoding="utf-8") as f:
        try:
            header = next(csv.reader(f))
        except StopIteration:
            return False
    return set(columns).issubset(set(header))


def result_complete(out_root, pid, approach, trial=None, model=None):
    path = per_csv_path(out_root, pid, approach, trial, model)
    if approach in LLM_APPROACHES:
        model = model_label(approach, model)
        expected_header = HYBRID_PER_HEADER if approach in HYBRID_APPROACHES else LLM_PER_HEADER
        if not _has_columns(path, expected_header):
            return False
        target_trials = _int(trial, 0)
        completed = _completed_trial_numbers(path, model)
        return bool(completed) if target_trials == 0 else target_trials in completed
    if approach in {"histra", "refactory"}:
        return _has_columns(path, SEED_PER_HEADER)
    return _has_columns(path, PER_HEADER)


def _read_overall_rows(path):
    rows = []
    for row in _read_dict_rows(path):
        if row.get("approach") not in APPROACHES:
            continue
        if "trial" in row or "label" in row:
            continue
        if not all(col in row for col in OVERALL_HEADER if col not in {"ip_last", "ip_traj"}):
            continue
        row = dict(row)
        if "ip_last" not in row:
            row["ip_last"] = row.get("ip", "")
        if "ip_traj" not in row:
            row["ip_traj"] = ""
        rows.append({col: row.get(col, "") for col in OVERALL_HEADER})
    return rows


def _aggregate_rows(approach, model, rows):
    corrects = sum(_int(r.get("corrects")) for r in rows)
    buggys = sum(_int(r.get("buggys")) for r in rows)
    fixed = sum(_float(r.get("fixed")) for r in rows)
    return [
        approach,
        model,
        corrects,
        buggys,
        _format_count(fixed),
        _format_metric((fixed / buggys) if buggys else 0.0),
        _format_metric(mean(_float(r.get("ted")) for r in rows) if rows else 0.0),
        _format_metric(mean(_float(r.get("ip_last")) for r in rows) if rows else 0.0),
        _format_metric(mean(_float(r.get("ip_traj")) for r in rows) if rows else 0.0),
        _format_metric(mean(_float(r.get("att")) for r in rows) if rows else 0.0),
    ]


def _row_value(row, key):
    if key == "ip_last":
        return row.get("ip_last", row.get("ip", ""))
    return row.get(key, "")


def _project_row(row, header):
    return {h: _row_value(row, h) for h in header}


def _llm_overall_from_csv(pid, approach, model, result_path, corrects, fallback_buggys):
    by_trial = defaultdict(list)
    for row in _read_dict_rows(result_path):
        if row.get("model", "") != model:
            continue
        trial = _int(row.get("trials"), 0)
        if trial > 0:
            by_trial[trial].append(row)

    trial_rows = []
    for trial_rows_raw in by_trial.values():
        fixed_vals = [_int(r.get("fixed"), 0) for r in trial_rows_raw]
        ted_vals = [_float(r.get("ted")) for r in trial_rows_raw if r.get("ted") != ""]
        ip_last_vals = [
            _float(_row_value(r, "ip_last"))
            for r in trial_rows_raw
            if _row_value(r, "ip_last") != ""
        ]
        ip_traj_vals = [
            _float(r.get("ip_traj"))
            for r in trial_rows_raw
            if r.get("ip_traj") != ""
        ]
        att_vals = [_float(r.get("att")) for r in trial_rows_raw if r.get("att") != ""]
        buggys = max(len(trial_rows_raw), 1)
        fixed = sum(fixed_vals)
        trial_rows.append({
            "buggys": buggys,
            "fixed": fixed,
            "rr": fixed / buggys,
            "ted": mean(ted_vals) if ted_vals else 0.0,
            "ip_last": mean(ip_last_vals) if ip_last_vals else 0.0,
            "ip_traj": mean(ip_traj_vals) if ip_traj_vals else 0.0,
            "att": mean(att_vals) if att_vals else 0.0,
        })

    if not trial_rows:
        return {
            "pid": pid,
            "approach": approach,
            "model": model,
            "corrects": str(corrects),
            "buggys": str(fallback_buggys),
            "fixed": "0",
            "rr": "0.000000",
            "ted": "0.000000",
            "ip_last": "0.000000",
            "ip_traj": "0.000000",
            "att": "0.000000",
        }

    buggys = max(row["buggys"] for row in trial_rows)
    fixed = mean(row["fixed"] for row in trial_rows)
    return {
        "pid": pid,
        "approach": approach,
        "model": model,
        "corrects": str(corrects),
        "buggys": str(buggys),
        "fixed": _format_count(fixed),
        "rr": _format_metric(mean(row["rr"] for row in trial_rows)),
        "ted": _format_metric(mean(row["ted"] for row in trial_rows)),
        "ip_last": _format_metric(mean(row["ip_last"] for row in trial_rows)),
        "ip_traj": _format_metric(mean(row["ip_traj"] for row in trial_rows)),
        "att": _format_metric(mean(row["att"] for row in trial_rows)),
    }


def refresh_summary(out_root):
    overall_path = os.path.join(out_root, "overall.csv")
    summary_path = os.path.join(out_root, "summary.csv")
    if not os.path.exists(overall_path) or os.path.getsize(overall_path) == 0:
        return

    by_approach_model = defaultdict(list)
    for row in _read_overall_rows(overall_path):
        key = (row["approach"], row.get("model", ""))
        by_approach_model[key].append(row)

    rows = [SUMMARY_HEADER]
    order = {name: i for i, name in enumerate(SUMMARY_ORDER)}
    for key in sorted(by_approach_model, key=lambda k: (order.get(k[0], 999), k[1])):
        rows.append(_aggregate_rows(*key, by_approach_model[key]))

    with open(summary_path, "w", newline="", encoding="utf-8") as sf:
        csv.writer(sf).writerows(rows)


def _default_jobs(approach, problem_count):
    env_jobs = os.environ.get("RUN_JOBS")
    if env_jobs:
        return max(1, int(env_jobs))
    if approach in BASELINE_APPROACHES:
        return 1
    return max(1, problem_count)


def preflight_approach(approach):
    if approach not in {"par", "partraj", "hybrid_e2e"}:
        return
    from baselines.par import check_api_ready
    if approach == "hybrid_e2e":
        label = "Hybrid"
    else:
        label = "PaRTraj" if approach == "partraj" else "PaR"
    check_api_ready(label)


def core(pid, timeout, tests, trajs, refs, approach, reset, out_root, lock):
    model = model_label(approach)
    trial = os.environ.get("RUN_TRIAL")
    is_llm = approach in LLM_APPROACHES
    seed = os.environ.get("EXPERIMENT_SEED", "")
    temperature = temperature_label()
    out_dir = os.path.join(out_root, pid)
    os.makedirs(out_dir, exist_ok=True)
    result_path = per_csv_path(out_root, pid, approach, trial, model)
    overall_path = os.path.join(out_root, "overall.csv")

    if (not reset) and result_complete(out_root, pid, approach, trial, model):
        return
    completed_trials = _completed_trial_numbers(result_path, model) if is_llm else set()
    current_trial = _int(trial, 0)
    if is_llm:
        if current_trial <= 0:
            current_trial = 1 if reset else ((max(completed_trials) + 1) if completed_trials else 1)
    else:
        current_trial = ""

    # Run the chosen approach -> {user_id: (patch_or_None, seconds[, source])}
    if approach == "histra":
        results = histra_solve(timeout, tests, trajs, refs)
    else:
        results = baseline_solve(approach, pid, timeout, tests, trajs, refs)

    rows = []
    fixed_cnt = 0
    ted_vals, ip_last_vals, ip_traj_vals, att_vals = [], [], [], []
    for uid, result in results.items():
        if len(result) == 3:
            patch, secs, source = result
        else:
            patch, secs = result
            source = ""
        was = trajs.get(uid) or []
        buggy = was[-1] if was else ""
        oracle = refs.get(uid) or ""
        fixed = 1 if patch else 0
        ted = _metrics.ted(buggy, patch) if (fixed and buggy) else None
        ip_last = (_metrics.intent_preservation(buggy, patch, oracle)
                   if (fixed and buggy and oracle) else None)
        ip_traj = (_metrics.intent_preservation_trajectory(was, patch, oracle)
                   if (fixed and was and oracle) else None)
        if fixed:
            fixed_cnt += 1
            if ted is not None:
                ted_vals.append(ted)
            if ip_last is not None:
                ip_last_vals.append(ip_last)
            if ip_traj is not None:
                ip_traj_vals.append(ip_traj)
        att_vals.append(secs)
        row = {
            "user_id": uid,
            "buggy": buggy,
            "patch": patch or "",
            "oracle": oracle,
            "fixed": fixed,
            "ted": ted if ted is not None else "",
            "ip_last": ip_last if ip_last is not None else "",
            "ip_traj": ip_traj if ip_traj is not None else "",
            "att": f"{secs:.6f}",
        }
        if is_llm:
            row.update({
                "temperature": temperature,
                "model": model,
                "trials": current_trial,
            })
            if approach in HYBRID_APPROACHES:
                row["source"] = source or ("partraj" if patch else "none")
        else:
            row["seed"] = seed
        rows.append(row)

    if is_llm:
        preserved = []
        reset_all_model = reset and _int(trial, 0) == 0
        header = HYBRID_PER_HEADER if approach in HYBRID_APPROACHES else LLM_PER_HEADER
        for row in _read_dict_rows(result_path):
            row_model = row.get("model", "")
            row_trial = _int(row.get("trials"), 0)
            if not row_model:
                continue
            if row_model != model or (not reset_all_model and row_trial != current_trial):
                preserved.append(_project_row(row, header))
        rows_to_write = preserved + [_project_row(row, header) for row in rows]
    else:
        header = SEED_PER_HEADER
        rows_to_write = [_project_row(row, header) for row in rows]

    with open(result_path, "w", newline="", encoding="utf-8") as cf:
        writer = csv.DictWriter(cf, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows_to_write)

    corrects = len(refs)
    buggys = max(len(results), 1)
    rr = fixed_cnt / buggys
    ted_mean = mean(ted_vals) if ted_vals else 0.0
    ip_last_mean = mean(ip_last_vals) if ip_last_vals else 0.0
    ip_traj_mean = mean(ip_traj_vals) if ip_traj_vals else 0.0
    att_mean = mean(att_vals) if att_vals else 0.0

    summary = PrettyTable()
    summary.field_names = ["PID", "Approach", "Model", "Trials", "Seed", "Corrects",
                           "Buggys", "Fixed", "RR", "TED", "IP_last",
                           "IP_traj", "ATT(s)"]
    summary.add_row([pid, approach, model, current_trial, seed, corrects, len(results), fixed_cnt,
                     f"{rr:.0%}", f"{ted_mean:.2f}", f"{ip_last_mean:+.2f}",
                     f"{ip_traj_mean:+.2f}",
                     f"{att_mean:.2f}"])
    print(summary)

    with lock:
        clean = []
        for row in _read_overall_rows(overall_path):
            same_result = (
                row["pid"] == pid
                and row["approach"] == approach
                and row.get("model", "") == model
            )
            if not same_result:
                clean.append(row)

        if is_llm:
            clean.append(_llm_overall_from_csv(
                pid, approach, model, result_path, corrects, len(results)
            ))
        else:
            clean.append({
                "pid": pid,
                "approach": approach,
                "model": model,
                "corrects": str(corrects),
                "buggys": str(len(results)),
                "fixed": str(fixed_cnt),
                "rr": _format_metric(rr),
                "ted": _format_metric(ted_mean),
                "ip_last": _format_metric(ip_last_mean),
                "ip_traj": _format_metric(ip_traj_mean),
                "att": _format_metric(att_mean),
            })
        order = {name: i for i, name in enumerate(SUMMARY_ORDER)}
        clean.sort(key=lambda r: (r["pid"], order.get(r["approach"], 999), r.get("model", "")))
        with open(overall_path, "w", newline="", encoding="utf-8") as of:
            writer = csv.DictWriter(of, fieldnames=OVERALL_HEADER)
            writer.writeheader()
            writer.writerows(clean)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', type=str, required=True,
                        help="Path to dataset directory (data/<pid>/...)")
    parser.add_argument('-a', '--approach', type=str, default="histra",
                        choices=list(RUNNABLE_APPROACHES),
                        help="Repair approach to run: histra | refactory | par | "
                             "partraj | hybrid_e2e")
    parser.add_argument('-r', '--reset', action='store_true', default=False,
                        help="Recompute even if results/<pid>/<approach>.csv exists")
    parser.add_argument('-j', '--jobs', type=int, default=None,
                        help="Number of problem processes to run at once "
                             "(default: 1 for par/partraj, all problems otherwise; "
                             "can also be set with RUN_JOBS)")
    parser.add_argument('-o', '--out-root', type=str, default="results",
                        help="Directory where per-problem CSVs, overall.csv, "
                             "and summary.csv are written.")
    parser.add_argument('--trial', type=str, default=None,
                        help="LLM trial number. Results still stay in "
                             "<out-root>/<pid>/<approach>.csv; this updates "
                             "the trials metadata and averaged overall row.")
    parser.add_argument('--model', type=str, default=None,
                        help="LLM model for par/partraj. Stored in the model "
                             "column of per-problem and aggregate CSVs.")
    parser.add_argument('--seed', type=str, default=os.environ.get("EXPERIMENT_SEED", "0"),
                        help="Experiment seed for reproducible non-LLM sampling "
                             "(default: EXPERIMENT_SEED or 0).")
    args = parser.parse_args()

    configure_seed(args.seed)

    if args.model:
        os.environ["PAR_MODEL"] = args.model
    if args.trial is not None:
        os.environ["RUN_TRIAL"] = args.trial
    else:
        os.environ.pop("RUN_TRIAL", None)

    assert os.path.exists(args.dataset), f"Dataset path does not exist: {args.dataset}"
    problems = DataLoader.run(args.dataset)
    out_root = args.out_root
    os.makedirs(out_root, exist_ok=True)

    pending = []
    for data in problems:
        pid = data[0]
        if args.reset or not result_complete(out_root, pid, args.approach,
                                             args.trial, args.model):
            pending.append(data)
    if pending:
        try:
            preflight_approach(args.approach)
        except Exception as exc:
            raise SystemExit(str(exc))

    lock = Lock()
    jobs = args.jobs if args.jobs is not None else _default_jobs(args.approach, len(pending))
    jobs = max(1, jobs)
    def reap_finished(active, wait=False):
        remaining = []
        while active:
            proc = active.pop(0)
            if wait:
                proc.join()
            elif proc.exitcode is None:
                remaining.append(proc)
                continue
            else:
                proc.join()
            if proc.exitcode != 0:
                raise RuntimeError(f"Problem process failed with exit code {proc.exitcode}")
        return remaining

    active = []
    for data in pending:
        pid, timeout, tests, trajs, refs = data
        out_dir = os.path.join(out_root, pid)
        os.makedirs(out_dir, exist_ok=True)
        if jobs == 1:
            try:
                core(pid, timeout, tests, trajs, refs,
                     args.approach, args.reset, out_root, lock)
            except Exception as exc:
                raise SystemExit(f"{args.approach} failed on {pid}: {exc}")
            continue
        proc = Process(target=core, args=(pid, timeout, tests, trajs, refs,
                                          args.approach, args.reset, out_root, lock))
        proc.start()
        active.append(proc)
        while len(active) >= jobs:
            active = reap_finished(active)
            if len(active) >= jobs:
                time.sleep(0.2)

    active = reap_finished(active, wait=True)

    refresh_summary(out_root)
