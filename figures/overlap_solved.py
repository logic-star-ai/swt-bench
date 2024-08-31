"""
Method vs Applicability, FtX, FtP and PtP
main
"""

from tabulate import tabulate
import fire
from pathlib import Path

from figures.util import *

def main(instance_log_path: str = "./run_instance_swt_logs", total_instance_count: int = total_cases_lite, format="github"):
    instance_log_path = Path(instance_log_path)
    if not instance_log_path.exists():
        raise FileNotFoundError(f"Instance log directory not found at {instance_log_path}")
    methods = [
        ("gpt-4-1106-preview", "libro_gpt-4-1106-preview__bm25_27k_cl100k__seed={seed},temperature=0.7.jsonl", r"\libro", "libro", [1,2,3,4,5], Path("inference_output/gpt-4-1106-preview__libro__libro_gpt-4-1106-preview__bm25_27k_cl100k__seed={seed},temperature=0.7.jsonl__(1, 2, 3, 4, 5)__gpt-4-1106-preview__test__test.jsonl")),
        ("gpt4__SWE-bench_Lite__default_test_demo4__t-0.00__p-0.95__c-3.00__install-1", "sweap__gpt-4-1106-preview", r"\sweap"),
    ]

    print(f"All: {total_instance_count}")
    solved_by_all = None
    for model, run_id, name, *args in methods:
        reports = collect_reports(model, run_id, instance_log_path, *args)
        resolved = set(instance_id for instance_id, report in reports.items() if report["resolved"])
        if solved_by_all is None:
            solved_by_all = resolved
        else:
            solved_by_all &= resolved
    print(f"Solved by all: {len(solved_by_all)}")
    for model, run_id, name, *args in methods:
        reports = collect_reports(model, run_id, instance_log_path, *args)
        resolved = set(instance_id for instance_id, report in reports.items() if report["resolved"])
        print(f"{name}: {len(resolved)}")

if __name__ == "__main__":
    fire.Fire(main)