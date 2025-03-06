import hashlib
from functools import partial
from time import time

import docker
from docker.models.containers import Container
import json
import traceback
import logging
import os

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from tqdm import tqdm
from typing import List, Tuple, Optional

from src.auxillary_src.extract_patches import remove_binary_diffs
from src.constants import (
    APPLY_PATCH_FAIL,
    APPLY_PATCH_PASS
)
from src.docker_utils import (
    remove_image,
    copy_to_container,
    exec_run_with_timeout,
    cleanup_container,
    list_images,
    should_remove,
    checked_exec_run,
)
from src.docker_build import start_container, BuildMode
from src.test_spec import make_test_spec, TestSpec
from src.utils import get_log_dir, get_test_directives, log_git_diff, setup_logging, link_image_build_dir, close_logger
from src.exec_spec import ExecSpec, make_exec_spec, ExecMode
from src.grading import report_results


class EvaluationError(Exception):
    def __init__(self, instance_id, message, logger: logging.Logger):
        super().__init__(message)
        self.instance_id = instance_id
        self.log_file = logger.log_file
        self.logger = logger

    def __str__(self):
        log_msg = traceback.format_exc()
        self.logger.info(log_msg)
        return (
            f"{self.instance_id}: {super().__str__()}\n"
            f"Check ({self.log_file}) for more information."
        )


def extract_model_patch(exec_spec: ExecSpec, raw_model_patch: str, patch_types: List[str], build_mode: BuildMode = "api") -> str:
    log_dir = get_log_dir(exec_spec.run_id, exec_spec.patch_id, exec_spec.instance_id)

    if os.path.exists(log_dir / "extracted_patch.diff"):
        with open(log_dir / "extracted_patch.diff", "r") as f:
            extracted_patch = f.read()
    else:
        logger, _ = setup_logging(log_dir, exec_spec.instance_id)

        container = None
        client = docker.from_env()
        try:
            container = start_container(exec_spec, client, logger, build_mode=build_mode)

            with open(log_dir / "raw_model_patch.txt", "w") as f:
                f.write(raw_model_patch)
            copy_to_container(container, log_dir / "raw_model_patch.txt", Path("/root/raw_model_patch.txt"))

            requirements_file = Path(os.path.join(os.path.dirname(__file__), "auxillary_src", "requirements_extraction.txt"))
            copy_to_container(container, requirements_file, Path("/root/requirements_extraction.txt"))

            extraction_file = Path(os.path.join(os.path.dirname(__file__), "auxillary_src", "extract_patches.py"))
            copy_to_container(container, extraction_file, Path("/root/extract_patches.py"))

            checked_exec_run(container, "pip3 install -r /root/requirements_extraction.txt")
            res = container.exec_run(f"python3 /root/extract_patches.py --patch_type {' '.join(patch_types)} --reference_commit {exec_spec.base_commit}")
            if res.exit_code == 0:
                res = container.exec_run("cat /root/extracted_patch.diff")
                if res.exit_code == 0:
                    extracted_patch = res.output.decode("utf-8")
                    with open(log_dir / "extracted_patch.diff", "w") as f:
                        f.write(extracted_patch)
                else:
                    logger.info(f"Patch extraction failed:\n {res.output.decode()}")
                    extracted_patch = ""
            else:
                logger.info(f"Patch extraction failed:\n {res.output.decode()}")
                extracted_patch = ""
        except Exception as e:
            logger.error(f"Error in extracting patch for {exec_spec.instance_id}: {e}")
            logger.info(traceback.format_exc())
            raise e
        finally:
            # Remove instance container + image, close logger
            cleanup_container(client, container, logger)
    return extracted_patch


def apply_patch_in_container(log_dir: Path, patch_text: str, container: Container, logger: logging.Logger, instance_id: str):
    # Copy model prediction as patch file to container
    diff_number = len([x for x in os.listdir(log_dir) if x.startswith("patch") and x.endswith(".diff")])
    patch_file = f"patch_{diff_number}.diff"
    patch_path = Path(log_dir / patch_file)
    patch_path.write_text(patch_text)
    logger.info(
        f"Intermediate patch for {instance_id} written to {patch_path}, now applying to container..."
    )
    copy_to_container(container, patch_path, Path(f"/tmp/{patch_file}"))

    # Attempt to apply patch to container
    val = container.exec_run(
        f"git apply -v /tmp/{patch_file}",
        workdir="/testbed",
        user="root",
    )
    if val.exit_code != 0:
        logger.info(f"{APPLY_PATCH_FAIL}:\n{val.output.decode('utf-8')}")
        raise EvaluationError(
            instance_id,
            f"{APPLY_PATCH_FAIL}:\n{val.output.decode('utf-8')}",
            logger,
        )
    else:
        logger.info(f"{APPLY_PATCH_PASS}:\n{val.output.decode('utf-8')}")


