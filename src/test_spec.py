import hashlib
import json
import platform
import re

from dataclasses import dataclass
from typing import Union

from src.constants import (
    SWEbenchInstance,
    MAP_REPO_TO_INSTALL,
    MAP_VERSION_TO_INSTALL,
    MAP_REPO_TO_TEST_FRAMEWORK,
    USE_X86,
)
from src.dockerfiles import (
    get_dockerfile_base,
    get_dockerfile_env,
    get_dockerfile_instance,
)
from src.utils import (
    get_requirements,
    get_environment_yml,
    get_test_directives,
)

from src.exec_spec import ExecSpec, make_exec_spec

DIFF_MODIFIED_FILE_REGEX = r"--- a/(.*)"


@dataclass
class TestSpec:
    """
    A dataclass that represents a test specification for a single instance of SWE-bench.
    """
    instance_id: str
    golden_code_patch: str
    golden_test_patch: str
    exec_spec: ExecSpec


def get_test_specs_from_dataset(dataset: Union[list[SWEbenchInstance], list[TestSpec]]) -> list[TestSpec]:
    """
    Idempotent function that converts a list of SWEbenchInstance objects to a list of TestSpec objects.
    """
    if isinstance(dataset[0], TestSpec):
        return dataset
    return list(map(make_test_spec, dataset))


def get_exec_specs_from_dataset(dataset: Union[list[SWEbenchInstance], list[TestSpec]]) -> list[ExecSpec]:
    """
    Idempotent function that converts a list of SWEbenchInstance objects to a list of TestSpec objects.
    """
    if not isinstance(dataset[0], TestSpec):
        # return dataset
        dataset = list(map(make_test_spec, dataset))
    return [x.exec_spec for x in dataset]


def make_test_spec(instance: SWEbenchInstance) -> TestSpec:
    if isinstance(instance, TestSpec):
        return instance
    instance_id = instance["instance_id"]
    golden_code_patch = instance["golden_code_patch"]
    golden_test_patch = instance["golden_test_patch"]
    exec_spec = make_exec_spec(instance)

    return TestSpec(
        instance_id=instance_id,
        golden_code_patch=golden_code_patch,
        golden_test_patch=golden_test_patch,
        exec_spec=exec_spec
    )
