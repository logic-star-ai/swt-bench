import json

import fire
import os
import pathlib
import subprocess

from datasets import load_dataset
from tqdm import tqdm


def clone_repo(example, tmp_dir):
    repo_name = example["repo"].split("/")[-1]
    if not os.path.isdir(f"{tmp_dir}/{repo_name}"):
        pathlib.Path(f"{tmp_dir}/{repo_name}").mkdir(parents=True, exist_ok=True)
        subprocess.run(["bash", "-c", f"cd {tmp_dir} && git clone https://github.com/{example['repo']}"],
                       check=True, capture_output=True)
    subprocess.run(["bash", "-c",
                    f"cd {tmp_dir}/{repo_name} && git reset && git stash && git clean -fdx && git checkout {example['base_commit']}"],
                   check=True, capture_output=True)
    return f"{tmp_dir}/{repo_name}"

def count_lines_files(dir):
    """
    Count the number of files with .py ending and lines in each file
    """
    num_files = 0
    num_lines = 0
    for root, dirs, files in os.walk(dir):
        for file in files:
            if file.endswith(".py"):
                num_files += 1
                with open(os.path.join(root, file)) as f:
                    try:
                        num_lines += len(f.readlines())
                    except UnicodeDecodeError:
                        pass
    return num_files, num_lines

def main(dataset_name: str = "princeton-nlp/SWE-bench", tmp_dir: str = "/tmp", out_file: str = "counted_lines_files.jsonl"):
    # load out file and already processed instances
    if os.path.exists(out_file):
        with open(out_file) as f:
            processed_instances = set(json.loads(l.strip())["instance_id"] for l in f.readlines())
    else:
        processed_instances = set()

    dataset = load_dataset(dataset_name)
    with open(out_file, "a") as f:
        for example in tqdm(dataset["test"]):
            if example["instance_id"] in processed_instances:
                continue
            repo_dir = clone_repo(example, tmp_dir)
            num_files, num_lines = count_lines_files(repo_dir)
            print(json.dumps({"num_files": num_files, "num_lines": num_lines, "instance_id": example["instance_id"]}), file=f, flush=True)

if __name__ == '__main__':
    fire.Fire(main)