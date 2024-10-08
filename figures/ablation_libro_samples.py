"""
Method vs Applicability, FtX, FtP and PtP
main
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
        ("gpt-4-1106-preview", "gpt-4-1106-preview__swt_bench_lite_aug1_bm25_27k_cl100k_selfmade__seed=0,temperature=0.7,n=25__test._{seed}", rf"\libro {i}", "libro", list(range(25))[:i],
         Path("inference_output/gpt-4-1106-preview__libro_25__test.jsonl"))
        for i in range(1, 25)
    ]
    for counter, y_axis, color in [
        (no_error_count, r"{$\bc{A}$ \up{}}", "myred"),
        # (ftx_count, r"{\ftx \up{}}"),
        (ftp_count, r"{\ftp \up{}}", "myblue"),
        # (ptp_count, r"{\ptp}"),
    ]:
        print(r"""\begin{subfigure}{0.45\textwidth}
    \centering
    \begin{tikzpicture}[scale=0.5]
        \begin{axis}[
            xlabel={\# Samples},
            ylabel={%s},
            xmin=1, xmax=5,
            ymin=0, ymax=100,
            xtick={1,2,3,4,5},
            ytick={0,25,50,75,100},
            legend pos=north west,
            ymajorgrids=true,
            grid style=dashed,
        ]""" % (y_axis,))

        coordinates = []
        for i, (model, run_id, name, *args) in enumerate(methods):
            reports = collect_reports(model, run_id, instance_log_path, *args)
            counted = 100*counter(reports)/total_instance_count
            coordinates.append((i+1, counted))
        print(r"""\addplot[
                    color=myblue,
                    mark=triangle,
                    ]
                    coordinates {
                    %s
                    };
                """ % ("".join([f"({i},{counted})" for i, counted in coordinates]),))
        print("""\end{axis}
            \end{tikzpicture}
            \end{subfigure}""")

if __name__ == "__main__":
    fire.Fire(main)