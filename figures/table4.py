"""
Method vs Applicability, FtX, FtP and PtP
for different models
"""

import fire
from pathlib import Path

from figures.util import *
from tabulate import tabulate

def main(instance_log_path: str = "./run_instance_swt_logs", total_instance_count: int = total_cases_lite, format: str = "github"):
    instance_log_path = Path(instance_log_path)
    if not instance_log_path.exists():
        raise FileNotFoundError(f"Instance log directory not found at {instance_log_path}")
    methods = [
        ("mistral-large__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__mistral_large", r"Mistral Large 2"),
        ("gpt4__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__gpt-4-1106-preview", r"GPT-4 Preview 1106"),
        ("claude-3.5__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__s-0__c-3.00__install-1", "swea__claude-3.5-sonnet", "Claude 3.5 Sonnet"),
        ("gpt4o-mini__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__gpt-4o-mini-2024-07-18", r"GPT-4o mini  (2024-07-18)"),
        ("claude-3-haiku-20240307__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__claude-3-haiku-20240307", r"Claude 3.0 Haiku"),
        ("mixtral8x22b__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__together_mistralai_Mixtral-8x22B-Instruct-v0.1", r"Mixtral 8x22B"),
    ]
    gold_model, gold_run_id = "gold", "validate-gold-1"
    gold_reports = collect_reports(gold_model, gold_run_id, instance_log_path)
    total_coverage_possible = count_coverage_delta_gold(gold_reports)

    headers = (
        ["Model", r"{$\bc{W}$ \up{}}", r"{\suc \up{}}", r"{\ftx \up{}}", r"{\ftp \up{}}", r"{\ptp}",  r"{$\dc^{\text{all}}$ }"]
        if format.startswith("latex") else
        ["Model", "Applicability", "Success", "F2X", "F2P", "P2P", "Coverage"]
    )
    rows = []
    for model, run_id, name, *args in methods:
        reports = collect_reports(model, run_id, instance_log_path, *args)
        applied = 100*no_error_count(reports)/total_instance_count
        ftp = 100*ftp_count(reports)/total_instance_count
        actual_ftp = 100*actual_ftp_count(reports)/total_instance_count
        ftx = 100*ftx_count(reports)/total_instance_count
        ptp = 100*ptp_count(reports)/total_instance_count
        total_coverage_delta = 100 * sum_coverage_delta(reports) / total_coverage_possible
        rows.append([name, applied, ftp, ftx, actual_ftp, ptp, total_coverage_delta])
    print(tabulate(rows, headers=headers, tablefmt=format, floatfmt=".1f"))

if __name__ == "__main__":
    fire.Fire(main)