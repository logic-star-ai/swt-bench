"""
Method vs Applicability, FtX, FtP and PtP
"""
import functools
from typing import Tuple

import fire
from pathlib import Path
import json

from src.constants import FAIL_TO_PASS, FAIL_TO_FAIL, PASS_TO_PASS


def collect_reports(model_name, run_id, instance_log_path: Path):
    run_path = instance_log_path / run_id / model_name
    reports = {}
    for dir in run_path.iterdir():
        if not dir.is_dir():
            continue
        report = dir / "report.json"
        if not report.exists():
            continue
        with open(report) as f:
            report_data = json.load(f)
        instance_id = dir.name
        reports[instance_id] = report_data[instance_id]
    return reports


def applied_count(reports):
    return sum(r["patch_successfully_applied"] for r in reports.values())

def ftp_count(reports):
    return sum(r["resolved"] for r in reports.values())

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
    return sum(get_ftx(r["pred"], r["base"]) for r in reports.values())


def get_ptp(report_pred: dict[str, list[str]], report_base: dict[str, list[str]]) -> int:
    """
    Determine resolved status of an evaluation instance

    """
    base_p2p = set(report_base[PASS_TO_PASS])
    pred_p2p = set(report_pred[PASS_TO_PASS])

    added_ptp = pred_p2p.difference(base_p2p)

    return bool(added_ptp)

def ptp_count(reports):
    return sum(get_ptp(r["pred"], r["base"]) for r in reports.values())

def main(instance_log_path: str = "./run_instance_swt_logs", total_instance_count: int = 300):
    instance_log_path = Path(instance_log_path)
    if not instance_log_path.exists():
        raise FileNotFoundError(f"Instance log directory not found at {instance_log_path}")
    methods = [
        ("gpt-4-1106-preview", "zsb__gpt-4-1106-preview__bm25_27k_cl100k__seed=0,temperature=0", r"\zsb"),
        ("gpt-4-1106-preview", "zsp__gpt-4-1106-preview__bm25_27k_cl100k__seed=0,temperature=0", r"\zsp"),
        # TODO libro,
        ("gpt-4-1106-preview", "acr__gpt-4-1106-preview", r"\acr"),
        ("aider--gpt-4-1106-preview", "aider_gpt-4-1106-preview", r"\aider"),
        ("gpt4__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__gpt-4-1106-preview", r"\swea"),
        ("gpt4__SWE-bench_Lite__default_test_demo4__t-0.00__p-0.95__c-3.00__install-1", "sweap__gpt-4-1106-preview", r"\sweap"),
    ]

    print("Method & Applicability & FtX & FtP & PtP")
    for model, run_id, name, in methods:
        reports = collect_reports(model, run_id, instance_log_path)
        applied = 100*applied_count(reports)/total_instance_count
        ftp = 100*ftp_count(reports)/total_instance_count
        ftx = 100*ftx_count(reports)/total_instance_count
        ptp = 100*ptp_count(reports)/total_instance_count
        print(f"{name} & {applied:.1f} & {ftx:.1f} & {ftp:.1f} & {ptp:.1f}")

if __name__ == "__main__":
    fire.Fire(main)