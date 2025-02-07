from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from docker_build import BuildMode

import docker
import json
import resource

from argparse import ArgumentParser
from typing import List, Tuple, Optional, Dict, Literal

from src.docker_utils import (
    list_images,
    clean_images,
)

from src.dataset import get_dataset_from_preds, get_gold_predictions
from src.utils import str2bool
from run_evaluation import run_instances, make_run_report

def run(
        dataset_name: str,
        is_swt: bool,
        split: str,
        instance_ids: list,
        predictions_path: str,
        compute_coverage: bool,
        max_workers: int,
        force_rebuild: bool,
        cache_level: str,
        clean: bool,
        open_file_limit: int,
        run_id: str,
        patch_types: List[str],
        timeout: int,
        build_mode: "BuildMode" = "api",
        skip_eval: bool = False,
        force_rerun: bool = True,
    ):
    """
    Run evaluation harness for the given dataset and predictions.
    """
    # set open file limit
    assert len(run_id) > 0, "Run ID must be provided"
    resource.setrlimit(resource.RLIMIT_NOFILE, (open_file_limit, open_file_limit))
    client = docker.from_env()

    # load predictions as map of instance_id to prediction
    if predictions_path == 'gold':
        print("Using gold tests - ignoring predictions_path")
        predicted_tests = get_gold_predictions(dataset_name, split, is_swt)
    else:
        if predictions_path.endswith(".json"):
            with open(predictions_path, "r") as f:
                predicted_tests = json.load(f)
        elif predictions_path.endswith(".jsonl"):
            with open(predictions_path, "r") as f:
                predicted_tests = [json.loads(line) for line in f]
        else:
            raise ValueError("Predictions path must be \"gold\", .json, or .jsonl")
    predicted_tests = {pred["instance_id"]: pred for pred in predicted_tests}

    # get dataset from predictions
    dataset = get_dataset_from_preds(dataset_name, split, instance_ids, predicted_tests, run_id, is_swt=is_swt, exclude_completed=not force_rerun)
    full_dataset = get_dataset_from_preds(dataset_name, split, instance_ids, predicted_tests, run_id, False, is_swt=is_swt)
    existing_images = list_images(client)
    print(f"Running {len(dataset)} {'unevaluated' if not force_rerun else 'selected'} instances...")
    if not dataset:
        print("No instances to run.")
    elif skip_eval:
        print("Skipping evaluation and only generating reports")
    else:
        # build environment images + run instances
        # build_env_images(client, dataset, force_rebuild, max_workers)
        run_instances(predicted_tests, dataset, compute_coverage, cache_level, clean, force_rebuild, max_workers, run_id, patch_types, timeout, client, build_mode)

    # clean images + make final report
    clean_images(client, existing_images, cache_level, clean)
    make_run_report(predicted_tests, full_dataset, client, run_id)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--dataset_name", default="princeton-nlp/SWE-bench_Lite", type=str, help="name of dataset")
    # don't switch golden patches
    parser.add_argument(
        "--is_swt", type=str2bool, default=False, help="Indicate that benchmark is extended with RAG, need to handle patches differently"
    )
    parser.add_argument("--split", type=str, default="test")
    parser.add_argument("--instance_ids", nargs="+", type=str, help="Instance IDs to run (space separated)")
    parser.add_argument("--predictions_path", type=str, help="Path to predictions file - if 'gold', uses gold predictions", required=True)
    parser.add_argument("--max_workers", type=int, default=4, help="Maximum number of workers (should be <= 75%% of CPU cores)")
    parser.add_argument("--open_file_limit", type=int, default=4096, help="Open file limit")
    parser.add_argument("--patch_types", nargs="+", choices=["fuzzy", "custom", "vanilla"], default=["vanilla"], type=str, help="Type of patch to be extracted")
    parser.add_argument(
        "--compute_coverage", type=str2bool, default=True, help="Compute coverage"
    )
    parser.add_argument(
        "--build_mode", choices=["cli", "api"], default="api", help="Run docker build via the REST API or the CLI. Try CLI if facing UID/GID errors."
    )

    parser.add_argument(
        "--timeout", type=int, default=1_800, help="Timeout (in seconds) for running tests for each instance"
        )
    parser.add_argument(
        "--force_rebuild", type=str2bool, default=False, help="Force rebuild of all images"
    )
    parser.add_argument(
        "--cache_level",
        type=str,
        choices=["none", "base", "env", "instance"],
        help="Cache level - remove images above this level",
        default="env",
    )
    # if clean is true then we remove all images that are above the cache level
    # if clean is false, we only remove images above the cache level if they don't already exist
    parser.add_argument(
        "--clean", type=str2bool, default=False, help="Clean images above cache level"
    )
    parser.add_argument("--run_id", type=str, required=True, help="Run ID - identifies the run")
    # Skip running the evaluation and just grade
    parser.add_argument(
        "--skip_eval", type=str2bool, default=False, help="Skip evaluation and only generate reports"
    )
    # Rerun instances that have already been run
    parser.add_argument(
        "--force_rerun", type=str2bool, default=False, help="Force rerun of instances that have already been run"
    )
    args = parser.parse_args()

    run(**vars(args))