"""
Method vs Applicability, FtX, FtP and PtP
main
"""

from tabulate import tabulate
import fire

from figures.util import *

from figures.util import with_error_bars


def main(instance_log_path: str = "./run_instance_swt_logs", total_instance_count: int = 279, format="github"):
    instance_log_path = Path(instance_log_path)
    if not instance_log_path.exists():
        raise FileNotFoundError(f"Instance log directory not found at {instance_log_path}")
    methods = [
        ("gpt-4o-mini-2024-07-18", "gpt-4o-mini-2024-07-18__swt_bench_lite_aug1_bm25_27k_cl100k_selfmade__seed=0,temperature=0.7,n=25__test._{seed}", r"\zsp 0.7", [0,1,2,3,4]),
        ("gpt-4o-mini-2024-07-18", "gpt-4o-mini-2024-07-18__swt_bench_lite_aug1_bm25_27k_cl100k_selfmade__seed=0,temperature=0.7,n=25__test._{seed}", r"\pak 0.7", [f"{{seed+{k}}}" for k in (0,5,10,15,20)], "p@k", (0,1,2,3,4)),
        ("gpt4o-mini__SWE-bench_Lite__default_test_demo4__t-0.70__p-0.95__s-{seed}__c-3.00__install-1", "swe-agent-demo4-gpt4omini__swt_bench_lite__test__{seed}", r"\sweap 0.7", [1,2,3,4,5]),
        ("aider--gpt-4o-mini-2024-07-18", "aider_gpt4omini__swt-lite__test_s{seed}", r"\aider 0.7", [0,1,2,3,4]),
    ]

    headers = (
        ["Method", r"{$\bc{A}$ \up{}}", r"{\ftx \up{}}", r"{\ftp \up{}}", r"{\ptp}"]
        if format == "latex" else
        ["Method", "Applicability", "F2X", "F2P", "P2P"]
    )
    rows = []
    for model, run_id, name, seeds, *args in methods:
        ftp_scores = []
        ftx_scores = []
        ptp_scores = []
        applied_scores = []
        for seed in seeds:
            reports = collect_reports(model.format(seed=seed), run_id.format(seed=seed), instance_log_path, *args)
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