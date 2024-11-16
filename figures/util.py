import functools
from collections import defaultdict
from typing import Tuple, Literal

from pathlib import Path
import json

import numpy as np

from constants import FAIL_TO_PASS, FAIL_TO_FAIL, PASS_TO_PASS
import difflib

FILTER_FILE = "dataset/filter_cases_lite.txt"
FILTER_FILE_FULL = "dataset/filter_cases_full.txt"

@functools.lru_cache(maxsize=1)
def _filter_cases():
    filter_cases = set()
    for file in [FILTER_FILE, FILTER_FILE_FULL]:
        with open(file) as f:
            filter_cases.update(f.read().splitlines(keepends=False))
    return frozenset(filter_cases)

total_cases_lite = 276

def _collect_reports(model_name, run_id, instance_log_path: Path, filter_cases=True):
    run_path = instance_log_path / run_id / model_name
    reports = {}
    for dir in run_path.iterdir():
        if not dir.is_dir():
            continue
        report = dir / "report.json"
        if not report.exists():
            continue
        instance_id = dir.name
        if filter_cases and instance_id in _filter_cases():
            continue
        with open(report) as f:
            report_data = json.load(f)[instance_id]
        patch_path = instance_log_path / run_id / f"pred_post_{model_name}" / dir.name / "model_patch.diff"
        if patch_path.exists():
            with open(patch_path) as f:
                report_data["patch"] = f.read()
        reports[instance_id] = report_data
    return reports

def _collect_reports_multi(model_name, run_id_pattern, instance_log_path: Path, seeds: Tuple[int], filter_cases=True):
    all_reports = defaultdict(dict)
    for seed in seeds:
        run_id = run_id_pattern.format(seed=seed)
        reports = collect_reports(model_name, run_id, instance_log_path, filter_cases=filter_cases)
        for instance_id, report in reports.items():
            all_reports[instance_id][seed] = report
    return all_reports

def _select_reports_libro(all_reports, libro_decision_file: Path):
    with open(libro_decision_file) as f:
        libro_decisions = [json.loads(l) for l in f.readlines()]
    libro_decisions = {d["instance_id"]: d for d in libro_decisions}
    reports = {}
    for instance_id, i_reports in all_reports.items():
        cluster_preferred = []
        cluster_secondary = []
        for seed, report in i_reports.items():
            report["seed"] = seed
            libro_decision = libro_decisions.get(f"{instance_id}_seed={seed}", {}).get("full_output", "no")
            if "yes" in libro_decision.lower():
                cluster_preferred.append(report)
            else:
                cluster_secondary.append(report)
        if not cluster_preferred and not cluster_secondary:
            best_case = [r for r in i_reports.values()][0]
        else:
            def get_patch_len(x):
                if x.get("patch") is None:
                    return float("inf")
                return len(x["patch"])
            if not cluster_preferred:
                best_case = min(cluster_secondary, key=get_patch_len)
            else:
                best_case = min(cluster_preferred, key=get_patch_len)
        reports[instance_id] = best_case
    return reports

def _select_reports_passatk(all_reports):
    reports = {}
    for instance_id, i_reports in all_reports.items():
        for attribute_pref in ["resolved", "added_f2p", "coverage_delta_pred", "patch_successfully_applied"]:
            for seed, report in i_reports.items():
                if (report.get(attribute_pref) or 0) > reports.get(instance_id, {}).get(attribute_pref, 0):
                    reports[instance_id] = report
                    break
            if reports.get(instance_id) is not None:
                break
    return reports


def collect_reports(model_name, run_id, instance_log_path: Path, mode: Literal["single", "libro", "p@k"] = "single", seeds: Tuple[int] = None, libro_decision_file: Path = None, filter_cases=True):
    if mode == "single":
        return _collect_reports(model_name, run_id, instance_log_path, filter_cases)
    if seeds is None:
        raise ValueError("seeds must be provided for mode 'libro' or 'p@k'")
    all_reports = _collect_reports_multi(model_name, run_id, instance_log_path, seeds, filter_cases)
    if mode == "p@k":
        return _select_reports_passatk(all_reports)
    if mode == "libro":
        if libro_decision_file is None:
            raise ValueError("libro_decision_file must be provided for mode 'libro'")
        return _select_reports_libro(all_reports, libro_decision_file)
    else:
        raise ValueError(f"Unknown mode: {mode}")

def applied_count(reports):
    """
    Count the number of instances where the patch was successfully applied
    """
    return sum(r["patch_successfully_applied"] for r in reports.values())

