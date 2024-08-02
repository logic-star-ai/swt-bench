"""
Method vs Applicability, FtX, FtP and PtP
setting of directed fuzzing
"""

import fire
from pathlib import Path

from figures.util import *

def main(instance_log_path: str = "./run_instance_swt_logs", total_instance_count: int = 279):
    instance_log_path = Path(instance_log_path)
    if not instance_log_path.exists():
        raise FileNotFoundError(f"Instance log directory not found at {instance_log_path}")
    methods = [
        ("gold", "validate-gold", r"Gold"),
        ("gpt-4-1106-preview", "gpt-4-1106-preview__swt_bench_linecover_oracle__seed=0,temperature=0__test.json", r"\zsp"),
        ("gpt-4-1106-preview", "gpt-4-1106-preview__swt_bench_linecover_oracle__seed=0,temperature=0.7,n=5__test._0.json", r"\pak", "p@k", [1,2,3,4,5]),
        # ("gpt4__SWE-bench_Lite__default_test_demo4__t-0.00__p-0.95__c-3.00__install-1", "sweap__gpt-4-1106-preview", r"\sweap"),
    ]

    print(r"Method & {$\bc{A}$ \up{}} & {\ftx \up{}} & {\ftp \up{}} & {\ptp} \\")
    for model, run_id, name, *args in methods:
        reports = collect_reports(model, run_id, instance_log_path, *args)
        applied = 100*no_error_count(reports)/total_instance_count
        ftp = 100*ftp_count(reports)/total_instance_count
        ftx = 100*ftx_count(reports)/total_instance_count
        ptp = 100*ptp_count(reports)/total_instance_count
        print(rf"{name} & {applied:.1f} & {ftx:.1f} & {ftp:.1f} & {ptp:.1f} \\")

if __name__ == "__main__":
    fire.Fire(main)