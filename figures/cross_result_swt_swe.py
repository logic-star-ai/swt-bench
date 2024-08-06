import json
import sys

from figures.util import *

swe_bench_results: str = sys.argv[1]  # i.e. "results/experiments-swe-bench/20240402_sweagent_gpt4/results/results.json"

raw_swe_bench_ress = json.load(open(swe_bench_results))
swe_bench_resolved = raw_swe_bench_ress["resolved"]
swe_bench_applied = raw_swe_bench_ress["applied"]

print("Original precision", len(swe_bench_resolved) / len(swe_bench_applied))


swt_bench_reports = collect_reports("sweap__gpt-4-1106-preview_reduced") # TODO
resolved_own_test = ftp_reports(swt_bench_reports)
swe_bench_accept_own = [r for r in swe_bench_applied if r["instance_id"] in resolved_own_test]
swe_bench_resolve_own = [r for r in swe_bench_resolved if r["instance_id"] in resolved_own_test]
print("Own precision", len(swe_bench_resolve_own) / len(swe_bench_accept_own))
print("Own filtered out ratio", len(swe_bench_accept_own) / len(swe_bench_applied))
