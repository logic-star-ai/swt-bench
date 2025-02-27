"""
An implementation of a LIBRO like operation

Takes several samples for unittest generation,
looks at their evaluation trace and picks the one that most closely
resembles the issue description (picked by LLM or so)
"""
import difflib
import re
from collections import defaultdict
from typing import List, Optional, Literal
import json
import pathlib

import fire
from unidiff import PatchSet

from datasets import load_from_disk, load_dataset, Dataset, DatasetDict

PROMPT = """
You are an automated expert software engineer working on a project. Below is a user issue in a repository.
{}

Another agent has generated a test case that tries to encapsulate the user issue.
The test suite of the repository was executed before and after adding the test case.
The difference between the execution traces is shown below:
```trace
{}
```

You are an automated expert software engineer working on a project. Above is a user issue in a repository.
Please look at the generated test case and the execution trace of running the test case on the current repository.
Please answer whether the test case accurately tests the issue described by the user.
Please answer with "yes" or "no".
"""

def extract_execution_trace_from_log(log: str) -> List[str]:
    # extract the execution trace from the evaluation output
    log = log.splitlines()
    start_line = 0
    for i, line in enumerate(log[start_line:], start=start_line):
        if i < len(log)-1 and "trace.py --count -C coverage.cover" in log[i + 1]:
            break
    if i >= len(log) - 1:
        return None
    for j, line in enumerate(log[i:], start=i):
        if line.startswith("+ cat coverage.cover"):
            break
    return log[i + 1:j - 1]

def load_log(eval_output_dir: str, run_id, model, pre_post: Literal["pre", "post"]) -> dict:
    run_path = pathlib.Path(eval_output_dir) / run_id / f"pred_{pre_post}__{model}"
    logs = {}
    for dir in run_path.iterdir():
        if not dir.is_dir():
            continue
        log = dir / "test_output.txt"
        if not log.exists():
            continue
        with open(log) as f:
            logs[dir.name] = f.read()
    return logs

def load_patch(eval_output_dir: str, run_id, model) -> dict:
    run_path = pathlib.Path(eval_output_dir) / run_id / f"pred_post__{model}"
    patches = {}
    for dir in run_path.iterdir():
        if not dir.is_dir():
            continue
        patch = dir / "model_patch.diff"
        if not patch.exists():
            continue
        with open(patch) as f:
            patches[dir.name] = f.read()
    return patches

def load_pre_post_logs(eval_output_dir: str, run_id, model) -> dict:
    pre_logs = load_log(eval_output_dir, run_id, model, "pre")
    post_logs = load_log(eval_output_dir, run_id, model, "post")
    patch = load_patch(eval_output_dir, run_id, model)
    return {
        "pre": pre_logs,
        "post": post_logs,
        "patch": patch,
    }

def main(
    eval_output_dir: str = "./run_instance_swt_logs",
    dataset: str = "princeton-nlp/SWE-bench_Lite",
    run_id_pattern: str = "gpt-4o-2024-11-20__SWT-bench_Verified_bm25_27k_zsp__test_{seed}",
    model: str = "gpt-4o-2024-11-20",
    seeds: list[int] = (0,1,2,3,4),
    out_dataset_prefix: str = "./datasets/libro",
    split: str = "test",
):
    run_ids = [run_id_pattern.format(seed=seed) for seed in seeds]

    dataset = load_dataset(dataset)
    logs_by_instance = {}
    new_examples = []
    for seed, run_id in zip(seeds, run_ids):
        logs_by_instance[seed] = load_pre_post_logs(eval_output_dir, run_id, model)
    for example in dataset[split]:
        instance_id = example["instance_id"]
        user_issue = example["problem_statement"]
        for seed in seeds:
            pre_log = logs_by_instance[seed]["pre"].get(instance_id)
            post_log = logs_by_instance[seed]["post"].get(instance_id)
            if pre_log is None or post_log is None:
                continue
            execution_trace_pre = extract_execution_trace_from_log(pre_log)
            execution_trace_post = extract_execution_trace_from_log(post_log)
            patch = logs_by_instance[seed]["patch"].get(instance_id)

            diffstuff = "".join(difflib.unified_diff(execution_trace_pre, execution_trace_post))
            if not diffstuff:
                # if there is no difference in the traces, the unit test is not testing anything
                continue

            new_example = {
                **example,
                "text": PROMPT.format(user_issue, diffstuff),
                "execution_trace_pre": execution_trace_pre,
                "execution_trace_post": execution_trace_post,
                "unittest_patch": patch,
                "instance_id": instance_id + "_seed=" + str(seed),
            }
            new_examples.append(new_example)
    ds_l = Dataset.from_list(new_examples)
    ds = DatasetDict({split: ds_l})
    ds.save_to_disk(out_dataset_prefix + f"__{run_id_pattern}__{seeds}__{model}__{split}")


        


if __name__ == "__main__":
    fire.Fire(main)
