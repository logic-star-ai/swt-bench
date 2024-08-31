import fire
from datasets import load_dataset
from figures.util import *
from figures.util import _filter_cases

import tiktoken

tokenizer = tiktoken.encoding_for_model("gpt-4")

def instance_issue_lens(dataset, split):
    instance_issue_len_per_id = {}
    for example in load_dataset(dataset)[split]:
        if example["instance_id"] in _filter_cases():
            continue
        issue = example["problem_statement"]
        instance_issue_len_per_id[example["instance_id"]] = len(tokenizer.encode(issue))
    return instance_issue_len_per_id


def main(
        dataset="princeton-nlp/SWE-bench_Lite",
        split="test",
        instance_log_path: str = "./run_instance_swt_logs",
):
    instance_log_path = Path(instance_log_path)

    print("bucket sizes")
    buckets = [100, 200, 500, float("inf")]
    print(",".join(f"<= {bucket}" for bucket in buckets))

    instance_issue_len = instance_issue_lens(dataset, split)
    repo_lens = defaultdict(list)
    for instance_id, issue_len in instance_issue_len.items():
        repo = instance_id.split("_")[0]
        repo_lens[repo].append(issue_len)


    instance_by_len = defaultdict(list)
    global_bucket_sizes = [0 for _ in buckets]
    for instance_id, issue_len in instance_issue_len.items():
        instance_by_len[issue_len].append(instance_id)
        for i, bucket in enumerate(buckets):
            if issue_len <= bucket:
                global_bucket_sizes[i] += 1
                break
    print(",".join(map(str, global_bucket_sizes)))

    print("repo avg len")
    repos = sorted(repo_lens.keys())
    print("," + ",".join(repos))
    print("avg len" + "," + ",".join(str(sum(repo_lens[repo])/len(repo_lens[repo])) for repo in repos))


    print("resolved")
    print(",\leq 100,\leq 200,\leq 500,> 500")
    methods = [
        ("gold", "validate-gold-1", r"Gold"),
        ("gpt-4-1106-preview", "libro_gpt-4-1106-preview__bm25_27k_cl100k__seed={seed},temperature=0.7.jsonl", r"Pass @ 5", "p@k", [1,2,3,4,5]),
        ("gpt-4-1106-preview", "zsb__gpt-4-1106-preview__bm25_27k_cl100k__seed=0,temperature=0", r"ZeroShotBase"),
        ("gpt-4-1106-preview", "zsp__gpt-4-1106-preview__bm25_27k_cl100k__seed=0,temperature=0", r"ZeroShotPlus"),
        ("gpt-4-1106-preview", "libro_gpt-4-1106-preview__bm25_27k_cl100k__seed={seed},temperature=0.7.jsonl", r"LIBRO", "libro", [1,2,3,4,5], Path("inference_output/gpt-4-1106-preview__libro__libro_gpt-4-1106-preview__bm25_27k_cl100k__seed={seed},temperature=0.7.jsonl__(1, 2, 3, 4, 5)__gpt-4-1106-preview__test__test.jsonl")),
        ("gpt-4-1106-preview", "acr__gpt-4-1106-preview", r"AutoCodeRover"),
        ("aider--gpt-4-1106-preview", "aider_gpt-4-1106-preview", r"Aider"),
        ("gpt4__SWE-bench_Lite__default_test_demo3__t-0.00__p-0.95__c-3.00__install-1", "swea__gpt-4-1106-preview", r"SWE-Agent"),
        ("gpt4__SWE-bench_Lite__default_test_demo4__t-0.00__p-0.95__c-3.00__install-1", "sweap__gpt-4-1106-preview", r"SWE-Agent+"),
    ]
    for model, run_id, name, *args in methods:
        reports = collect_reports(model, run_id, instance_log_path, *args)

        local_buckets = [0 for _ in buckets]
        for instance_id, report in reports.items():
            issue_len = instance_issue_len[instance_id]
            for i, bucket in enumerate(buckets):
                if issue_len <= bucket:
                    local_buckets[i] += report["resolved"]
                    break

        print(name, end=",")
        print(",".join(map(str, (100*lb/gp for lb, gp in zip(local_buckets, global_bucket_sizes)))))

    print("applied")
    print(",\leq 100,\leq 200,\leq 500,> 500")

    for model, run_id, name, *args in methods:
        reports = collect_reports(model, run_id, instance_log_path, *args)

        local_buckets_applied = [0 for _ in buckets]
        for instance_id, report in reports.items():
            issue_len = instance_issue_len[instance_id]
            for i, bucket in enumerate(buckets):
                if issue_len <= bucket:
                    local_buckets_applied[i] += no_error_filter(report)
                    break

        print(name, end=",")
        print(",".join(map(str, (100*lb/gp for lb, gp in zip(local_buckets_applied, global_bucket_sizes)))))

if __name__ == "__main__":
    fire.Fire(main)