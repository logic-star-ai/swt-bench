from datasets import load_dataset
import fire

import nltk
nltk.download('punkt_tab')

from nltk.tokenize import word_tokenize

from figures.util import *
from figures.util import _filter_cases
from unidiff import PatchSet

import tabulate

table_rows = {
    "len_issues": r"\# Words",
    "files": r"\# Files",
    "lines": r"\# Lines",
    "base_ftp": r"\# \ftp",
    "base_ftf": r"\# \ftf",
    "base_ptp": r"\# \ptp",
    "base_ptf": r"\# \ptf",
    "tests_total": "\# Total",
    "base_coverage": "Coverage",
    "gold_ftp": r"\# \ftp",
    "gold_ftf": r"\# \ftf",
    "gold_ptp": r"\# \ptp",
    "gold_ptf": r"\# \ptf",
    "gold_added_total": r"\# Added",
    "gold_removed_total": r"\# Removed",
    "gold_edited_files": r"\# Files Edited",
    "gold_edited_lines": r"\# Lines Edited",
}


def main(
    instance_log_path: str = "run_instance_swt_logs",
    dataset: str = "princeton-nlp/SWE-bench",
    split: str = "test",
    path_to_line_counts: str = "counted_lines_files.jsonl",
    format="github",
):
    instance_log_path = Path(instance_log_path)
    model, run_id = ("gold", "validate-full-gold")

    with open(path_to_line_counts) as f:
        line_counts = [json.loads(l) for l in f.readlines()]
    line_counts = {lc["instance_id"]: lc for lc in line_counts}

    reports = collect_reports(model, run_id, instance_log_path)
    dataset = load_dataset(dataset)
    measures = {
        key: []
        for key in table_rows.keys()
    }
    for example in dataset[split]:
        instance_id = example["instance_id"]
        if instance_id in _filter_cases():
            continue
        measures["len_issues"].append(len(word_tokenize(example["problem_statement"])))
        report = reports[instance_id]
        tests_base = report["tests_base"]
        tests_gold = report["tests_gold"]
        all_tests_base = set(sum(tests_base.values(), []))
        all_tests_gold = set(sum(tests_gold.values(), []))
        measures["gold_added_total"].append(len(all_tests_gold - all_tests_base))
        measures["gold_removed_total"].append(len(all_tests_base - all_tests_gold))
        measures["tests_total"].append(sum(len(v) for v in tests_base.values()))
        for key, key2 in [
            ("ftp", "FAIL_TO_PASS"),
            ("ftf", "FAIL_TO_FAIL"),
            ("ptp", "PASS_TO_PASS"),
            ("ptf", "PASS_TO_FAIL"),
        ]:
            measures[f"base_{key}"].append(len(tests_base[key2]))
            exclusively_added = set(tests_gold[key2]) - all_tests_base
            measures[f"gold_{key}"].append(len(exclusively_added))
        if report["coverage_base"] is not None:
            measures["base_coverage"].append(report["coverage_base"])
        patch = load_diff(instance_id, model, run_id, instance_log_path)
        if patch is not None:
            patchset = PatchSet(patch)
            measures["gold_edited_files"].append(len(patchset))
            measures["gold_edited_lines"].append(sum(file.added + file.removed for file in patchset))
        measures["lines"].append(line_counts[instance_id]["num_lines"])
        measures["files"].append(line_counts[instance_id]["num_files"])
    avg = lambda x: sum(x) / len(x) if x else "-"
    max_f = lambda x: max(x) if x else "-"
    headers = ["", "Mean", "Max"]
    rows = []
    for key, label in table_rows.items():
        values = measures[key]
        if key == "base_coverage":
            rows.append([label, f"{avg(values):.1%}", f"{max_f(values):.0%}"])
        if key == "lines":
            rows.append([label, f"{avg(values)/1000:.0f}K", f"{max_f(values)/1000:.0f}K"])
        else:
            rows.append([label, f"{avg(values):.1f}", f"{max_f(values):.0f}"])
    print(tabulate.tabulate(rows, headers=headers, tablefmt=format, floatfmt=".1f"))




if __name__ == "__main__":
    fire.Fire(main)
