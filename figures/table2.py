"""
Method vs Applicability, FtX, FtP and PtP
"""

import fire
from pathlib import Path

from figures.util import collect_reports, applied_count, ftx_count, ftp_count, ptp_count

def main(instance_log_path: str = "./run_instance_swt_logs", total_instance_count: int = 300):
    instance_log_path = Path(instance_log_path)
    if not instance_log_path.exists():
        raise FileNotFoundError(f"Instance log directory not found at {instance_log_path}")
    methods = [
        ("gpt-4-1106-preview", "zsb__gpt-4-1106-preview__bm25_27k_cl100k__seed=0,temperature=0", r"\zsb"),
        ("gpt-4-1106-preview", "zsp__gpt-4-1106-preview__bm25_27k_cl100k__seed=0,temperature=0", r"\zsp"),
        ("gpt-4-1106-preview", "libro_gpt-4-1106-preview__bm25_27k_cl100k__seed=1,temperature=0.7.jsonl", r"\libro", "libro", [1,2,3,4,5], Path("inference_output/gpt-4-1106-preview__libro__libro_gpt-4-1106-preview__bm25_27k_cl100k__seed={seed},temperature=0.7.jsonl__[1, 2, 3, 4, 5]__gpt-4-1106-preview__test__seed=0,temperature=0__test.jsonl")),
        ("gpt-4-1106-preview", "libro_gpt-4-1106-preview__bm25_27k_cl100k__seed=1,temperature=0.7.jsonl", r"\pak", "p@k", [1,2,3,4,5]),
        ("gpt-4-1106-preview", "acr__gpt-4-1106-preview", r"\acr"),
        ("aider--gpt-4-1106-preview", "aider_gpt-4-1106-preview", r"\aider"),
        ("gpt4__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__gpt-4-1106-preview", r"\swea"),
        ("gpt4__SWE-bench_Lite__default_test_demo4__t-0.00__p-0.95__c-3.00__install-1", "sweap__gpt-4-1106-preview", r"\sweap"),
    ]

    print(r"Method & {$\bc{A}$ \up{}} & {\ftx \up{}} & {\ftp \up{}} & {\ptp} \\")
    for model, run_id, name, *args in methods:
        reports = collect_reports(model, run_id, instance_log_path, *args)
        applied = 100*applied_count(reports)/total_instance_count
        ftp = 100*ftp_count(reports)/total_instance_count
        ftx = 100*ftx_count(reports)/total_instance_count
        ptp = 100*ptp_count(reports)/total_instance_count
        print(f"{name} & {applied:.1f} & {ftx:.1f} & {ftp:.1f} & {ptp:.1f} \\")

if __name__ == "__main__":
    fire.Fire(main)