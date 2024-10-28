"""
Overlap between best methods
"""
import fire

from figures.util import *

from venny4py.venny4py import *
from matplotlib import pyplot as plt

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Computer Modern Roman",
    "font.size": 20,
})



def main(instance_log_path: str = "./run_instance_swt_logs", out_path: str = "figures/overlap_venn"):
    instance_log_path = Path(instance_log_path)
    if not instance_log_path.exists():
        raise FileNotFoundError(f"Instance log directory not found at {instance_log_path}")
    methods = [
        ("gpt-4-1106-preview", "libro_gpt-4-1106-preview__bm25_27k_cl100k__seed={seed},temperature=0.7.jsonl", "LIBRO", "libro", [1,2,3,4,5], Path("inference_output/gpt-4-1106-preview__libro__libro_gpt-4-1106-preview__bm25_27k_cl100k__seed={seed},temperature=0.7.jsonl__(1, 2, 3, 4, 5)__gpt-4-1106-preview__test__test.jsonl")),
        ("gpt-4-1106-preview", "acr__gpt-4-1106-preview", r"AutoCodeRover"),
        ("aider--gpt-4-1106-preview", "aider_gpt-4-1106-preview", r"Aider"),
        ("gpt4__SWE-bench_Lite__default_test_demo4__t-0.00__p-0.95__c-3.00__install-1", "sweap__gpt-4-1106-preview", r"SWE-Agent+"),
    ]
    sets = {}
    for model, run_id, name, *args in methods:
        reports = collect_reports(model, run_id, instance_log_path, *args)
        resolved_reports, _ = filtered_by_resolved(reports)
        sets[name] = set(resolved_reports.keys())
    # note change bbox_to_anchor to bbox_to_anchor=(.5, 1.05)
    venny4py(
        sets,
        out_path,
        edge_color=None,
        ext="pdf",
        size=10,
        font_size=30,
    )
    print("Total solved:", len(set.union(*sets.values())))



if __name__ == "__main__":
    fire.Fire(main)
