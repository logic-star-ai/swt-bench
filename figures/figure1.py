from datasets import load_dataset
import fire
from figures.util import _filter_cases, repo_from_instance_id


def main(
    dataset: str = "princeton-nlp/SWE-bench",
    split: str = "test",
):
    dataset = load_dataset(dataset)

    for example in dataset[split]:
        instance_id = example["instance_id"]
        if instance_id in _filter_cases():
            continue
        print(repo_from_instance_id(instance_id))




if __name__ == "__main__":
    fire.Fire(main)
