"""
Method vs Applicability, FtX, FtP and PtP
balanced
"""
import datetime

import datasets

import dataset
import fire
from pathlib import Path
from tabulate import tabulate

from figures.util import *

MODEL_KNOWLEDGE_CUTOFF = {
    "gpt4__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1": datetime.datetime(month=4, year=2023, day=30),
    "mistral-large__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1": datetime.datetime(month=1, year=2024, day=31),
    "claude-3.5__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__s-0__c-3.00__install-1": datetime.datetime(month=4, year=2024, day=30),
    "gpt4o-mini__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1": datetime.datetime(month=10, year=2023, day=31),
    "claude-3-haiku-20240307__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1": datetime.datetime(month=8, year=2023, day=31),
    "mixtral8x22b__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1": datetime.datetime(month=9, year=2021, day=30),

}

def main(instance_log_path: str = "./run_instance_swt_logs", dataset: str = "princeton-nlp/SWE-bench_Lite", split: str = "test", format="github"):
    instance_log_path = Path(instance_log_path)
    if not instance_log_path.exists():
        raise FileNotFoundError(f"Instance log directory not found at {instance_log_path}")
    methods = [
        ("gpt4__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__gpt-4-1106-preview", r"GPT-4 Preview 1106"),
        ("mistral-large__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__mistral_large", r"Mistral Large 2"),
        ("claude-3.5__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__s-0__c-3.00__install-1", "swea__claude-3.5-sonnet", "Claude 3.5 Sonnet"),
        ("gpt4o-mini__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__gpt-4o-mini-2024-07-18", r"GPT-4o mini  (2024-07-18)"),
        ("claude-3-haiku-20240307__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__claude-3-haiku-20240307", r"Claude 3.0 Haiku"),
        ("mixtral8x22b__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__together_mistralai_Mixtral-8x22B-Instruct-v0.1", r"Mixtral 8x22B"),
    ]
    try:
        ds = datasets.load_dataset(dataset)
    except Exception:
        ds = datasets.load_from_disk(dataset)
    instance_timestamps = {instance["instance_id"]: datetime.datetime.strptime(instance["created_at"], "%Y-%m-%dT%H:%M:%SZ") for instance in ds[split]}

    gold_model, gold_run_id = "gold", "validate-gold-1"
    all_gold_reports = collect_reports(gold_model, gold_run_id, instance_log_path)

    headers = (
        ["Model", "$KC$", "PR created", "$n$", r"{$\bc{A}$ \up{}}", r"{\ftp \up{}}", r"{$\dc^{\text{all}}$ }"]
        if format.startswith("latex") else
        ["Model", "KC", "PR created", "n", "Applicable", "F2P", "Coverage"]
    )
    rows = []
    for model, run_id, name, *args in methods:
        reports = collect_reports(model, run_id, instance_log_path, *args)
        cutoff = MODEL_KNOWLEDGE_CUTOFF.get(model)
        gold_before_cutoff = {instance_id: report for instance_id, report in all_gold_reports.items() if instance_timestamps[instance_id] <= cutoff and report["resolved"]}
        gold_after_cutoff = {instance_id: report for instance_id, report in all_gold_reports.items() if instance_timestamps[instance_id] > cutoff and report["resolved"]}
        before_cutoff = {instance_id: report for instance_id, report in reports.items() if instance_timestamps[instance_id] <= cutoff}
        after_cutoff = {instance_id: report for instance_id, report in reports.items() if instance_timestamps[instance_id] > cutoff}

        for name2, cutoffs, cutoff_relation, pred_reports, gold_reports in [(name, cutoff.strftime("%d %b %Y"), "before KC", before_cutoff, gold_before_cutoff), ("", "", "after KC", after_cutoff, gold_after_cutoff)]:

            applicable = f"{100*no_error_count(pred_reports)/len(gold_reports):.1f}" if len(gold_reports) > 0 else "-"
            # ftx = f"{100*ftx_count(pred_reports)/len(gold_reports):.1f}" if len(gold_reports) > 0 else "-"
            resolved = f"{100*ftp_count(pred_reports)/len(gold_reports):.1f}" if len(gold_reports) > 0 else "-"
            # ptp = f"{100*ptp_count(pred_reports)/len(gold_reports):.1f}" if len(gold_reports) > 0 else "-"
            total_coverage_possible = count_coverage_delta_gold(gold_reports)
            total_coverage_delta = f"{100 * sum_coverage_delta(pred_reports) / total_coverage_possible:.1f}" if total_coverage_possible > 0 else "-"
            rows.append([name2, cutoffs, f"{cutoff_relation}", len(gold_reports), applicable, resolved, total_coverage_delta])
    print(tabulate(rows, headers=headers, tablefmt=format, floatfmt=".1f"))

if __name__ == "__main__":
    fire.Fire(main)
