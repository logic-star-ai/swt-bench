"""
Method vs Applicability, FtX, FtP and PtP
for different models
"""

import fire
from pathlib import Path

from figures.util import *
from tabulate import tabulate

def main(instance_log_path: str = "./run_instance_swt_logs", total_instance_count: int = 279, format: str = "github"):
    instance_log_path = Path(instance_log_path)
    if not instance_log_path.exists():
        raise FileNotFoundError(f"Instance log directory not found at {instance_log_path}")
    methods = [
        ("gpt4__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__gpt-4-1106-preview", r"GPT-4"),
        ("mistral-large__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__mistral_large", r"Mistral Large 2"),
        ("gpt4o-mini__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__gpt-4o-mini-2024-07-18", r"GPT-4o mini"),
        ("mixtral8x22b__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__together_mistralai_Mixtral-8x22B-Instruct-v0.1", r"Mixtral"),
        ("claude-3-haiku-20240307__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__claude-3-haiku-20240307", r"Haiku"),
    ]

    headers = (
        ["Method", r"{$\bc{A}}$ \up{}}", r"{\ftx \up{}}", r"{\ftp \up{}}", r"{\ptp}"]
        if format == "latex" else
        ["Method", "Applicability", "FtX", "FtP", "PtP", "Cost"]
    )
    rows = []
    for model, run_id, name, *args in methods:
        reports = collect_reports(model, run_id, instance_log_path, *args)
        applied = 100*no_error_count(reports)/total_instance_count
        ftp = 100*ftp_count(reports)/total_instance_count
        ftx = 100*ftx_count(reports)/total_instance_count
        ptp = 100*ptp_count(reports)/total_instance_count
        rows.append([name, applied, ftx, ftp, ptp])
    print(tabulate(rows, headers=headers, tablefmt=format, floatfmt=".1f"))

if __name__ == "__main__":
    fire.Fire(main)