def eval_in_container(log_dir: str, container: Container, logger: logging.Logger, eval_script: str, timeout: int, instance_id: str, compute_coverage: bool) -> str:
    eval_file = Path(log_dir / "eval.sh")
    eval_file.write_text(eval_script)
    logger.info(
        f"Eval script for {instance_id} written to eval.sh, now applying to container..."
    )
    copy_to_container(container, eval_file, Path("/eval.sh"))
    if compute_coverage:
        copy_to_container(container, Path(os.path.join(os.path.dirname(__file__), "auxillary_src", "trace.py")), Path("/root/trace.py"))

    # Run eval script, write output to logs
    result = exec_run_with_timeout(container, "/bin/bash /eval.sh", timeout=timeout)
    test_output = result.decode("utf-8")
    test_output_path = log_dir / "test_output.txt"
    with open(test_output_path, "w") as f:
        f.write(test_output)
    logger.info(f"Test output for {instance_id} written to {test_output_path}")
    return test_output_path


def eval_in_container_with_diff(log_dir: Path, container: Container, logger: logging.Logger, eval_script: str, timeout: int, instance_id: str, compute_coverage: bool) -> str:
    git_diff_output_before = log_git_diff(logger, container, "Git diff before:")

    test_output_path = eval_in_container(log_dir, container, logger, eval_script, timeout, instance_id, compute_coverage)

    git_diff_output_after = log_git_diff(logger, container, "Git diff after:")

    if git_diff_output_after != git_diff_output_before:
        logger.info(f"Git diff changed after running eval script")
    return test_output_path


def run_instance(
        test_spec: TestSpec,
        pred: dict,
        rm_image: bool,
        force_rebuild: bool,
        compute_coverage: bool,
        run_id: str,
        patch_types: List[str],
        timeout: int = None,
        build_mode: BuildMode = "api",
    ):
    """
    Run a single instance with the given prediction.

    Args:
        test_spec (TestSpec): TestSpec instance
        pred (dict): Prediction w/ model_name_or_path, model_patch, instance_id
        rm_image (bool): Whether to remove the image after running
        force_rebuild (bool): Whether to force rebuild the image
        compute_coverage (bool): Whether to compute coverage
        run_id (str): Run ID
        patch_types (List[str]): Patch types to extract
        timeout (int): Timeout for running tests
    """

    exec_spec = test_spec.exec_spec
    exec_spec.timeout = timeout
    exec_spec.rm_image = rm_image
    exec_spec.force_rebuild = force_rebuild
    exec_spec.run_id = run_id
    exec_spec.compute_coverage = compute_coverage
    instance_id = test_spec.instance_id

    patch_id_base = pred.get("model_name_or_path", "None").replace("/", "__")
    exec_spec.patch_id = patch_id_base

    if len(patch_types) == 1 and patch_types[0] == "vanilla":
        model_patch = remove_binary_diffs(pred["model_patch"])
    else:
        model_patch = extract_model_patch(exec_spec, pred["model_patch"], patch_types, build_mode=build_mode)

    if model_patch:
        caching_log_dir = [False, False, True, True, True, True]
        patch_ids = ["pred_pre__" + patch_id_base, "pred_post__" + patch_id_base, "gold_pre", "gold_post", "base_pre", "base_post"]
        test_patches = [model_patch, model_patch, test_spec.golden_test_patch, test_spec.golden_test_patch, None, None]
        code_patches = [None, test_spec.golden_code_patch, None, test_spec.golden_code_patch, None, test_spec.golden_code_patch]

        output_paths = []
        for cld, test_patch, code_patch, patch_id in zip(caching_log_dir, test_patches, code_patches, patch_ids):
            exec_spec.test_directives = get_test_directives(model_patch if test_patch is None else test_patch, exec_spec.repo)
            exec_spec.patch_list = [] if code_patch is None else [code_patch]
            exec_spec.patch_list += [test_patch]
            exec_spec.patch_id = patch_id
            if cld:
                log_dir = get_log_dir(patch_id, instance_id, test_directive_id(exec_spec.test_directives))
            else:
                log_dir = None
            _, test_output_path = run_eval_exec_spec(exec_spec, model_patch, log_dir, build_mode)
            output_paths.append(test_output_path)


    return instance_id


