"""
Method vs Applicability, FtX, FtP and PtP
for different additional context
"""

import fire
from pathlib import Path

from figures.util import *

def main(instance_log_path: str = "./run_instance_swt_logs", total_instance_count: int = total_cases_lite):
    instance_log_path = Path(instance_log_path)
    if not instance_log_path.exists():
        raise FileNotFoundError(f"Instance log directory not found at {instance_log_path}")
    methods = [
        ('gpt-4-1106-preview', 'zsp__gpt-4-1106-preview__bm25_27k_cl100k_test=-,files=-,patch=-__seed=0,temperature=0', r"- & - & -"),
        ('gpt-4-1106-preview', 'zsp__gpt-4-1106-preview__bm25_27k_cl100k_test=-,files=y,patch=y__seed=0,temperature=0', r"- & \cmark & \cmark"),
        ('gpt-4-1106-preview', 'zsp__gpt-4-1106-preview__bm25_27k_cl100k_test=-,files=x,patch=x__seed=0,temperature=0', r"- & \xmark & \xmark"),
        ('gpt-4-1106-preview', 'zsp__gpt-4-1106-preview__bm25_27k_cl100k_test=y,files=-,patch=-__seed=0,temperature=0', r"\cmark & - & -"),
        ('gpt-4-1106-preview', 'zsp__gpt-4-1106-preview__bm25_27k_cl100k_test=y,files=y,patch=y__seed=0,temperature=0', r"\cmark & \cmark & \cmark"),
        ('gpt-4-1106-preview', 'zsp__gpt-4-1106-preview__bm25_27k_cl100k_test=y,files=x,patch=x__seed=0,temperature=0', r"\cmark & \xmark & \xmark"),
    ]
    with open("inference_output/zsp__gpt-4-1106-preview__bm25_27k_cl100k_test=-,files=x,patch=x__seed=0,temperature=0.jsonl", "r") as f:
        lines = [json.loads(l) for l in f.readlines()]
    instances_with_invalid_patch = {l["instance_id"] for l in lines}
    print("sample size:", len(instances_with_invalid_patch))

    print(r"Method & {$\bc{A}$ \up{}} & {\ftx \up{}} & {\ftp \up{}} & {\ptp} \\")
    for model, run_id, name, *args in methods:
        reports = collect_reports(model, run_id, instance_log_path, *args)
        reports = {i: r for i, r in reports.items() if i in instances_with_invalid_patch}
        applied = 100*no_error_count(reports)/total_instance_count
        ftp = 100*ftp_count(reports)/total_instance_count
        ftx = 100*ftx_count(reports)/total_instance_count
        ptp = 100*ptp_count(reports)/total_instance_count
        print(rf"{name} & {applied:.1f} & {ftx:.1f} & {ftp:.1f} & {ptp:.1f} \\")

if __name__ == "__main__":
    fire.Fire(main)