"""
Method vs Applicability, FtX, FtP and PtP
main
"""

from tabulate import tabulate
import fire
from pathlib import Path

from figures.util import *
import numpy as np
from scipy import stats

def with_error_bars(data, confidence=0.95):
    # Calculate mean
    mean = np.mean(data)

    # Calculate standard deviation
    std_dev = np.std(data, ddof=1)  # ddof=1 for sample standard deviation

    # Calculate standard error
    std_error = std_dev / np.sqrt(len(data))

    # Calculate 95% confidence interval
    confidence_level = confidence
    degrees_freedom = len(data) - 1
    t_value = stats.t.ppf((1 + confidence_level) / 2, degrees_freedom)
    margin_of_error = t_value * std_error

    return mean, margin_of_error


def main(instance_log_path: str = "./run_instance_swt_logs", total_instance_count: int = 279, format="github"):
    instance_log_path = Path(instance_log_path)
    if not instance_log_path.exists():
        raise FileNotFoundError(f"Instance log directory not found at {instance_log_path}")
    methods = [
        ("gold", "validate-gold", r"Gold"),
        ("gpt-4o-mini-2024-07-18", "gpt-4o-mini-2024-07-18__swt_bench_lite_aug1_bm25_27k_cl100k_selfmade__seed=0,temperature=0,n=5__test._{seed}", r"\zsp 0"),
        ("gpt-4o-mini-2024-07-18", "gpt-4o-mini-2024-07-18__swt_bench_lite_aug1_bm25_27k_cl100k_selfmade__seed=0,temperature=0.2,n=5__test._{seed}", r"\zsp 0.2"),
        ("gpt-4o-mini-2024-07-18", "gpt-4o-mini-2024-07-18__swt_bench_lite_aug1_bm25_27k_cl100k_selfmade__seed=0,temperature=0.4,n=5__test._{seed}", r"\zsp 0.4"),
    ]

    headers = (
        ["Method", r"{$\bc{A}$ \up{}}", r"{\ftx \up{}}", r"{\ftp \up{}}", r"{\ptp}"]
        if format == "latex" else
        ["Method", "Applicability", "F2X", "F2P", "P2P"]
    )
    rows = []
    seeds = [0, 1, 2, 3, 4]
    for model, run_id, name, *args in methods:
        ftp_scores = []
        ftx_scores = []
        ptp_scores = []
        applied_scores = []
        for seed in seeds:
            reports = collect_reports(model, run_id.format(seed=seed), instance_log_path, *args)
            applied_scores.append(100*no_error_count(reports)/total_instance_count)
            ftp_scores.append(100*ftp_count(reports)/total_instance_count)
            ftx_scores.append(100*ftx_count(reports)/total_instance_count)
            ptp_scores.append(100*ptp_count(reports)/total_instance_count)
        applied_mean, applied_ci = with_error_bars(applied_scores)
        ftp_mean, ftp_me = with_error_bars(ftp_scores)
        ftx_mean, ftx_me = with_error_bars(ftx_scores)
        ptp_mean, ptp_me = with_error_bars(ptp_scores)
        rows.append([name, f"{applied_mean:.1f}±{applied_ci:.1f}", f"{ftx_mean:.1f}±{ftx_me:.1f}", f"{ftp_mean:.1f}±{ftp_me:.1f}", f"{ptp_mean:.1f}±{ptp_me:.1f}"])
    print(tabulate(rows, headers=headers, tablefmt=format, floatfmt=".1f"))

if __name__ == "__main__":
    fire.Fire(main)