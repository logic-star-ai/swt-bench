"""
Method vs Applicability, FtX, FtP and PtP
main
"""
import datetime

import datasets

import dataset
import fire
from pathlib import Path

from figures.util import *

MODEL_KNOWLEDGE_CUTOFF = {
    "gpt-4-1106-preview": datetime.datetime(month=4, year=2023, day=30),
}

def main(instance_log_path: str = "./run_instance_swt_logs", dataset: str = "princeton-nlp/SWE-bench_Lite", split: str = "test"):
    instance_log_path = Path(instance_log_path)
    if not instance_log_path.exists():
        raise FileNotFoundError(f"Instance log directory not found at {instance_log_path}")
    methods = [
        ("gpt-4-1106-preview", "gpt-4-1106-preview__SWE-bench-balanced-2024-04-30__zsp__fs-bm25__mcc-27000-cl100k__seed=0,temperature=0__test.json", r"\zsb"),
    ]
    ds = datasets.load_dataset(dataset)
    instance_timestamps = {instance["instance_id"]: datetime.datetime.strptime(instance["created_at"], "%Y-%m-%dT%H:%M:%SZ") for instance in ds[split]}

    gold_model, gold_run_id = "gold", "validate-gold"
    gold_reports = collect_reports(gold_model, gold_run_id, instance_log_path)

    print(r"Method & before cutoff & after cutoff \\")
    for model, run_id, name, *args in methods:
        reports = collect_reports(model, run_id, instance_log_path, *args)
        actual_model = "gpt-4-1106-preview"
        cutoff = MODEL_KNOWLEDGE_CUTOFF.get(actual_model)
        gold_before_cutoff = {instance_id: report for instance_id, report in gold_reports.items() if instance_timestamps[instance_id] <= cutoff and report["resolved"]}
        gold_after_cutoff = {instance_id: report for instance_id, report in gold_reports.items() if instance_timestamps[instance_id] > cutoff and report["resolved"]}
        before_cutoff = {instance_id: report for instance_id, report in reports.items() if instance_timestamps[instance_id] <= cutoff}
        after_cutoff = {instance_id: report for instance_id, report in reports.items() if instance_timestamps[instance_id] > cutoff}
        resolved_before_cutoff = 100*ftp_count(before_cutoff)/len(gold_before_cutoff)
        resolved_after_cutoff = 100*ftp_count(after_cutoff)/len(gold_after_cutoff)
        print(rf"{name} & {resolved_before_cutoff:.1f} & {resolved_after_cutoff:.1f} \\")


if __name__ == "__main__":
    fire.Fire(main)