
from tabulate import tabulate
import fire
from pathlib import Path

from figures.util import *

TOTAL_INSTANCE_MAP = {
    "lite": total_cases_lite,
    "full": total_cases_full,
    "verified": total_cases_verified,
}
GOLD_RUN_MAP = {
    "lite": "validate-lite-gold-1",
    "full": "validate-full-gold",
    "verified": "validate-verified-gold-1",
}

def main(
        path,
        name=None,
        format="github",
        mode: Literal["single", "libro", "p@k"] = "single",
        seeds: Tuple[int] = None,
        libro_decision_file: Path = None,
        dataset: Literal["lite", "full", "verified"] = "lite",
    ):
    """
    Generic script to report results for a single run
    Pass as path parameter the path to the exact model run, e.g. "run_instance_swt_logs/swea__gpt-4-1106-preview/gpt4__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1"
    """
    total_instance_count = TOTAL_INSTANCE_MAP[dataset]
    instance_log_path = Path(path)
    if mode == "single":
        if not instance_log_path.exists():
            raise FileNotFoundError(f"Instance log directory not found at {instance_log_path}")
    else:
        for seed in seeds:
            seed_path = Path(str(instance_log_path).format(seed=seed))
            if not seed_path.exists():
                raise FileNotFoundError(f"Instance log directory not found at {seed_path}")
    if name == None:
        name = instance_log_path.parent.name

    fields = (
        [r"{$\mathcal{W}$}", r"{$\suc$}", r"{\ftx}", r"{\ftp}", r"{\ptp}"]
        if format.startswith("latex") else
        ["Applicability (W)", "Success Rate (S)", "F->X", "F->P", "P->P"]
    )
    rows = [["Method", name]]
    run_id = instance_log_path.parent.name
    model = instance_log_path.name
    # compute success rate and more detailed f2x, ftp etc
    reports = collect_reports(model, run_id, instance_log_path.parent.parent, mode=mode, seeds=seeds, libro_decision_file=libro_decision_file)
    applied = 100*no_error_count(reports)/total_instance_count
    success = 100*ftp_count(reports)/total_instance_count
    ftp = 100*actual_ftp_count(reports)/total_instance_count
    ftx = 100*ftx_count(reports)/total_instance_count
    ptp = 100*ptp_count(reports)/total_instance_count
    rows.extend([key, val] for key, val in zip(fields, [applied, success, ftx, ftp, ptp]))
    # compute coverage delta (if gold run is available)
    gold_run_id = GOLD_RUN_MAP[dataset]
    try:
        gold_reports = collect_reports("gold", gold_run_id, instance_log_path.parent.parent)
    except Exception:
        print("Warning: No gold run found, skipping report of coverage delta")
        gold_reports = None

    if gold_reports:
        fields = (
            [r"{$\dc^{\text{all}}$ }", r"{$\dc^{\suc}$}", r"{$\dc^{\neg\suc}$}"]
            if format.startswith("latex") else
            ["Coverage Delta (Δᵃˡˡ)", "Coverage Delta Resolved (Δᔆ)", "Coverage Delta Unresolved (Δⁿᵒᵗ ᔆ)"]
        )
        total_coverage_possible = count_coverage_delta_gold(gold_reports)
        resolved_reports, unresolved_reports = filtered_by_resolved(reports)
        total_coverage_delta = 100 * sum_coverage_delta(reports) / total_coverage_possible
        countable_resolved = count_coverage_delta_gold(resolved_reports)
        resolved_coverage_delta = 100 * sum_coverage_delta(
            resolved_reports) / countable_resolved if countable_resolved > 0 else 0
        unresolved_coverage_delta = 100 * sum_coverage_delta(unresolved_reports) / (
                    total_coverage_possible - countable_resolved) if total_coverage_possible - countable_resolved > 0 else 0
        rows.extend([key, val] for key, val in zip(fields, [total_coverage_delta, resolved_coverage_delta, unresolved_coverage_delta]))

    # print results
    print(tabulate(rows, tablefmt=format, floatfmt=".1f"))

if __name__ == "__main__":
    fire.Fire(main)
