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
        ("gpt-4o-mini-2024-07-18", "gpt-4o-mini-2024-07-18__swt_bench_lite_aug1_bm25_27k_cl100k_selfmade__seed=0,temperature=0,n=5__test._{seed}", r"0", [0,1,2,3,4]),
        ("gpt-4o-mini-2024-07-18", "gpt-4o-mini-2024-07-18__swt_bench_lite_aug1_bm25_27k_cl100k_selfmade__seed=0,temperature=0.2,n=5__test._{seed}", r"0.2", [0,1,2,3,4]),
        ("gpt-4o-mini-2024-07-18", "gpt-4o-mini-2024-07-18__swt_bench_lite_aug1_bm25_27k_cl100k_selfmade__seed=0,temperature=0.4,n=5__test._{seed}", r"0.4", [0,1,2,3,4]),
        ("gpt-4o-mini-2024-07-18", "gpt-4o-mini-2024-07-18__swt_bench_lite_aug1_bm25_27k_cl100k_selfmade__seed=0,temperature=0.7,n=25__test._{seed}", r"0.7", [0,1,2,3,4]),
    ]
    gold_model, gold_run_id = "gold", "validate-gold"
    gold_reports = collect_reports(gold_model, gold_run_id, instance_log_path)

    headers = (
        ["$T$", r"{$\bc{A}$ \up{}}", r"{\ftx \up{}}", r"{\ftp \up{}}", r"{\ptp}", r"{$\dc^{\text{all}}$ }"]
        if format.startswith("latex") else
        ["Temperature", "Applicability", "F2X", "F2P", "P2P", "Coverage"]
    )
    rows = []
    for model, run_id, name, seeds, *args in methods:
        ftp_scores = []
        ftx_scores = []
        ptp_scores = []
        applied_scores = []
        coverages_delta = []
        for seed in seeds:
            reports = collect_reports(model, run_id.format(seed=seed), instance_log_path, *args)
            applied_scores.append(100*no_error_count(reports)/total_instance_count)
            ftp_scores.append(100*ftp_count(reports)/total_instance_count)
            ftx_scores.append(100*ftx_count(reports)/total_instance_count)
            ptp_scores.append(100*ptp_count(reports)/total_instance_count)
            total_coverage_possible = count_coverage_delta_gold(gold_reports)
            total_coverage_delta = 100 * sum_coverage_delta(reports) / total_coverage_possible
            coverages_delta.append(total_coverage_delta)

        if len(seeds) > 1:
            applied_mean, applied_ci = with_error_bars(applied_scores)
            ftp_mean, ftp_me = with_error_bars(ftp_scores)
            ftx_mean, ftx_me = with_error_bars(ftx_scores)
            ptp_mean, ptp_me = with_error_bars(ptp_scores)
            coverages_delta_mean, coverages_delta_me = with_error_bars(coverages_delta)
            rows.append([name, f"{applied_mean:.1f} ± {applied_ci:.1f}", f"{ftx_mean:.1f} ± {ftx_me:.1f}", f"{ftp_mean:.1f} ± {ftp_me:.1f}", f"{ptp_mean:.1f} ± {ptp_me:.1f}", f"{coverages_delta_mean:.1f} ± {coverages_delta_me:.1f}"])
        else:
            rows.append([name, f"{applied_scores[0]:.1f}", f"{ftx_scores[0]:.1f}", f"{ftp_scores[0]:.1f}", f"{ptp_scores[0]:.1f}", f"{coverages_delta[0]:.1f}"])
    print(tabulate(rows, headers=headers, tablefmt=format, floatfmt=".1f"))

if __name__ == "__main__":
    fire.Fire(main)