def run_eval_exec_spec(exec_spec: ExecSpec, model_patch: str, log_dir: Optional[Path]=None, build_mode: BuildMode = "api") -> Tuple[str, Path]:
    client = docker.from_env()
    instance_id = exec_spec.instance_id

    if log_dir is None:
        log_dir = get_log_dir(exec_spec.run_id, exec_spec.patch_id, exec_spec.instance_id)

    logger, _ = setup_logging(log_dir, instance_id)
    logger.warning(f"Starting evaluation at {time()}")

    with open(log_dir / "exec_spec.json", "w") as f:
        json.dump(exec_spec.as_dict(), f)

    with open(log_dir / "model_patch.diff", "w") as f:
        f.write(model_patch)

    if (log_dir / "test_output.txt").exists():
        return instance_id, (log_dir / "test_output.txt")

    link_image_build_dir(log_dir, exec_spec.instance_image_key)

    # Run the instance
    container = None
    try:
        container = start_container(exec_spec, client, logger, build_mode=build_mode)

        test_output_path = eval_in_container_with_diff(log_dir, container, logger, exec_spec.eval_script, exec_spec.timeout, instance_id, exec_spec.compute_coverage)

        return instance_id, test_output_path
    except EvaluationError as e:
        raise EvaluationError(instance_id, str(e), logger) from e
    except Exception as e:
        logger.error(f"Error in evaluating model for {instance_id}: {e}")
        logger.info(traceback.format_exc())
        raise EvaluationError(instance_id, str(e), logger) from e
    finally:
        # Remove instance container + image, close logger
        cleanup_container(client, container, logger)
        if exec_spec.rm_image:
            remove_image(client, exec_spec.instance_image_key, logger)
        logger.warning(f"End of eval at {time()}")
        close_logger(logger)


def run_instances(
        predictions: dict,
        instances: list,
        compute_coverage: bool,
        cache_level: str,
        clean: bool,
        force_rebuild: bool,
        max_workers: int,
        run_id: str,
        patch_types: List[str],
        timeout: int,
        client: docker.DockerClient,
        build_mode: BuildMode,
        exec_mode: ExecMode,
        reproduction_script_name: Optional[str] = None,
    ):
    """
    Run all instances for the given predictions in parallel.

    Args:
        predictions (dict): Predictions dict generated by the model
        instances (list): List of instances
        cache_level (str): Cache level
        clean (bool): Clean images above cache level
        force_rebuild (bool): Force rebuild images
        max_workers (int): Maximum number of workers
        run_id (str): Run ID
        timeout (int): Timeout for running tests
        client (docker.DockerClient): Docker client
        build_mode (BuildMode): Build mode
        exec_mode (ExecMode): Execution mode
        reproduction_script_name (Optional[str]): Name of the reproduction script
    """
    test_specs = list(map(partial(make_test_spec, exec_mode=exec_mode, reproduction_script_name=reproduction_script_name), instances))

    # print number of existing instance images
    instance_image_ids = {x.exec_spec.instance_image_key for x in test_specs}
    existing_images = {
        tag for i in client.images.list(all=True)
        for tag in i.tags if tag in instance_image_ids
    }
    if not force_rebuild and len(existing_images):
        print(f"Found {len(existing_images)} existing instance images. Will reuse them.")

    # run instances in parallel
    print(f"Running {len(instances)} instances...")
    with tqdm(total=len(instances), smoothing=0) as pbar:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create a future for running each instance
            futures = [
                executor.submit(
                    run_instance,
                    test_spec,
                    predictions[test_spec.instance_id],
                    should_remove(
                        test_spec.exec_spec.instance_image_key,
                        cache_level,
                        clean,
                        existing_images,
                    ),
                    force_rebuild,
                    compute_coverage,
                    run_id,
                    patch_types,
                    timeout,
                    build_mode,
                )
                for test_spec in test_specs
            ]
            # Wait for each future to complete
            try:
                for future in as_completed(futures):
                    # Update progress bar
                    pbar.update(1)
                    # check if instance ran successfully
                    e = future.exception()
                    if e is None:
                        continue
                    try:
                        if isinstance(e, EvaluationError):
                            print(f"EvaluationError {e.instance_id}: {e}")
                        elif isinstance(e, Exception):
                            print("ExecutionError")
                            traceback.print_exc()
                        elif isinstance(e, TimeoutError):
                            print(f"TimeoutError: {e}")
                    except Exception as e:
                        print(f"Error trying to format error: {e}")
                        traceback.print_exc()
            except TimeoutError as e:
                print(f"TimeoutError: {e}")
    print("All instances run.")

def find_all_test_output_paths(dir: Path):
    for file in dir.rglob("test_output.txt"):
        yield file

def test_directive_id(test_directives: list[str]):
    return hashlib.sha256("__".join(test_directives).encode()).hexdigest()


