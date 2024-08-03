"""
Method vs Applicability, FtX, FtP and PtP
main
"""

from tabulate import tabulate
import fire
from pathlib import Path

from figures.util import *

def main(instance_log_path: str = "./run_instance_swt_logs", total_instance_count: int = 279, format="github"):
    instance_log_path = Path(instance_log_path)
    if not instance_log_path.exists():
        raise FileNotFoundError(f"Instance log directory not found at {instance_log_path}")
    methods = [
        ("gold", "validate-gold", r"Gold"),
        ("gpt-4o-mini-2024-07-18", "gpt-4o-mini-2024-07-18__swt_bench_lite_aug1_bm25_27k_cl100k_selfmade__seed=0,temperature=0,n=5__test._0", r"\zsp 0"),
        ("gpt-4o-mini-2024-07-18", "gpt-4o-mini-2024-07-18__swt_bench_lite_aug1_bm25_27k_cl100k_selfmade__seed=0,temperature=0.2,n=5__test._0", r"\zsp 0.2"),
        ("gpt-4o-mini-2024-07-18", "gpt-4o-mini-2024-07-18__swt_bench_lite_aug1_bm25_27k_cl100k_selfmade__seed=0,temperature=0.4,n=5__test._0", r"\zsp 0.4"),
        ("gpt-4o-mini-2024-07-18", "gpt-4o-mini-2024-07-18__swt_bench_lite_aug1_bm25_27k_cl100k_selfmade__seed=0,temperature=0,n=5__test._{seed}", r"\pak 0", "p@k", [0, 1, 2, 3, 4]),
        ("gpt-4o-mini-2024-07-18", "gpt-4o-mini-2024-07-18__swt_bench_lite_aug1_bm25_27k_cl100k_selfmade__seed=0,temperature=0.2,n=5__test._{seed}", r"\pak 0.2", "p@k", [0, 1, 2, 3, 4]),
        ("gpt-4o-mini-2024-07-18", "gpt-4o-mini-2024-07-18__swt_bench_lite_aug1_bm25_27k_cl100k_selfmade__seed=0,temperature=0.4,n=5__test._{seed}", r"\pak 0.4", "p@k", [0, 1, 2, 3, 4]),
    ]

    headers = (
        ["Method", r"{$\bc{A}$ \up{}}", r"{\ftx \up{}}", r"{\ftp \up{}}", r"{\ptp}"]
        if format == "latex" else
        ["Method", "Applicability", "F2X", "F2P", "P2P"]
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