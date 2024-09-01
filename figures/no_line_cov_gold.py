"""
Which instances have 0 line coverage in gold
"""

from tabulate import tabulate
import fire
from pathlib import Path

from figures.util import *

def main(instance_log_path: str = "./run_instance_swt_logs", total_instance_count: int = total_cases_lite, format="github"):
    instance_log_path = Path(instance_log_path)
    if not instance_log_path.exists():
        raise FileNotFoundError(f"Instance log directory not found at {instance_log_path}")
    model, run_id = ("gold", "validate-gold-1")

    reports = collect_reports(model, run_id, instance_log_path)
    num_gold = count_coverage_delta_gold(reports)
    num_total = total_instance_count
    print(f"0 coverage delta: {1-num_gold/num_total}")

if __name__ == "__main__":
    fire.Fire(main)