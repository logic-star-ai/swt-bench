"""
Method vs Applicability, FtX, FtP and PtP
"""

import fire
from pathlib import Path

from figures.util import *

def filtered_by_resolved(reports):
    return (
        {instance_id: report for instance_id, report in reports.items() if report["resolved"]},
        {instance_id: report for instance_id, report in reports.items() if not report["resolved"]}
    )

def avg_coverage_delta(reports):
    s = 0
    total = 0
    for report in reports.values():
        if report["coverage_delta_pred"] is not None:
            s += report["coverage_delta_pred"]
            total += 1
    return s / total

def main(instance_log_path: str = "./run_instance_swt_logs", total_instance_count: int = 279):
    instance_log_path = Path(instance_log_path)
    if not instance_log_path.exists():
        raise FileNotFoundError(f"Instance log directory not found at {instance_log_path}")
    methods = [
        ("gold", "validate-gold", r"Gold"),
        ("gpt-4-1106-preview", "zsb__gpt-4-1106-preview__bm25_27k_cl100k__seed=0,temperature=0", r"\zsb"),
        ("gpt-4-1106-preview", "zsp__gpt-4-1106-preview__bm25_27k_cl100k__seed=0,temperature=0", r"\zsp"),
        ("gpt-4-1106-preview", "libro_gpt-4-1106-preview__bm25_27k_cl100k__seed={seed},temperature=0.7.jsonl", r"\libro", "libro", [1,2,3,4,5], Path("inference_output/gpt-4-1106-preview__libro__libro_gpt-4-1106-preview__bm25_27k_cl100k__seed={seed},temperature=0.7.jsonl__[1, 2, 3, 4, 5]__gpt-4-1106-preview__test__all__seed=0,temperature=0__test.jsonl")),
        ("gpt-4-1106-preview", "libro_gpt-4-1106-preview__bm25_27k_cl100k__seed={seed},temperature=0.7.jsonl", r"\pak", "p@k", [1,2,3,4,5]),
        ("gpt-4-1106-preview", "acr__gpt-4-1106-preview", r"\acr"),
        ("aider--gpt-4-1106-preview", "aider_gpt-4-1106-preview", r"\aider"),
        ("gpt4__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__gpt-4-1106-preview", r"\swea"),
        ("gpt4__SWE-bench_Lite__default_test_demo4__t-0.00__p-0.95__c-3.00__install-1", "sweap__gpt-4-1106-preview", r"\sweap"),
    ]

    print(r"Method & total delta & resolved delta & unresolved delta \\")
    for model, run_id, name, *args in methods:
        reports = collect_reports(model, run_id, instance_log_path, *args)
        resolved_reports, unresolved_reports = filtered_by_resolved(reports)
        total_coverage_delta = avg_coverage_delta(reports)
        resolved_coverage_delta = avg_coverage_delta(resolved_reports)
        unresolved_coverage_delta = avg_coverage_delta(unresolved_reports)
        print(rf"{name} & {total_coverage_delta:.1f} & {resolved_coverage_delta:.1f} & {unresolved_coverage_delta:.1f} \\")

if __name__ == "__main__":
    fire.Fire(main)