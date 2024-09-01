"""
Method vs coverage
main
"""

import fire

from figures.util import *
from tabulate import tabulate


def main(instance_log_path: str = "./run_instance_swt_logs", total_instance_count: int = total_cases_lite, format="github"):
    instance_log_path = Path(instance_log_path)
    if not instance_log_path.exists():
        raise FileNotFoundError(f"Instance log directory not found at {instance_log_path}")
    methods = [
        ("gold", "validate-gold-1", r"Gold"),
        ("gpt-4-1106-preview", "libro_gpt-4-1106-preview__bm25_27k_cl100k__seed={seed},temperature=0.7.jsonl", r"\paf", "p@k", [1,2,3,4,5]),
        ("gpt-4-1106-preview", "zsb__gpt-4-1106-preview__bm25_27k_cl100k__seed=0,temperature=0", r"\zsb"),
        ("gpt-4-1106-preview", "zsp__gpt-4-1106-preview__bm25_27k_cl100k__seed=0,temperature=0", r"\zsp"),
        ("gpt-4-1106-preview", "libro_gpt-4-1106-preview__bm25_27k_cl100k__seed={seed},temperature=0.7.jsonl", r"\libro", "libro", [1,2,3,4,5], Path("inference_output/gpt-4-1106-preview__libro__libro_gpt-4-1106-preview__bm25_27k_cl100k__seed={seed},temperature=0.7.jsonl__(1, 2, 3, 4, 5)__gpt-4-1106-preview__test__test.jsonl")),
        ("gpt-4-1106-preview", "acr__gpt-4-1106-preview", r"\acr"),
        ("aider--gpt-4-1106-preview", "aider_gpt-4-1106-preview", r"\aider"),
        ("gpt4__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__gpt-4-1106-preview", r"\swea"),
        ("gpt4__SWE-bench_Lite__default_test_demo4__t-0.00__p-0.95__c-3.00__install-1", "sweap__gpt-4-1106-preview", r"\sweap"),
    ]
    gold_reports = collect_reports("gold", "validate-gold-1", instance_log_path)
    total_coverage_possible = count_coverage_delta_gold(gold_reports)

    print(r"Method & {$\dc^{\text{all}}$ } & {$\dc^{\ftp}$} & {$\dc^{\neg(\ftp)}$} \\")
    headers = (
        ["Method", r"{$\dc^{\text{all}}$ }", r"{$\dc^{\ftp}$}", r"{$\dc^{\neg(\ftp)}$}"]
        if format.startswith("latex") else
        ["Method", "Coverage", "Resolved Coverage", "Unresolved Coverage"]
    )
    rows = []
    for model, run_id, name, *args in methods:
        reports = collect_reports(model, run_id, instance_log_path, *args)
        reports = no_error_reports(reports)
        resolved_reports, unresolved_reports = filtered_by_resolved(reports)
        total_coverage_delta = 100 * sum_coverage_delta(reports) / total_coverage_possible
        countable_resolved = count_coverage_delta_gold(resolved_reports)
        resolved_coverage_delta = 100 * sum_coverage_delta(resolved_reports) / countable_resolved if countable_resolved > 0 else 0
        unresolved_coverage_delta = 100 * sum_coverage_delta(unresolved_reports) / (total_coverage_possible - countable_resolved) if total_coverage_possible - countable_resolved > 0 else 0
        rows.append([name, total_coverage_delta, resolved_coverage_delta, unresolved_coverage_delta])
    print(tabulate(rows, headers=headers, tablefmt=format, floatfmt=".1f"))

if __name__ == "__main__":
    fire.Fire(main)