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
    "gpt-4-1106-preview": datetime.datetime(month=4, year=2023, day=30),
}

def main(instance_log_path: str = "./run_instance_swt_logs", dataset: str = "princeton-nlp/SWE-bench", split: str = "test", format="github"):
    instance_log_path = Path(instance_log_path)
    if not instance_log_path.exists():
        raise FileNotFoundError(f"Instance log directory not found at {instance_log_path}")
    methods = [
        ("gpt-4-1106-preview", "gpt-4-1106-preview__SWE-bench-balanced-2024-04-30__zsp__fs-bm25__mcc-27000-cl100k__seed=0,temperature=0__test", r"\zsb"),
    ]
    try:
        ds = datasets.load_dataset(dataset)
    except Exception:
        ds = datasets.load_from_disk(dataset)
    instance_timestamps = {instance["instance_id"]: datetime.datetime.strptime(instance["created_at"], "%Y-%m-%dT%H:%M:%SZ") for instance in ds[split]}

    gold_model, gold_run_id = "gold", "validate-gold-balanced"
    gold_reports = no_error_reports(collect_reports(gold_model, gold_run_id, instance_log_path))

    headers = (
        ["PR created", "$n$", r"{$\bc{A}$ \up{}}", r"{\suc \up{}}", r"{\ftx \up{}}", r"{\ftp \up{}}", r"{\ptp}", r"{$\dc^{\text{all}}$ }"]
        if format.startswith("latex") else
        ["PR created", "n", "Applicable", "F2X", "F2P", "P2P", "Coverage"]
    )
    rows = []
    for model, run_id, name, *args in methods:
        reports = collect_reports(model, run_id, instance_log_path, *args)
        actual_model = "gpt-4-1106-preview"
        cutoff = MODEL_KNOWLEDGE_CUTOFF.get(actual_model)
        gold_before_cutoff = {instance_id: report for instance_id, report in gold_reports.items() if instance_timestamps[instance_id] <= cutoff and report["resolved"]}
        gold_after_cutoff = {instance_id: report for instance_id, report in gold_reports.items() if instance_timestamps[instance_id] > cutoff and report["resolved"]}
        before_cutoff = {instance_id: report for instance_id, report in reports.items() if instance_timestamps[instance_id] <= cutoff}
        after_cutoff = {instance_id: report for instance_id, report in reports.items() if instance_timestamps[instance_id] > cutoff}

        for cutoff_relation, pred_reports, gold_reports in [("after $KC$", after_cutoff, gold_after_cutoff), ("before $KC$", before_cutoff, gold_before_cutoff)]:

            applicable = 100*no_error_count(pred_reports)/len(gold_reports)
            ftx = 100*ftx_count(pred_reports)/len(gold_reports)
            resolved = 100*ftp_count(pred_reports)/len(gold_reports)
            ftp = 100*actual_ftp_count(pred_reports)/len(gold_reports)
            ptp = 100*ptp_count(pred_reports)/len(gold_reports)
            total_coverage_possible = count_coverage_delta_gold(gold_reports)
            total_coverage_delta = 100 * sum_coverage_delta(reports) / total_coverage_possible
            rows.append([f"{cutoff_relation}", len(gold_reports), applicable, resolved, ftx, ftp, ptp, total_coverage_delta])
    print(tabulate(rows, headers=headers, tablefmt=format, floatfmt=".1f"))

if __name__ == "__main__":
    fire.Fire(main)
