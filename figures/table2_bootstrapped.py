"""
Method vs Applicability, FtX, FtP and PtP
main
with bootstrapped confidence intervals
"""

from tabulate import tabulate
import fire
from pathlib import Path
from bootstrapped import bootstrap as bs
from bootstrapped import stats_functions as bs_stats

from figures.util import *

def main(instance_log_path: str = "./run_instance_swt_logs", total_instance_count: int = 279, format="github", alpha=0.05):
    instance_log_path = Path(instance_log_path)
    if not instance_log_path.exists():
        raise FileNotFoundError(f"Instance log directory not found at {instance_log_path}")
    methods = [
        ("gold", "validate-gold", r"Gold"),
        ("gpt-4-1106-preview", "zsb__gpt-4-1106-preview__bm25_27k_cl100k__seed=0,temperature=0", r"\zsb"),
        ("gpt-4-1106-preview", "zsp__gpt-4-1106-preview__bm25_27k_cl100k__seed=0,temperature=0", r"\zsp"),
        ("gpt-4-1106-preview", "libro_gpt-4-1106-preview__bm25_27k_cl100k__seed={seed},temperature=0.7.jsonl", r"\libro", "libro", [1,2,3,4,5], Path("inference_output/gpt-4-1106-preview__libro__libro_gpt-4-1106-preview__bm25_27k_cl100k__seed={seed},temperature=0.7.jsonl__[1, 2, 3, 4, 5]__gpt-4-1106-preview__test__all__seed=0,temperature=0__test.jsonl")),
        ("gpt-4-1106-preview", "libro_gpt-4-1106-preview__bm25_27k_cl100k__seed={seed},temperature=0.7.jsonl", r"\pak", "p@k", [1,2,3,4,5]),
        ("gpt-4-1106-preview", "acr__gpt-4-1106-preview", r"\acr"),
        ("aider--gpt-4-1106-preview", "aider_gpt-4-1106-preview", r"\aider"),
        ("gpt4__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__gpt-4-1106-preview", r"\swea"),
        ("gpt4__SWE-bench_Lite__default_test_demo4__t-0.00__p-0.95__c-3.00__install-1", "sweap__gpt-4-1106-preview", r"\sweap"),
    ]
    gold_reports = collect_reports("gold", "validate-gold", instance_log_path)
    gold_reports = ftp_reports(gold_reports)

    headers = (
        ["Method", r"{$\bc{A}$ \up{}}", r"{\ftx \up{}}", r"{\ftp \up{}}", r"{\ptp}"]
        if format.startswith("latex") else
        ["Method", "Applicability", "F2X", "F2P", "P2P"]
    )
    rows = []
    for model, run_id, name, *args in methods:
        reports = collect_reports(model, run_id, instance_log_path, *args)
        applied_f = reports_to_array(gold_reports, no_error_reports(reports))
        ftx_f = reports_to_array(gold_reports, ftx_reports(reports))
        ftp_f = reports_to_array(gold_reports, ftp_reports(reports))
        ptp_f = reports_to_array(gold_reports, ptp_reports(reports))
        applied = bs.bootstrap(applied_f, stat_func=bs_stats.mean, alpha=alpha)
        ftx = bs.bootstrap(ftx_f, stat_func=bs_stats.mean, alpha=alpha)
        ftp = bs.bootstrap(ftp_f, stat_func=bs_stats.mean, alpha=alpha)
        ptp = bs.bootstrap(ptp_f, stat_func=bs_stats.mean, alpha=alpha)
        rows.append([name, f"{applied.value:.1f} ({applied.lower_bound:.1f}-{applied.upper_bound:.1f})", f"{ftx.value:.1f} ({ftx.lower_bound:.1f}-{ftx.upper_bound:.1f})", f"{ftp.value:.1f} ({ftp.lower_bound:.1f}-{ftp.upper_bound:.1f})", f"{ptp.value:.1f} ({ptp.lower_bound:.1f}-{ptp.upper_bound:.1f})"])
    print(tabulate(rows, headers=headers, tablefmt=format, floatfmt=".1f"))

if __name__ == "__main__":
    fire.Fire(main)
