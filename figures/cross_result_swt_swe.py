import json
import sys

import fire
import requests

from figures.util import *

def main(swe_bench_results: str = "https://raw.githubusercontent.com/swe-bench/experiments/main/evaluation/lite/20240402_rag_gpt4/results/results.json", instance_log_path: str = "./run_instance_swt_logs"):
    instance_log_path = Path(instance_log_path)

    raw_swe_bench_ress = requests.get(swe_bench_results).json()
    swe_bench_resolved = raw_swe_bench_ress["resolved"]
    swe_bench_applied = raw_swe_bench_ress["applied"]

    print("Original precision", len(swe_bench_resolved) / len(swe_bench_applied))


    swt_bench_reports = collect_reports("gpt4__SWE-bench_Lite__default_test_demo4__t-0.00__p-0.95__c-3.00__install-1", "sweap__gpt-4-1106-preview_reduced", instance_log_path)
    resolved_own_test = ftp_reports(swt_bench_reports)
    swe_bench_accept_own = [r for r in swe_bench_applied if r in resolved_own_test]
    swe_bench_resolve_own = [r for r in swe_bench_resolved if r in resolved_own_test]
    print("Filtered on F2P precision", len(swe_bench_resolve_own) / len(swe_bench_accept_own))
    print("Filtered on F2P recall", len(swe_bench_resolve_own) / len(swe_bench_resolved))
    print("% Filtered out", 1 - (len(swe_bench_accept_own) / len(swe_bench_applied)))

if __name__ == '__main__':
    fire.Fire(main)