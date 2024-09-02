import fire
from datasets import load_dataset

from figures.util import *
from figures.util import _filter_cases
import requests


def main(
    dataset="princeton-nlp/SWE-bench_Lite",
    instance_log_path: str = "./run_instance_swt_logs",
):
    instance_log_path = Path(instance_log_path)
    repos = []
    num_instances_per_repo = defaultdict(int)
    for example in load_dataset(dataset)["test"]:
        if example["instance_id"] in _filter_cases():
            continue
        repo = repo_from_instance_id(example["instance_id"])
        repos.append(repo)
        num_instances_per_repo[repo] += 1
    repos = list(sorted(set(repos)))
    print("bench," + ",".join(repos))
    method, swe_res, swt_res = (
        "SWEA",
        "https://raw.githubusercontent.com/swe-bench/experiments/main/evaluation/lite/20240402_sweagent_gpt4/results/results.json",
        ("gpt4__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__gpt-4-1106-preview"),
    )

    raw_swe_bench_ress = requests.get(swe_res).json()
    swe_bench_ress = raw_swe_bench_ress["resolved"]
    swe_bench_ress = [res for res in swe_bench_ress if res not in _filter_cases()]
    swe_bench_ress_by_repo = defaultdict(list)
    for res in swe_bench_ress:
        repo = repo_from_instance_id(res)
        swe_bench_ress_by_repo[repo].append(res)
    print("SWE-Bench", end=",")
    for repo in repos:
        if num_instances_per_repo[repo] == 0:
            continue
        repo_ress = swe_bench_ress_by_repo.get(repo, [])
        good_cases = len(repo_ress)
        print(100 * good_cases / num_instances_per_repo[repo], end=",")
    print()

    print("SWT-Bench", end=",")
    model, run_id = swt_res

    reports = collect_reports(model, run_id, instance_log_path, "single")

    by_repo = defaultdict(dict)
    for res, report in reports.items():
        repo = repo_from_instance_id(res)
        by_repo[repo][res] = report

    for repo in repos:
        if num_instances_per_repo[repo] == 0:
            continue
        repo_ress = by_repo[repo]
        good_cases = ftp_count(repo_ress)
        print(100 * good_cases / num_instances_per_repo[repo], end=",")
    print()


if __name__ == '__main__':
    fire.Fire(main)