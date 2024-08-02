"""
Creates a subset of the SWE-bench with a balanced number of instances before and after a cutoff date.
"""
import random
import datetime

import fire
import tqdm
from datasets import load_dataset, Dataset, DatasetDict

def main(
    dataset: str = "princeton-nlp/SWE-bench",
    output_path: str = None,
    splits: str = "test,dev",
    cutoff: str = "2023-04-30",
    seed: int = 0,
):
    if output_path is None:
        output_path = f"{dataset}-balanced-{cutoff}"
    splits = splits.split(",")
    instances_before_cutoff = []
    instances_after_cutoff = []
    cutoff = datetime.datetime.strptime(cutoff, "%Y-%m-%d")
    loaded_dataset = load_dataset(dataset)

    splits_dict = {}
    for split in splits:
        for instance in tqdm.tqdm(loaded_dataset[split]):
            instance_timestamp = datetime.datetime.strptime(instance["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            if instance_timestamp <= cutoff:
                instances_before_cutoff.append(instance)
            else:
                instances_after_cutoff.append(instance)

        max_amount = min(len(instances_after_cutoff), len(instances_before_cutoff))
        print(f"Split {split}: {max_amount} of {len(instances_before_cutoff)} instances before cutoff, {max_amount} of {len(instances_after_cutoff)} instances after cutoff")
        rnd = random.Random(seed)
        instances_before_cutoff = rnd.sample(instances_before_cutoff, max_amount) if len(instances_before_cutoff) > max_amount else instances_before_cutoff
        instances_after_cutoff = rnd.sample(instances_after_cutoff, max_amount) if len(instances_after_cutoff) > max_amount else instances_after_cutoff
        splits_dict[split] = Dataset.from_list(instances_after_cutoff + instances_before_cutoff)
    ds = DatasetDict(splits_dict)
    ds.save_to_disk(output_path)

if __name__ == '__main__':
    fire.Fire(main)