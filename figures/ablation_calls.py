"""
Ablation of number of calls until successful resolution
"""

from tabulate import tabulate
import fire
from pathlib import Path

from figures.util import *


def main(instance_log_path: str = "./run_instance_swt_logs", total_instance_count: int = total_cases_lite, format="github"):
    instance_log_path = Path(instance_log_path)
    if not instance_log_path.exists():
        raise FileNotFoundError(f"Instance log directory not found at {instance_log_path}")
    methods = [
        ("gpt4__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__gpt-4-1106-preview", r"\swea", "inference_output/swe-agent__gpt4__swe-bench_lite_demo3_turns.jsonl", r"myblue", "square"),
        ("gpt4__SWE-bench_Lite__default_test_demo4__t-0.00__p-0.95__c-3.00__install-1", "sweap__gpt-4-1106-preview", r"\sweap", "inference_output/swe-agent__gpt4__swe-bench_lite_demo4_turns.jsonl", r"myred", "triangle"),
        ("gpt-4-1106-preview", "acr__gpt-4-1106-preview", r"\acr", "inference_output/acr__gpt4__swe-bench_lite__test_turns.jsonl", r"mygreen", "diamond"),
        ("aider--gpt-4-1106-preview", "aider_gpt-4-1106-preview", r"\aider", "inference_output/aider__swt-bench_lite__test__turns.jsonl", r"myyellow", "circle"),
    ]

    for counter, y_axis in [
        (no_error_count, r"{$\bc{A}$ \up{}}"),
        # (ftx_count, r"{\ftx \up{}}"),
        (ftp_count, r"{\ftp \up{}}"),
        # (ptp_count, r"{\ptp}"),
    ]:
        print(r"""\begin{subfigure}{0.45\textwidth}
    \centering
    \begin{tikzpicture}[scale=0.5]
        \begin{axis}[
            xlabel={Turns},
            ylabel={%s},
            xmin=0, xmax=20,
            ymin=0, ymax=100,
            xtick={0,5,10,15,20},
            ytick={0,50,100},
            legend pos=north west,
            ymajorgrids=true,
            grid style=dashed,
        ]""" % (y_axis,))
        for model, run_id, name, num_turns_file, color, shape, *args in methods:
            with open(num_turns_file) as f:
                num_turns = [json.loads(l) for l in (f)]
            num_turns_per_instance = {x["instance_id"]: x["num_turns"] for x in num_turns}
            reports = collect_reports(model, run_id, instance_log_path, *args)
            res = []
            for i in range(21):
                reports_i = {k: v for k, v in reports.items() if num_turns_per_instance[k] <= i}
                counted = 100*counter(reports_i)/total_instance_count
                res.append((i, counted))
            print(r"""\addplot[
                color=%s,
                mark=%s,
                ]
                coordinates {
                %s
                };
            \addlegendentry{%s}""" % (color, shape, "".join([f"({i},{counted})" for i, counted in res]), name))
        print("""\end{axis}
    \end{tikzpicture}
    \end{subfigure}""")

if __name__ == "__main__":
    fire.Fire(main)