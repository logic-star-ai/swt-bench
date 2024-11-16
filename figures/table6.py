import fire
from datasets import load_dataset
from venny4py.venny4py import venny4py

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
        repos.append(example["instance_id"].split("_")[0])
        num_instances_per_repo[example["instance_id"].split("_")[0]] += 1
    repos = list(sorted(set(repos)))
    print("method,swe_total,swt_total,overlap")
    for method, swe_res, swt_res in [
        (
            "ZSP",
            "figures/zsp_swe-lite_bm25_gpt4.json",
            ("gpt-4-1106-preview", "zsp__gpt-4-1106-preview__bm25_27k_cl100k__seed=0,temperature=0"),
        ),
        (
            "SWEA",
            "https://raw.githubusercontent.com/swe-bench/experiments/main/evaluation/lite/20240402_sweagent_gpt4/results/results.json",
            ("gpt4__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__gpt-4-1106-preview"),
        )
    ]:

        if swe_res.startswith("http"):
            raw_swe_bench_ress = requests.get(swe_res).json()
        else:
            raw_swe_bench_ress = json.load(open(swe_res))
        swe_bench_ress = raw_swe_bench_ress["resolved"]
        swe_total = {res for res in swe_bench_ress if res not in _filter_cases()}

        model, run_id = swt_res

        reports = collect_reports(model, run_id, instance_log_path, "single")

        swt_total = set(ftp_reports(reports).keys())
        sets = {
            "SWE-Bench": swe_total,
            "SWT-Bench": swt_total,
        }
        venny4py(
            sets,
            f"overlap_{method}",
            edge_color=None,
            ext="pdf",
            size=10,
            font_size=30,
        )
        print(method, len(swe_total), len(swt_total), len(swt_total & swe_total), sep=",")


if __name__ == '__main__':
    fire.Fire(main)