def no_error_filter(r):
    """
    Return the instances where at least one test was executed i.e.
    there was no syntax error or name error introduced by the patch
    """
    if "tests_pred" not in r:
        return False
    original_number_tests = sum(len(t) for t in r["tests_base"].values())
    tests_after_pred = sum(len(t) for t in r["tests_pred"].values())
    # if tests after pred is less than 10% of the original number of tests this counts as error
    return tests_after_pred >= 0.1*original_number_tests



def no_error_count(reports):
    """
    Count the number of instances where at least one test was executed i.e.
    there was no syntax error or name error introduced by the patch
    """
    return sum(no_error_filter(r) for r in reports.values())

def no_error_reports(reports):
    return {instance_id: report for instance_id, report in reports.items() if no_error_filter(report)}

def ftp_count(reports):
    return sum(r["resolved"] for r in reports.values())

def ftp_reports(reports):
    return {instance_id: report for instance_id, report in reports.items() if report["resolved"]}

def get_actual_ftp(report_pred: dict[str, list[str]], report_base: dict[str, list[str]]) -> int:
    """
    Determine resolved status of an evaluation instance

    """
    base_f2p = set(report_base[FAIL_TO_PASS])
    pred_f2p = set(report_pred[FAIL_TO_PASS])

    added_ftp = pred_f2p.difference(base_f2p)

    return bool(added_ftp)

def actual_ftp_count(reports):
    return sum(get_actual_ftp(r["tests_pred"], r["tests_base"]) for r in reports.values() if "tests_pred" in r)

def actual_ftp_reports(reports):
    return {instance_id: report for instance_id, report in reports.items() if "tests_pred" in report and get_actual_ftp(report["tests_pred"], report["tests_base"])}

def get_ftx(report_pred: dict[str, list[str]], report_base: dict[str, list[str]]) -> int:
    """
    Determine resolved status of an evaluation instance

    """
    base_f2p = set(report_base[FAIL_TO_PASS])
    pred_f2p = set(report_pred[FAIL_TO_PASS])

    base_f2f = set(report_base[FAIL_TO_FAIL])
    pred_f2f = set(report_pred[FAIL_TO_FAIL])

    added_ftx = pred_f2p.difference(base_f2p) | pred_f2f.difference(base_f2f)

    return bool(added_ftx)

def ftx_count(reports):
    return sum(get_ftx(r["tests_pred"], r["tests_base"]) for r in reports.values() if "tests_pred" in r)

def ftx_reports(reports):
    return {instance_id: report for instance_id, report in reports.items() if "tests_pred" in report and get_ftx(report["tests_pred"], report["tests_base"])}


def get_ptp(report_pred: dict[str, list[str]], report_base: dict[str, list[str]]) -> int:
    """
    Determine resolved status of an evaluation instance

    """
    base_p2p = set(report_base[PASS_TO_PASS])
    pred_p2p = set(report_pred[PASS_TO_PASS])

    added_ptp = pred_p2p.difference(base_p2p)

    return bool(added_ptp)

def ptp_count(reports):
    return sum(get_ptp(r["tests_pred"], r["tests_base"]) for r in reports.values() if "tests_pred" in r)

def ptp_reports(reports):
    return {instance_id: report for instance_id, report in reports.items() if "tests_pred" in report and get_ptp(report["tests_pred"], report["tests_base"])}

def filtered_by_resolved(reports):
    return (
        {instance_id: report for instance_id, report in reports.items() if report["resolved"]},
        {instance_id: report for instance_id, report in reports.items() if not report["resolved"]}
    )


def sum_coverage_delta(reports):
    s = 0
    for report in reports.values():
        delta = report.get("coverage_delta_pred")
        if delta is not None:
            s += delta
    return s

def count_coverage_delta_gold(reports):
    s = 0
    for report in reports.values():
        s += report.get("coverage_delta_gold") is not None
    return s


def with_error_bars(data, z=1.96):
    # Calculate mean
    mean = np.mean(data)

    # Calculate standard deviation
    std_dev = np.std(data, ddof=1)  # ddof=1 for sample standard deviation

    # Calculate standard error
    std_error = std_dev / np.sqrt(len(data))

    # Calculate 95% confidence interval
    margin_of_error = z * std_error

    return mean, margin_of_error

def reports_to_array(gold_reports, reports):
    return np.array([100 if k in reports else 0 for k in sorted(gold_reports.keys())])

def load_diff(instance, model, run_id, instance_log_path):
    diff_path = instance_log_path / run_id / f"pred_post__{model}" / instance / "model_patch.diff"
    if diff_path.exists():
        with open(diff_path) as f:
            return f.read()
    return None

def repo_from_instance_id(instance_id):
    return instance_id.split("__")[1].split("-")[0]