def make_run_report(
        predictions: dict,
        dataset: list,
        client: docker.DockerClient,
        run_id: str,
        exec_mode: ExecMode,
    ):
    """
    Make a final evaluation and run report of the instances that have been run.
    Also reports on images and containers that may still running!

    Args:
        predictions (dict): Predictions dict generated by the model
        dataset (list): List of instances
        client (docker.DockerClient): Docker client
        run_id (str): Run ID
    """
    # instantiate sets to store IDs of different outcomes
    completed_ids = set()
    resolved_ids = set()
    error_ids = set()
    unstopped_containers = set()
    unremoved_images = set()
    unresolved_ids = set()
    coverages = []
    coverage_deltas = []


    # iterate through dataset and check if the instance has been run
    for instance in tqdm(dataset):
        instance_id = instance["instance_id"]
        prediction = predictions[instance_id]
        patch_id_base = prediction["model_name_or_path"].replace("/", "__")
        model_patch_file = get_log_dir(
                run_id,
                "pred_pre__" + patch_id_base,
                instance_id,
        ) / "model_patch.diff"
        test_output_file = model_patch_file.parent / "test_output.txt"
        if not model_patch_file.exists() or not test_output_file.exists():
            # The instance was not run successfully
            error_ids.add(instance_id)
            continue

        report_file = get_log_dir(
            run_id,
            patch_id_base,
            instance_id,
        ) / "report.json"
        if report_file.exists():
            # If report file exists, then the instance has been run and reported before
            completed_ids.add(instance_id)
            report = json.loads(report_file.read_text())
        else:
            with model_patch_file.open() as f:
                model_patch = f.read()

            patch_ids = ["pred_pre__" + patch_id_base, "pred_post__" + patch_id_base, "gold_pre", "gold_post",
                         "base_pre", "base_post"]
            model_test_directive_path = test_directive_id(get_test_directives(model_patch, instance["repo"]))
            gold_test_directive_path = test_directive_id(
                get_test_directives(instance["golden_test_patch"], instance["repo"]))
            directive_paths = [gold_test_directive_path, gold_test_directive_path, model_test_directive_path,
                               model_test_directive_path]
            output_paths = (
                    [
                        get_log_dir(run_id, patch_id, instance_id) / "test_output.txt" for patch_id in patch_ids[:2]
                    ] + [
                        get_log_dir(patch_id, instance_id, directive_path) / "test_output.txt" for
                        patch_id, directive_path in zip(patch_ids[2:], directive_paths)
                    ]
            )
            report = report_results(
                patch_id_base,
                run_id,
                instance["golden_code_patch"],
                output_paths,
                instance_id,
                instance["repo"],
                exec_mode,
            )

        if report[instance_id]["resolved"]:
            # Record if the instance was resolved
            resolved_ids.add(instance_id)
        else:
            unresolved_ids.add(instance_id)
        if report[instance_id]["coverage_pred"] is not None:
            coverage_deltas.append(report[instance_id]["coverage_delta_pred"])
            coverages.append(report[instance_id]["coverage_pred"])


    if len(coverage_deltas) > 0:
        coverage_delta = sum(coverage_deltas)/len(coverage_deltas)
        coverage = sum(coverages) / len(coverages)
    else:
        coverage_delta = 0
        coverage = 0

    # get remaining images and containers
    images = list_images(client)
    exec_specs = list(map(make_exec_spec, dataset))
    for spec in exec_specs:
        image_name = spec.instance_image_key
        if image_name in images:
            unremoved_images.add(image_name)
    containers = client.containers.list(all=True)
    for container in containers:
        if run_id in container.name:
            unstopped_containers.add(container.name)

    # print final report
    print(f"Total instances: {len(dataset)}")
    print(f"Instances completed: {len(completed_ids)}")
    print(f"Mean coverage: {coverage}")
    print(f"Mean coverage delta: {coverage_delta}")
    print(f"Instances resolved: {len(resolved_ids)}")
    print(f"Instances unresolved: {len(unresolved_ids)}")
    print(f"Instances with errors: {len(error_ids)}")
    print(f"Instances still running: {len(unstopped_containers)}")
    print(f"Still existing images: {len(unremoved_images)}")

    # write report to file
    report = {
        "total_instances": len(dataset),
        "completed_instances": len(completed_ids),
        "resolved_instances": len(resolved_ids),
        "unresolved_instances": len(unresolved_ids),
        "error_instances": len(error_ids),
        "Mean coverage": coverage,
        "Mean coverage delta": coverage_delta,
        "unstopped_instances": len(unstopped_containers),
        "completed_ids": list(sorted(completed_ids)),
        "resolved_ids": list(sorted(resolved_ids)),
        "unresolved_ids": list(sorted(unresolved_ids)),
        "error_ids": list(sorted(error_ids)),
        "unstopped_containers": list(sorted(unstopped_containers)),
        "unremoved_images": list(sorted(unremoved_images)),
    }
    report_file = Path(os.path.join("evaluation_results",
        list(predictions.values())[0]["model_name_or_path"].replace("/", "__")
        + f".{run_id}"
        + ".json")
    )
    Path("evaluation_results").mkdir(parents=True, exist_ok=True)
    with open(report_file, "w") as f:
        print(json.dumps(report, indent=4), file=f)
    print(f"Report written to {report_file}")